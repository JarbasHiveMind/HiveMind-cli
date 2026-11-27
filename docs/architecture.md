# Architecture

This page is for developers who want to understand the HiveMind client protocol
by reading the simplest implementation. HiveMind CLI is that implementation. It
has no audio pipeline and no wake-word engine, only the raw connection and
message exchange.

---

## Component map

```
┌─────────────────────────────────┐
│          hivemind-cli           │
│                                 │
│  JarbasCliTerminal              │
│  (or JarbasCursesTerminal)      │
│         │                       │
│         │ HiveMessageBusClient  │
│         │  (hivemind_bus_client)│
└─────────┼───────────────────────┘
          │  WebSocket (ws:// or wss://)
          │
┌─────────┼───────────────────────┐
│         │   HiveMind-core       │
│    HiveMind node                │
│         │                       │
│    OVOS MessageBus bridge       │
│         │                       │
│    Skills / Intent engine       │
└─────────────────────────────────┘
```

---

## Connection

`JarbasCliTerminal.__init__` calls `HiveMessageBusClient(access_key, host, port,
password, self_signed)` from `hivemind_bus_client`. The client library handles the
WebSocket handshake, access-key authentication, and optional TLS certificate
validation. `bus.connect()` blocks until the handshake completes.

If a pre-connected `bus` object is passed in (used by the local-network scan path),
the constructor skips this step and reuses the existing connection.

```python
self.bus = HiveMessageBusClient(access_key, host=host, port=port,
                                password=password, self_signed=self_signed)
self.bus.connect()
```

---

## Sending an utterance

`JarbasCliTerminal.say(utterance)` wraps the text in an OVOS `Message` and emits
it on the bus:

```python
self.bus.emit(Message(
    "recognizer_loop:utterance",
    {"utterances": [utterance], "lang": self.lang},
    {"destination": "hive"}
))
```

Key points:

- **Message type** is `recognizer_loop:utterance`, the same message type the OVOS
  voice pipeline produces after STT. The hive receives this and processes it the
  same way it processes a spoken utterance. No HiveMind-specific message type is
  needed.
- **`lang`** defaults to `"en-us"`. No CLI flag overrides it. The
  `JarbasCliTerminal.__init__` signature accepts a `lang` parameter for
  programmatic use.
- **`destination: hive`** is a context marker only. Nothing in the client branches
  on it: `HiveMessageBusClient.emit` sends every BUS message upstream.

This is the minimal HiveMind client action: construct a `recognizer_loop:utterance`
Message and emit it. Every voice satellite does the same
thing, with audio-derived text instead of keyboard-derived text.

---

## Receiving a response

After connecting, the constructor registers one handler:

```python
self.bus.on_mycroft("speak", self.handle_speak)
```

`on_mycroft` listens for OVOS bus messages of type `speak` that originate from the
hive. When a skill calls `self.speak(text)` on the server side, the hive emits a
`speak` message that travels back over the WebSocket to the client. The handler
extracts `message.data["utterance"]` and renders it.

In plain mode (`JarbasCliTerminal`):

```python
def speak(self, utterance):
    print(" Mycroft:", utterance)
```

In curses mode (`JarbasCursesTerminal`):

```python
def speak(self, utterance):
    self.msg_box.addstr(f"Mycroft > {utterance} \n")
    self._refresh()
```

---

## The curses UI

`JarbasCursesTerminal.run()` calls `curses.wrapper(self._run_curses_gui)`, which
sets up three windows:

| Window | Position | Role |
|---|---|---|
| `header_box` | top row | Displays the platform identifier string. |
| `msg_box` | rows 1 … height-4 | Scrollable conversation history (`scrollok=True`). |
| `input_box` | bottom 3 rows | `Input > ` prompt, using `getstr()` for one line at a time. |

`curses.echo()` is set so typed characters appear on screen. After each `getstr()`
call, the input is decoded from bytes to UTF-8, echoed into `msg_box` as
`You > <utterance>`, and passed to `say()`.

Incoming `speak` messages are handled in a separate thread (the `HiveMessageBusClient`
event loop) and update `msg_box` directly. `_refresh()` is called after every write.

---

## Platform identifier

Both terminal classes carry a `platform` class attribute:

```python
JarbasCliTerminal.platform    = "JarbasCliTerminalV0.5"
JarbasCursesTerminal.platform = "JarbasCursesTerminalV0.5"
```

This string is passed as `useragent` during the local-scan connection path, which
lets the hive node log the connecting client type.

---

## Why this matters for building your own client

The core of a HiveMind client is five lines:

1. Instantiate `HiveMessageBusClient` with credentials.
2. Call `bus.connect()`.
3. Register `bus.on_mycroft("speak", handler)` for responses.
4. Emit `Message("recognizer_loop:utterance", {"utterances": [text], "lang": lang}, {"destination": "hive"})`.
5. Loop.

Audio satellites add STT before step 4 and TTS after step 3. Everything else is
the same. Reading this codebase first makes those satellites easier to follow.

---
[← Configuration](configuration.md) · [Home](index.md) · [Usage →](usage.md)
