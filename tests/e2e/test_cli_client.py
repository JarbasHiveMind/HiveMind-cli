"""End-to-end tests for the HiveMind-cli terminal client.

These tests boot a *real* hivemind-core master in-process via hivescope's
loopback WebSocket transport and drive the *real* ``JarbasCliTerminal`` over a
*real* ``HiveMessageBusClient``. The only thing mocked is the terminal's
stdin/stdout I/O:

* stdin — instead of a blocking ``input()`` call, the test calls
  ``harness.feed(text)``, which is the exact code path the terminal's run loop
  takes for each typed line.
* stdout — ``terminal.speak`` is replaced with a list ``.append`` so the test
  can assert what the user would have seen rendered, with no real TTY.

There is no network beyond the localhost loopback socket and no ``importorskip``
/ ``skipif`` guard — the ``[e2e]`` extra installs the full stack
(hivescope, hivemind-core, the policy plugins), so every test runs for real.
"""

import time

from ovos_bus_client.message import Message
from ovos_bus_client.session import Session


# ─────────────────────────────────────────────────────────────────────────────
# Connection / handshake
# ─────────────────────────────────────────────────────────────────────────────

def test_cli_connects_to_master(cli_harness):
    """The real CLI client completes the HiveMind handshake against a real master.

    A connected peer must appear in the master's peer table.
    """
    assert cli_harness.bus.connected_event.is_set()
    assert cli_harness.master.connected_peers(), "CLI peer not registered at master"
    assert cli_harness.peer  # resolves the single connected peer


# ─────────────────────────────────────────────────────────────────────────────
# Inbound — typed utterance reaches the hub's agent bus
# ─────────────────────────────────────────────────────────────────────────────

def test_typed_utterance_reaches_hub(cli_harness):
    """An utterance typed at the CLI reaches the master's OVOS agent bus.

    This is the core promise of the terminal client: keyboard in → hive bus.
    """
    seen = []
    cli_harness.master.agent_protocol.bus.on("recognizer_loop:utterance", seen.append)

    cli_harness.feed("what is the weather")

    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline and not seen:
        time.sleep(0.02)

    assert seen, "typed utterance never reached the agent bus"
    assert seen[0].data["utterances"] == ["what is the weather"]


def test_utterance_recorded_as_bus_message(cli_harness):
    """The master records the injected utterance as a BUS HiveMessage."""
    cli_harness.feed("hello hive")

    rec = cli_harness.master.recorder.wait_for(
        "recognizer_loop:utterance", direction="bus_inject", timeout=5.0
    )
    assert rec is not None, "utterance not recorded at master"


def test_multiple_utterances_arrive_in_order(cli_harness):
    """Several typed lines reach the hub in send order (FIFO)."""
    seen = []
    cli_harness.master.agent_protocol.bus.on("recognizer_loop:utterance", seen.append)

    sent = ["one", "two", "three"]
    for u in sent:
        cli_harness.feed(u)
        time.sleep(0.05)

    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline and len(seen) < len(sent):
        time.sleep(0.02)

    got = [m.data["utterances"][0] for m in seen]
    assert got == sent, f"expected {sent}, got {got}"


def test_utterance_carries_client_lang(cli_harness):
    """The terminal stamps its configured lang onto outbound utterances."""
    seen = []
    cli_harness.master.agent_protocol.bus.on("recognizer_loop:utterance", seen.append)

    cli_harness.terminal.lang = "pt-pt"
    cli_harness.feed("olá")

    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline and not seen:
        time.sleep(0.02)

    assert seen, "utterance never reached the agent bus"
    assert seen[0].data.get("lang") == "pt-pt"


# ─────────────────────────────────────────────────────────────────────────────
# Outbound — a speak from the hub is rendered by the terminal
# ─────────────────────────────────────────────────────────────────────────────

def test_speak_from_hub_rendered_by_terminal(cli_harness):
    """A ``speak`` emitted by the hub reaches the CLI and is rendered to stdout.

    ``terminal.speak`` is the mocked stdout sink; asserting on it is asserting on
    what the user would have seen in the conversation pane.
    """
    cli_harness.master.emit_on_bus(Message(
        "speak",
        {"utterance": "the weather is sunny"},
        {"destination": cli_harness.peer},
    ))

    spoken = cli_harness.wait_for_speak(timeout=5.0)
    assert "the weather is sunny" in spoken


def test_full_round_trip(cli_harness):
    """Type an utterance, the hub answers with a speak, the terminal renders it.

    Exercises both directions over the real bus in one flow.
    """
    seen = []
    cli_harness.master.agent_protocol.bus.on("recognizer_loop:utterance", seen.append)

    cli_harness.feed("tell me a joke")

    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline and not seen:
        time.sleep(0.02)
    assert seen, "utterance never reached the hub"

    # hub responds (simulating a skill answering)
    cli_harness.master.emit_on_bus(Message(
        "speak",
        {"utterance": "why did the chicken cross the road"},
        {"destination": cli_harness.peer},
    ))

    spoken = cli_harness.wait_for_speak(timeout=5.0)
    assert "why did the chicken cross the road" in spoken


def test_multiple_speaks_rendered(cli_harness):
    """Each speak from the hub produces one rendered line at the terminal."""
    lines = ["first", "second", "third"]
    for text in lines:
        cli_harness.master.emit_on_bus(Message(
            "speak",
            {"utterance": text},
            {"destination": cli_harness.peer},
        ))
        time.sleep(0.05)

    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline and len(cli_harness.spoken) < len(lines):
        time.sleep(0.02)

    assert cli_harness.spoken == lines, f"expected {lines}, got {cli_harness.spoken}"


# ─────────────────────────────────────────────────────────────────────────────
# Session fidelity — the terminal's session round-trips through the hub
# ─────────────────────────────────────────────────────────────────────────────

def test_session_lang_preserved_inbound(cli_harness):
    """A session lang attached to the typed utterance survives to the agent bus."""
    seen = []
    cli_harness.master.agent_protocol.bus.on("recognizer_loop:utterance", seen.append)

    sess = Session(lang="fr-fr")
    cli_harness.terminal.bus.emit(Message(
        "recognizer_loop:utterance",
        {"utterances": ["bonjour"], "lang": "fr-fr"},
        {"destination": "hive", "session": sess.serialize()},
    ))

    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline and not seen:
        time.sleep(0.02)

    assert seen, "utterance never reached the hub"
    ctx_session = seen[0].context.get("session") or {}
    # the lang round-trips (the session layer normalizes the BCP-47 region case)
    assert (ctx_session.get("lang") or "").lower() == "fr-fr"
