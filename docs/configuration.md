# Configuration

## CLI flags

All options are passed directly to `hivemind-cli`.

### `--access-key` *(required)*

The client access key issued by `hivemind-core add-client`. The CLI passes it
verbatim to `HiveMessageBusClient` as the identity credential. There is no
default. The CLI refuses to start without it.

### `--password`

Optional password associated with the access key. Default: `None`. Omit if the
client was created without a password.

### `--host`

WebSocket URI of the hive node, **including the protocol**:

```
ws://192.168.1.10        # plain WebSocket
wss://192.168.1.10       # WebSocket over TLS
ws://127.0.0.1           # loopback (local testing)
```

The CLI validates the prefix at startup and exits with code `1` if it is missing.

If `--host` is omitted entirely, the CLI prompts for a local-network scan using
`hivemind_presence.LocalDiscovery` (UDP broadcast). Answering `y` starts the scan.
The CLI prints each discovered node and attempts a connection.

### `--port`

WebSocket port number. Default: `5678`. Override when HiveMind-core is configured to
listen on a non-standard port.

```bash
hivemind-cli --access-key <key> --host ws://127.0.0.1 --port 8181
```

### `--no-curses`

Disables the curses split-pane interface. The CLI falls back to simple
stdin/stdout:

- Responses are printed as ` Mycroft: <utterance>`.
- Input prompt is `ask mycroft:` followed by a blocking `input()` call.

Use this flag when:

- The terminal does not support curses (limited SSH environments, serial consoles).
- You want to pipe utterances from a file or another process.
- You are capturing output in a script.

```bash
echo "what time is it" | hivemind-cli --access-key <key> --host ws://127.0.0.1 --no-curses
```

Note: if `curses` is not importable (not installed), `JarbasCursesTerminal` is
silently aliased to `JarbasCliTerminal`, so `--no-curses` is redundant in that
environment.

### `--self-signed`

Accept self-signed TLS certificates on `wss://` connections. Disabled by default
(certificates are verified). Use this on private/homelab deployments where you
generated your own certificate:

```bash
hivemind-cli --access-key <key> --host wss://192.168.1.10 --self-signed
```

---

## wss vs ws

| Scheme | When to use |
|---|---|
| `wss://` | Production, any deployment where traffic leaves the local machine. Certificate verification is on by default. Add `--self-signed` for home CAs. |
| `ws://` | Local development only (`ws://127.0.0.1`). Never send credentials over unencrypted WebSocket on a shared network. |

HiveMind-core listens on port `5678` for both schemes by default. The client
chooses the scheme.

---

## Scripting with `--no-curses`

The plain mode reads one line at a time from stdin and writes responses to stdout,
making it composable with standard Unix tools.

Send a single utterance non-interactively:

```bash
printf "set a timer for 5 minutes\n" \
  | hivemind-cli --access-key <key> --host ws://127.0.0.1 --no-curses
```

Batch a list of utterances from a file:

```bash
hivemind-cli --access-key <key> --host ws://127.0.0.1 --no-curses < utterances.txt
```

The process exits only when stdin is closed (EOF), so pipe accordingly.

---
[← Getting started](getting-started.md) · [Home](index.md) · [Architecture →](architecture.md)
