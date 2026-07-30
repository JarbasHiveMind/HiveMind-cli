# HiveMind CLI

Terminal client for [HiveMind](https://github.com/JarbasHiveMind/HiveMind-core).

Connect to a HiveMind node from the command line. Type an utterance and watch the
response on the bus. No audio hardware is required. Among HiveMind clients, this
one needs the least: only a keyboard.

The curses UI shows a split-pane conversation view. `--no-curses` streams plain
output. Use plain mode for scripting or for SSH sessions with minimal terminal
support.

![HiveMind CLI terminal](./cli_terminal.png)

## Where it fits: the satellite spectrum

| Client | Local processing | Remote processing |
|---|---|---|
| **HiveMind-cli** (this) | nothing | STT, TTS, intent, skills |
| [hivemind-mic-satellite](https://github.com/JarbasHiveMind/hivemind-mic-satellite) | microphone, VAD | STT, TTS, intent, skills |
| [HiveMind-voice-relay](https://github.com/JarbasHiveMind/HiveMind-voice-relay) | mic, VAD, wake-word | STT, TTS, intent, skills |
| [HiveMind-voice-sat](https://github.com/JarbasHiveMind/HiveMind-voice-sat) | mic, VAD, wake-word, STT, TTS | intent, skills |

HiveMind-cli requires only a keyboard. It has no microphone, no speaker, and no
wake-word engine. Every other satellite in the table adds a layer of local
processing on top of this one.

## Install

```bash
pip install HiveMind-cli
```

From source:

```bash
git clone https://github.com/JarbasHiveMind/HiveMind-cli
cd HiveMind-cli
pip install -e .
```

HiveMind CLI tracks the HiveMind bus-client 2.x stack (`ovos-bus-client>=2.0`).
`pyproject.toml` is the single source of truth for dependencies. There is no
`requirements.txt`.

## Quickstart

**1. Pair.** Issue credentials on the server:

```bash
hivemind-core add-client
# → Access Key: <key>   Password: <password>
```

**2. Connect.** Start the terminal:

```bash
hivemind-cli --access-key <key> --password <password> --host wss://192.168.1.10
```

**3. Type.** Enter an utterance and press Enter. The response appears in the
conversation pane (`Mycroft > …`).

## CLI flags

| Flag | Default | Description |
|---|---|---|
| `--access-key` | *(required)* | Client access key issued by `hivemind-core add-client`. |
| `--password` | `None` | Optional client password. |
| `--host` | *(scan)* | HiveMind host URI, including protocol: `ws://…` or `wss://…`. |
| `--port` | `5678` | WebSocket port. |
| `--no-curses` | off | Disable the curses UI. Use plain stdout/stdin instead. |
| `--self-signed` | off | Accept self-signed SSL certificates. |

`--host` is optional. If you omit it, the CLI scans the local network for a
HiveMind node over UDP broadcast and asks before connecting.

The host must include the protocol prefix (`ws://` or `wss://`). The CLI exits
with an error and a hint if the prefix is missing.

## Modes

### Curses interface (default)

A split-pane terminal UI with a scrollable message history and an `Input >`
prompt. Responses appear as `Mycroft > <utterance>`. This mode needs a terminal
that supports curses (most modern terminals do). If curses is unavailable at
import time, the CLI falls back to plain mode.

### Plain mode (`--no-curses`)

Line-by-line stdin/stdout. Responses print as ` Mycroft: <utterance>`. Use this
mode for SSH sessions with limited terminal support, piped input, or headless
scripting.

## Related

| Project | Role |
|---|---|
| [HiveMind-core](https://github.com/JarbasHiveMind/HiveMind-core) | The HiveMind server. It runs OVOS and manages satellites. |
| [hivemind-mic-satellite](https://github.com/JarbasHiveMind/hivemind-mic-satellite) | Thinnest audio satellite. Mic and VAD stay local. |
| [HiveMind-voice-relay](https://github.com/JarbasHiveMind/HiveMind-voice-relay) | Voice relay. Mic, VAD, and wake-word stay local; STT/TTS run remote. |
| [HiveMind-voice-sat](https://github.com/JarbasHiveMind/HiveMind-voice-sat) | Full local stack, including STT and TTS on-device. |

## Docs

Full documentation lives in [`docs/`](docs/index.md). Contributors should read
[`docs/development.md`](docs/development.md) for the dependency stack and how to
run the end-to-end test suite.

## Testing

The end-to-end suite boots a real `hivemind-core` master in-process, using
[hivescope](https://github.com/JarbasHiveMind/hivescope), and drives the real
terminal client over a real bus. Only stdin/stdout is mocked:

```bash
pip install -e ".[e2e]"
pytest tests/
```

See [`docs/development.md`](docs/development.md) for details.

## License

Apache-2.0
