# HiveMind CLI

Terminal client for [HiveMind](https://github.com/JarbasHiveMind/HiveMind-core).

Connect to a HiveMind node from the command line, type utterances, and watch bus
responses — no audio hardware required. This is the **simplest way to talk to a
hive**: the "hello world" of HiveMind clients.

The curses UI shows a split-pane conversation view. `--no-curses` streams plain
output, which is useful for scripting or SSH sessions with minimal terminal support.

## Where it fits — the satellite spectrum

| Client | Local processing | Remote processing |
|---|---|---|
| **HiveMind-cli** (this) | nothing | STT · TTS · intent · skills |
| [hivemind-mic-satellite](https://github.com/JarbasHiveMind/hivemind-mic-satellite) | microphone · VAD | STT · TTS · intent · skills |
| [HiveMind-voice-relay](https://github.com/JarbasHiveMind/HiveMind-voice-relay) | mic · VAD · wake-word | STT · TTS · intent · skills |
| [HiveMind-voice-sat](https://github.com/JarbasHiveMind/HiveMind-voice-sat) | mic · VAD · wake-word · STT · TTS | intent · skills |

HiveMind-cli requires only a keyboard — no microphone, no speaker, no wake-word
engine. Every other satellite adds layers on top of this foundation.

## Install

```bash
pip install HiveMind-cli
```

## Quickstart

**1. Pair** — issue credentials on the server:

```bash
hivemind-core add-client
# → Access Key: <key>   Password: <password>
```

**2. Connect** — start the terminal:

```bash
hivemind-cli --access-key <key> --password <password> --host wss://192.168.1.10
```

**3. Type** — enter any utterance and press Enter. Responses appear in the
conversation pane (`Mycroft > …`).

## CLI flags

| Flag | Default | Description |
|---|---|---|
| `--access-key` | *(required)* | Client access key issued by `hivemind-core add-client`. |
| `--password` | `None` | Optional client password. |
| `--host` | *(scan)* | HiveMind host URI, including protocol: `ws://…` or `wss://…`. |
| `--port` | `5678` | WebSocket port. |
| `--no-curses` | off | Disable the curses UI; use plain stdout/stdin instead. |
| `--self-signed` | off | Accept self-signed SSL certificates. |

`--host` is technically optional: if omitted, the CLI scans the local network for a
HiveMind node via UDP broadcast and asks before connecting.

The host **must** include the protocol prefix (`ws://` or `wss://`). The CLI exits
with an error and a hint if it is missing.

## Modes

### Curses interface (default)

A split-pane terminal UI with a scrollable message history and an `Input >` prompt.
Responses appear as `Mycroft > <utterance>`. Requires a terminal that supports
curses (most modern terminals do). Falls back automatically to plain mode if curses
is unavailable at import time.

### Plain mode (`--no-curses`)

Line-by-line stdin/stdout. Responses are printed as ` Mycroft: <utterance>`.
Suitable for SSH sessions with limited terminal support, piped input, or headless
scripting.

## Related

| Project | Role |
|---|---|
| [HiveMind-core](https://github.com/JarbasHiveMind/HiveMind-core) | The hive server — runs OVOS and manages satellites. |
| [hivemind-mic-satellite](https://github.com/JarbasHiveMind/hivemind-mic-satellite) | Thinnest audio satellite (mic + VAD local). |
| [HiveMind-voice-relay](https://github.com/JarbasHiveMind/HiveMind-voice-relay) | Voice relay (mic + VAD + wake-word local, STT/TTS remote). |
| [HiveMind-voice-sat](https://github.com/JarbasHiveMind/HiveMind-voice-sat) | Full local stack (STT + TTS on-device). |

## Docs

Full documentation lives in [`docs/`](docs/index.md).

## License

Apache-2.0
