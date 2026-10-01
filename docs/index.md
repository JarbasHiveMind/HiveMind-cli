# HiveMind CLI Documentation

HiveMind CLI (`hivemind-cli`) is the text-only terminal client for
[HiveMind](https://github.com/JarbasHiveMind/HiveMind-core). It connects to a hive
over WebSocket and lets you type utterances from the command line. No microphone,
speaker, or wake-word engine is required.

Start here to understand HiveMind. The minimum surface needed to speak to a hive
is one access key and a network connection. Every concept that matters, including
pairing, the wire protocol, session identity, and how responses come back, is
visible here before audio hardware enters the picture.

## The satellite spectrum

| Client | What runs locally | What runs on the hive |
|---|---|---|
| **HiveMind-cli** ← you are here | nothing | STT · TTS · intent · skills |
| [hivemind-mic-satellite](https://github.com/JarbasHiveMind/hivemind-mic-satellite) | microphone · VAD | STT · TTS · intent · skills |
| [HiveMind-voice-relay](https://github.com/JarbasHiveMind/HiveMind-voice-relay) | mic · VAD · wake-word | STT · TTS · intent · skills |
| [HiveMind-voice-sat](https://github.com/JarbasHiveMind/HiveMind-voice-sat) | mic · VAD · wake-word · STT · TTS | intent · skills |

HiveMind-cli sits at the thin end of this spectrum. It is a pure keyboard
interface. Audio satellites all build on top of the same connection and wire
protocol. Reading the CLI code is the clearest path to understanding how the
client side of HiveMind works.

## Documentation pages

| Page | Audience | What it covers |
|---|---|---|
| [Getting started](getting-started.md) | First-time users | Install, pair, connect, send first utterance |
| [Configuration](configuration.md) | All users | Every CLI flag, wss vs ws, ports, self-signed certs, scripting |
| [Architecture](architecture.md) | Developers | Wire protocol, HiveMessage anatomy, session identity, auth |
| [Usage](usage.md) | All users | Practical recipes: skill testing, debugging, SSH, scripting, accessibility |
| [Development & Testing](development.md) | Developers | Install from source, the bus-client 2.x stack, running the e2e suite, CI |
| [Troubleshooting](troubleshooting.md) | All users | Connection errors, SSL, auth failures, curses rendering issues |

## Quick reference

```bash
pip install HiveMind-cli

# pair on the server
hivemind-core add-client

# connect
hivemind-cli --access-key <key> --password <password> --host wss://192.168.1.10

# headless / scripting
hivemind-cli --access-key <key> --host ws://127.0.0.1 --no-curses
```
