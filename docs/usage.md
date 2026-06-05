# Usage

Practical recipes for common scenarios.

---

## Testing a skill

Connect to the hive and exercise the skill interactively:

```bash
hivemind-cli --access-key <key> --password <pw> --host wss://192.168.1.10
```

Type utterances that target the skill. The hive runs intent matching server-side;
you see the response immediately without needing audio hardware on the client.

This is the fastest feedback loop for skill development: no microphone accuracy
issues, no TTS delays, just raw intent + response.

---

## Debugging the message bus

Use `--no-curses` to get line-by-line output that you can grep or redirect:

```bash
hivemind-cli --access-key <key> --host ws://127.0.0.1 --no-curses 2>&1 | tee session.log
```

Each `speak` response appears on its own line. You can correlate utterances with
responses by reading the log sequentially.

To watch only the responses:

```bash
hivemind-cli --access-key <key> --host ws://127.0.0.1 --no-curses | grep "Mycroft:"
```

---

## Headless / SSH use

The curses UI works on most SSH sessions as long as the remote terminal advertises a
proper `TERM`. If you are on a constrained connection or a dumb terminal, disable it:

```bash
ssh user@server
hivemind-cli --access-key <key> --host ws://127.0.0.1 --no-curses
```

`--no-curses` + `ws://127.0.0.1` is the recommended combination when running the
CLI on the same machine as HiveMind-core (e.g. for local integration testing).

---

## Piping / scripting

Send a fixed utterance and capture the response:

```bash
printf "what is the weather today\n" \
  | hivemind-cli --access-key <key> --host ws://127.0.0.1 --no-curses
```

Send a list of utterances from a file and record all responses:

```bash
hivemind-cli --access-key <key> --host ws://127.0.0.1 --no-curses \
  < test_utterances.txt \
  > responses.txt
```

The process reads until EOF, so the file approach terminates naturally when input
is exhausted.

Automated regression test pattern:

```bash
#!/bin/bash
set -e
hivemind-cli --access-key "$HM_KEY" --host ws://127.0.0.1 --no-curses \
  < expected_inputs.txt \
  | diff - expected_outputs.txt
```

---

## Local-network discovery

If you do not know the host address, omit `--host` and let the CLI scan:

```bash
hivemind-cli --access-key <key> --password <pw>
```

```
You did not specify a host to connect
scan for node and attempt to connect? y/n: y
Found HiveMind node: ws://192.168.1.10:5678
```

The CLI connects to the first node it can authenticate against and starts the
terminal. This uses `hivemind_presence.LocalDiscovery` (UDP broadcast on the local
subnet) and requires the hive node to have presence/discovery enabled.

---

## Accessibility — keyboard-only voice assistant

HiveMind CLI is the most accessible interface to a HiveMind hive:

- No audio hardware required.
- Full keyboard operation.
- Screen-reader compatible in `--no-curses` mode (plain stdout).
- Works over SSH, so it runs on any device that can open a shell.
- Latency is network + intent processing only — no STT/TTS round-trips.

For users who prefer text over audio, or in situations where audio is impractical
(open offices, noisy environments, hearing impairments), the CLI provides a complete
interface to all hive skills.

To use it as a persistent assistant in a terminal multiplexer:

```bash
# inside a tmux or screen session
hivemind-cli --access-key <key> --password <pw> --host wss://192.168.1.10
```

The session persists across disconnects as long as the multiplexer session is alive.
