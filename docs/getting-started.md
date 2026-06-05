# Getting Started

This page walks you from zero to a working HiveMind CLI session. You need:

- A machine running [HiveMind-core](https://github.com/JarbasHiveMind/HiveMind-core)
  (the hive server).
- A second machine (or the same machine) where you will run the CLI. No microphone,
  no speaker, no special hardware.

---

## 1. Install

```bash
pip install HiveMind-cli
```

Verify the entry point is available:

```bash
hivemind-cli --help
```

---

## 2. Get an access key

Credentials are issued on the **server** side. SSH into the machine running
HiveMind-core and run:

```bash
hivemind-core add-client
```

The command prints an **Access Key** and a **Password**. Copy both — you will pass
them to the CLI.

---

## 3. Connect

```bash
hivemind-cli \
  --access-key <your-access-key> \
  --password <your-password> \
  --host wss://192.168.1.10
```

Replace `192.168.1.10` with the IP or hostname of your hive node. Use `wss://` for
TLS connections (the default HiveMind-core setup) or `ws://` for plain WebSocket
(local testing without TLS).

The host **must** include the protocol prefix. If you omit it the CLI exits with a
hint:

```
Invalid host, please specify a protocol
ws://192.168.1.10 or wss://192.168.1.10
```

If you omit `--host` entirely, the CLI asks whether to scan the local network for a
HiveMind node via UDP broadcast:

```
You did not specify a host to connect
scan for node and attempt to connect? y/n:
```

---

## 4. Send your first utterance

Once connected you see the curses interface:

```
=== JarbasCursesTerminalV0.5 ===
Input >
```

Type any utterance and press **Enter**:

```
Input > what time is it
```

The hive processes the utterance and speaks the response back. It appears in the
message pane:

```
You > what time is it
Mycroft > It's 3:45 PM.
```

That's it — you are talking to your hive.

---

## 5. Exit

Press **Ctrl-C** to disconnect and exit.

---

## What just happened

1. The CLI connected to the hive over WebSocket using your access key and password.
2. Your typed line was wrapped in a `recognizer_loop:utterance` HiveMessage and
   sent to the hive.
3. The hive ran intent matching and skill execution on the server side.
4. The skill's `speak()` call produced a `speak` message that travelled back over
   the WebSocket.
5. The CLI rendered it in the message pane.

No audio ever left your machine. See [Architecture](architecture.md) for the full
picture of what happens on the wire.
