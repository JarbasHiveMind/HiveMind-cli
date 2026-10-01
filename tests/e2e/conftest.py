# pytest_plugins must live in the root conftest.py (non-top-level not supported).
#
# Fixtures here boot a *real* hivemind-core master in-process via hivescope's
# loopback WebSocket transport and connect the *real* HiveMind-cli terminal
# client to it over a real HiveMessageBusClient handshake. Only the terminal's
# stdin/stdout I/O is mocked — there is no interactive TTY and no network beyond
# the localhost loopback socket.

import time
from dataclasses import dataclass, field
from typing import List

import pytest

from hivemind_bus_client.client import HiveMessageBusClient
from hivescope.topology import TopologyBuilder

from hivemind_cli_terminal import JarbasCliTerminal

# Credentials the loopback master pre-registers and the real client authenticates
# with. The CLI grants itself the bus message types a terminal needs: it injects
# utterances and receives speak.
CLI_ACCESS_KEY = "hivemind_cli_e2e_key_000000000000000000"
CLI_PASSWORD = "hivemind_cli_e2e_password"
CLI_ALLOWED_TYPES = ["recognizer_loop:utterance", "speak"]


@dataclass
class CLIHarness:
    """A real CLI terminal wired to a real loopback master.

    ``spoken`` collects every utterance the master sends down to the client and
    the terminal renders via ``speak()`` — i.e. the mocked stdout side. ``feed``
    drives the mocked stdin side: it is exactly what the terminal's ``run()``
    loop would call when a user types a line and presses Enter.
    """

    builder: TopologyBuilder
    master: object
    terminal: JarbasCliTerminal
    bus: HiveMessageBusClient
    spoken: List[str] = field(default_factory=list)

    @property
    def peer(self) -> str:
        peers = self.master.connected_peers()
        assert peers, "no client connected to master"
        return peers[0]

    def feed(self, utterance: str) -> None:
        """Simulate the user typing *utterance* at the prompt and pressing Enter.

        This is the exact code path ``JarbasCliTerminal.run()`` takes per line,
        with the blocking ``input()`` call stood in for by the test.
        """
        self.terminal.say(utterance)

    def wait_for_speak(self, timeout: float = 5.0) -> List[str]:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and not self.spoken:
            time.sleep(0.02)
        return self.spoken


@pytest.fixture
def cli_harness():
    """Boot a loopback master, connect the real CLI terminal, mock terminal I/O.

    Yields a :class:`CLIHarness`. Tears the whole stack down afterwards.
    """
    builder = TopologyBuilder()
    master = builder.add_master("M0", use_loopback=True)
    master.register_satellite(
        key=CLI_ACCESS_KEY,
        password=CLI_PASSWORD,
        allowed_types=CLI_ALLOWED_TYPES,
    )
    builder.start_all()

    bus = None
    terminal = None
    try:
        url = master.network_protocol.url  # ws://127.0.0.1:<port>/
        host, port = url.rstrip("/").rsplit(":", 1)

        bus = HiveMessageBusClient(
            CLI_ACCESS_KEY,
            host=host,
            port=int(port),
            password=CLI_PASSWORD,
            useragent=JarbasCliTerminal.platform,
        )
        bus.connect(site_id="e2e-cli")

        deadline = time.monotonic() + 10.0
        while time.monotonic() < deadline and not bus.connected_event.is_set():
            time.sleep(0.05)
        assert bus.connected_event.is_set(), "real CLI client failed to connect to master"

        # Build the real terminal around the connected bus (bus= path skips the
        # second connect). Mock stdout: terminal.speak() normally print()s; here
        # we capture so tests can assert what the user would have seen.
        terminal = JarbasCliTerminal(bus=bus)
        harness = CLIHarness(builder=builder, master=master, terminal=terminal, bus=bus)
        terminal.speak = harness.spoken.append

        # give the master a moment to finish registering the peer
        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline and not master.connected_peers():
            time.sleep(0.02)

        yield harness
    finally:
        if bus is not None:
            try:
                bus.close()
            except Exception:
                pass
        builder.stop_all()
