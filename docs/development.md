# Development & Testing

This page covers building HiveMind CLI from source, the dependency stack, and
running the end-to-end test suite.

---

## Install from source

```bash
git clone https://github.com/JarbasHiveMind/HiveMind-cli
cd HiveMind-cli
pip install -e .
```

`pyproject.toml` is the single source of truth for packaging — there is no
`requirements.txt`, `setup.py`, or `setup.cfg`. Runtime dependencies live in
`[project.dependencies]`; test dependencies live in the `[project.optional-dependencies]`
extras described below.

---

## Dependency stack — HiveMind bus 2.x

HiveMind CLI tracks the **HiveMind bus-client 2.x** stack. The pinned floors are
prereleases, declared as minimum versions so a normal resolver picks them up with
no `--pre` flag:

| Dependency | Floor | Role |
|---|---|---|
| `hivemind-bus-client` | `>=0.9.2a1` | WebSocket client + HiveMessage protocol |
| `hivemind-presence` | `>=0.0.2a2` | UDP local-network node discovery |
| `ovos-bus-client` | `>=2.0.0a3` | OVOS `Message` type and session model (2.x) |
| `ovos-spec-tools` | `>=0.8.0a1` | Shared OVOS spec primitives |

> The `ovos-bus-client>=2.0.0a3` floor is required: stable `1.5.0` bundled an older
> HiveMind protocol that collides with `hivemind-bus-client`. Staying on the 2.x
> line avoids that collision.

---

## Test extras

| Extra | Installs | Use |
|---|---|---|
| `[e2e]` | `pytest`, `hivescope>=0.5.2a1`, `hivemind-core>=4.6.2a1`, the HiveMind policy plugins | Full end-to-end suite (real master + real client) |
| `[test]` | alias for `[e2e]` | Back-compat name |
| `[license]` | `pytest`, `lichecker` | Local license-compliance checking (CI uses the shared `license-check` workflow) |

```bash
pip install -e ".[e2e]"
```

---

## Running the tests

The suite lives in a single `tests/` directory:

```
tests/
└── e2e/
    ├── conftest.py              # cli_harness fixture: real master + real client
    ├── test_cli_client.py       # the terminal client driven over a real bus
    ├── test_acl.py              # ACL policy admission
    └── test_bridge1_conformance.py  # OVOS-BRIDGE-1 / SESSION-1 conformance
```

Run everything:

```bash
pytest tests/
```

Run only the terminal-client tests:

```bash
pytest tests/e2e/test_cli_client.py
```

---

## How the end-to-end tests work

The e2e tests are **real**, not mocked transports:

1. [hivescope](https://github.com/JarbasHiveMind/hivescope) boots a real
   `hivemind-core` master **in-process** over a loopback WebSocket server
   (`ws://127.0.0.1:<random-port>/`).
2. A credential is pre-registered in the master's client database.
3. The real `JarbasCliTerminal` connects to that loopback URL through a real
   `HiveMessageBusClient`, completing the full handshake.
4. The test drives the terminal:
   - **stdin is mocked** — instead of a blocking `input()` call, the test calls the
     same `say()` path the run loop uses per typed line.
   - **stdout is mocked** — `terminal.speak` is replaced with a list `.append`, so
     the test asserts on exactly what the user would have seen rendered, with no TTY.
5. Assertions confirm that a typed utterance reaches the hub's OVOS agent bus, and
   that a `speak` emitted by the hub is rendered back at the terminal.

There is no network beyond the localhost loopback socket, and no `importorskip` /
`skipif` guards — the `[e2e]` extra installs the entire stack, so every test runs
for real on every CI run.

---

## Continuous integration

CI is wired entirely to the shared
[OpenVoiceOS/gh-automations](https://github.com/OpenVoiceOS/gh-automations) reusable
workflows (referenced `@dev`):

| Workflow | What it does |
|---|---|
| `build_tests` | Builds the sdist/wheel and runs `pytest tests/` with the `[e2e]` extra across Python 3.10–3.13 |
| `coverage` | Coverage report for `hivemind_cli_terminal` |
| `lint` | `ruff check` |
| `license_tests` | License compliance (`license-check`) |
| `pip_audit` | CVE scan of the dependency tree |
| `release_preview` | Predicts the next version from PR labels |
| `repo_health` | Checks required files are present |
| `release_workflow` / `publish_stable` | Alpha release on merge to `dev`, stable on merge to `master` |

Versions bump automatically from conventional-commit prefixes — never hand-edit
`hivemind_cli_terminal/version.py`.
