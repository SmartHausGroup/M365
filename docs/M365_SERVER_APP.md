# SMARTHAUS M365 Server — Application

The M365 ops adapter runs as a **formal application** you can launch like a commercial product. No Makefile or dev workflow required.

For the canonical production configuration contract, see `docs/commercialization/m365-canonical-config-contract.md`. The `.env` paths described here are launcher/bootstrap conveniences, not the authoritative production tenant model.

**Requirements:** Python **3.14** or newer.

---

## Install (once)

From the M365 repo root:

```bash
python3.14 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

Or with a system/Homebrew Python 3.14+:

```bash
pip install -e .
```

This installs the `m365-server` command.

---

## Run the server

**From the M365 repo root** (so `registry/` and optional `.env` are found):

```bash
m365-server
```

- Listens on **http://0.0.0.0:9000** (all interfaces).
- Port: set `M365_SERVER_PORT` or use `m365-server --port 9000`.
- Host: set `M365_SERVER_HOST` or use `m365-server --host 127.0.0.1`.

**With a window (status + Quit button):**

```bash
m365-server --gui
```

Shows “SMARTHAUS M365 Server” and the URL; use Quit to stop.

**Alternative (without installing the script):**

```bash
python -m m365_server
python -m m365_server --gui --port 9000
```

---

## Config and data

- **App root:** Current working directory when you run `m365-server`, or set `M365_APP_ROOT` to a directory that contains:
  - `registry/agents.yaml`
  - optional `.env` (Graph, OPA, etc.)
  - `logs/` is created automatically.
- **.env:** Put a `.env` in the app root, or in `~/.smarthaus/m365/.env`. Same variables as the repo (e.g. `GRAPH_STUB_MODE`, `AZURE_*`, `OPA_URL`, `LOG_DIR`).

These `.env` locations are local launcher inputs. They should not be treated as the canonical production contract for tenant identity, auth mode, governance settings, or org mappings.

---

## OPA (policy engine)

The server uses OPA if `OPA_URL` is set (e.g. `http://localhost:8181`). If OPA is not running, set `OPA_FAIL_OPEN=true` in `.env` so the server still runs and skips policy checks. For full policy enforcement, run OPA separately (Docker or system install) and point `OPA_URL` at it.

---

## Summary

| Action        | Command / note                          |
|---------------|------------------------------------------|
| Install       | `pip install -e .` (Python 3.14+)       |
| Run headless | `m365-server` (from repo root)          |
| Run with GUI | `m365-server --gui`                     |
| Custom port  | `m365-server --port 9000` or env        |
| No Makefile  | Everything via `m365-server` or `python -m m365_server` |
