# HiveMind CLI

Terminal client for [HiveMind](https://github.com/JarbasHiveMind/HiveMind-core). Connect to a HiveMind
instance from the command line, type utterances, and watch the bus responses — a lightweight,
keyboard-only way to talk to your hive without audio hardware.

## Install

```bash
pip install HiveMind-cli
```

## Usage

Connect to a hive with the access key issued by `hivemind-core add-client`:

```bash
hivemind-cli --access-key YOUR_ACCESS_KEY --password YOUR_PASSWORD --host wss://192.168.1.10
```

| Option | Description |
| --- | --- |
| `--access-key` | Client access key (required). |
| `--password` | Client password. |
| `--host` | HiveMind host (e.g. `wss://192.168.1.10`). |
| `--port` | HiveMind port (default `5678`). |
| `--no-curses` | Plain stdout instead of the curses interface. |
| `--self-signed` | Accept self-signed SSL certificates. |

The curses interface shows the conversation; type a line and press enter to send a
`recognizer_loop:utterance` to the hive. Use `--no-curses` for scripting or log-style output.

## Related

- [HiveMind-core](https://github.com/JarbasHiveMind/HiveMind-core) — the hive server.
- [HiveMind-voice-sat](https://github.com/JarbasHiveMind/HiveMind-voice-sat) — voice satellite (local STT/TTS).
- [HiveMind-voice-relay](https://github.com/JarbasHiveMind/HiveMind-voice-relay) — voice relay (server-side STT/TTS).

## License

Apache-2.0
