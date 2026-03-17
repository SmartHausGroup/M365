# Running M365 and External Reachability

**Summary:** M365 can run **locally** (Python or Docker). Docker is one way to keep it self-contained. By default it is **not** reachable from the internet until you expose it (e.g. tunnel or deploy).

---

## What we did (port 9000)

The **default port for the M365 Provisioning API and app launcher is 9000** (not 8000). Updated across the repo:

- **Makefile:** `make serve-api` → uvicorn on **9000**
- **m365-server:** default `M365_SERVER_PORT=9000`; `m365-server` and `m365-server --gui` listen on **9000**
- **Docker:** main dashboard/service container listens on **9000**; `docker-compose` maps host **9000** → container **9000**
- **Docs and scripts:** CAIO contract, verification script, deploy-agents, Power BI, Prometheus, and other references now use **http://localhost:9000**

The **ops-adapter** (OPA, policy-checked actions) stays on port **8080** inside its container; `docker-compose` maps it to **18080** on the host. So:

- **Port 9000** = main M365 API (instruction API, health, dashboards when using the main app image).
- **Port 8080 / 18080** = ops-adapter when using Docker compose.

---

## Does M365 run locally in Docker? Is that the approach?

**Yes.** You can run M365 locally in two main ways:

1. **Python (no Docker)**  
   - `make serve-api` → runs **provisioning_api.main:app** on port 9000.  
   - Or `m365-server` / `m365-server --gui` → runs the **ops_adapter** app on port 9000 (with optional OPA).  
   Both are “run on your machine” and listen on `0.0.0.0:9000` (or the port you set), so they’re reachable from other devices on your LAN if your firewall allows.

2. **Docker (self-contained)**  
   - `docker compose up` (or `docker-compose.yml`) runs:
     - **opa** (policy engine)
     - **ops-adapter** (actions, approvals, audit)
     - **m365-dashboard** (Provisioning API / dashboard app on port 9000)
   - So **yes, running M365 locally in Docker is a supported approach** and keeps the stack self-contained (Python, OPA, config in containers and mounted volumes).

Which one you use depends on preference: Python for quick local dev, Docker for a single-command, self-contained stack.

---

## Does it work?

- **Python:** `make serve-api` or `m365-server` should work from repo root with a valid `.env` (and OPA if you use policy). Health: `curl http://localhost:9000/health`.
- **Docker:** `docker compose up -d` (with the correct env file) should start the stack; the dashboard service listens on 9000 inside the container and is mapped to host 9000. Health: `curl http://localhost:9000/health` (for the dashboard/main API).

If something doesn’t work, check: `.env` (or `instances/sandbox.env`), Graph credentials, and that port 9000 is free.

---

## Can it be reached externally?

**By default: no.** The server binds to `0.0.0.0:9000`, so it is reachable from other machines on your **local network** (same Wi‑Fi/LAN), but not from the public internet unless you:

1. **Expose via a tunnel** (e.g. ngrok, Tailscale Funnel, Cloudflare Tunnel) so a public URL forwards to `localhost:9000`.
2. **Deploy** to a cloud host (e.g. VM, container in a cloud) and open firewall/load balancer to port 9000 (or 443 behind a reverse proxy).

So: **local + Docker = works and is self-contained; external reachability = add a tunnel or a cloud deployment.**
