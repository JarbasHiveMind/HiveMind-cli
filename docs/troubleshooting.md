# Troubleshooting

---

## The CLI exits immediately with "Invalid host, please specify a protocol"

**Cause:** `--host` was given without a protocol prefix.

**Fix:** Always include `ws://` or `wss://`:

```bash
# wrong
hivemind-cli --access-key <key> --host 192.168.1.10

# correct
hivemind-cli --access-key <key> --host wss://192.168.1.10
```

---

## Cannot connect — connection refused or timeout

**Check the port.** HiveMind-core defaults to `5678`. If your server uses a
different port, pass `--port`:

```bash
hivemind-cli --access-key <key> --host ws://192.168.1.10 --port 8181
```

**Check the host is reachable.** Ping the server and verify HiveMind-core is
running:

```bash
ping 192.168.1.10
ssh user@192.168.1.10 -- systemctl status hivemind
```

**Check the firewall.** Port 5678 (or your custom port) must be open for inbound
TCP on the server.

---

## SSL / TLS errors on `wss://`

**Certificate verification failure.** If HiveMind-core uses a self-signed
certificate, add `--self-signed`:

```bash
hivemind-cli --access-key <key> --host wss://192.168.1.10 --self-signed
```

Without this flag, the underlying WebSocket library rejects certificates that are
not signed by a trusted CA.

**Hostname mismatch.** If the certificate is issued for a hostname and you are
connecting by IP, either:
- Connect by hostname: `wss://myhive.local`
- Or use `--self-signed` (which disables hostname verification as well as CA
  verification).

---

## Authentication failure

**Wrong access key or password.** Verify that the values printed by
`hivemind-core add-client` are copied exactly (no trailing spaces, no quotes).

**Client not registered.** The access key must correspond to a client registered on
the hive node you are connecting to. Keys are not portable across nodes.

**Re-issue credentials:**

```bash
hivemind-core add-client
```

Then reconnect with the new key and password.

---

## No response from the hive

**The hive is connected but not answering.** This usually means:

- The utterance was not matched by any skill. Try a basic built-in utterance such as
  `what time is it`.
- The skill handling the utterance crashed on the server side. Check HiveMind-core
  logs on the server.
- The `speak` message is not being routed back. Confirm that the hive node's bridge
  is configured to relay `speak` messages to clients.

---

## Curses rendering issues over SSH

**Garbled display or `curses` errors.** This is usually a `TERM` environment
variable mismatch.

```bash
TERM=xterm-256color hivemind-cli --access-key <key> --host ws://127.0.0.1
```

**Fallback:** Use `--no-curses` for a plain stdin/stdout interface that works in any
terminal:

```bash
hivemind-cli --access-key <key> --host ws://127.0.0.1 --no-curses
```

**curses not available.** If `curses` is not importable (some minimal Python
installs), the library prints a warning at import time:

```
WARNING: curses interface not available
```

In this case `JarbasCursesTerminal` is aliased to `JarbasCliTerminal` automatically.
The `--no-curses` flag is redundant but harmless.

---

## Local-network scan finds no nodes

**Cause:** The hive node does not have presence/discovery enabled, or UDP broadcast
is blocked on the network.

**Fix:** Specify `--host` explicitly instead of relying on discovery:

```bash
hivemind-cli --access-key <key> --host ws://192.168.1.10
```

---

## "Scan aborted and host not specified, exiting" (exit code 2)

You answered `n` (or anything not starting with `y`) when asked whether to scan.
Either re-run with `--host`, or run again and answer `y` to the scan prompt.
