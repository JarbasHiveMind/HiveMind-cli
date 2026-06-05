# HiveMind CLI — Documentation

HiveMind CLI (`hivemind-cli`) is the text-only terminal client for
[HiveMind](https://github.com/JarbasHiveMind/HiveMind-core). It connects to a hive
over WebSocket and lets you type utterances from the command line — no microphone,
no speaker, no wake-word engine required.

It is the **best first step** to understand HiveMind: the minimum surface needed to
speak to a hive is one access key and a network connection. Every concept that
matters (pairing, the wire protocol, session identity, how responses come back) is
visible here before audio hardware is introduced.

## The satellite spectrum

| Client | What runs locally | What runs on the hive |
|---|---|---|
| **HiveMind-cli** ← you are here | nothing | STT · TTS · intent · skills |
| [hivemind-mic-satellite](https://github.com/JarbasHiveMind/hivemind-mic-satellite) | microphone · VAD | STT · TTS · intent · skills |
| [HiveMind-voice-relay](https://github.com/JarbasHiveMind/HiveMind-voice-relay) | mic · VAD · wake-word | STT · TTS · intent · skills |
| [HiveMind-voice-sat](https://github.com/JarbasHiveMind/HiveMind-voice-sat) | mic · VAD · wake-word · STT · TTS | intent · skills |

HiveMind-cli sits at the thin end of this spectrum: it is a pure keyboard interface.
Audio satellites all build on top of the same connection and wire protocol; reading
the CLI code is the clearest path to understanding how the client side of HiveMind
works.

## Documentation pages

| Page | Audience | What it covers |
|---|---|---|
| [Getting started](getting-started.md) | First-time users | Install, pair, connect, send first utterance |
| [Configuration](configuration.md) | All users | Every CLI flag, wss vs ws, ports, self-signed certs, scripting |
| [Architecture](architecture.md) | Developers | Wire protocol, HiveMessage anatomy, session identity, auth |
| [Usage](usage.md) | All users | Practical recipes: skill testing, debugging, SSH, scripting, accessibility |
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
