# ChatGPT Custom GPT — M365 Agent Control

This directory provides the **OpenAPI schema and setup guide** for using a **ChatGPT Custom GPT** as the control surface for SmartHaus M365 agents. Users talk to the GPT in natural language; the GPT interprets intent and calls the ops adapter to execute the appropriate agent action.

**Plan reference:** `plan:gpt-actions-m365-integration:1` — see `plans/gpt-actions-m365-integration/gpt-actions-m365-integration.md`.

---

## What you get

- **One Custom GPT Action** that calls your deployed **SmartHaus Ops Adapter** at `POST /actions/{agent}/{action}` with a JSON body `{ "params": { ... } }`.
- Policy (OPA), approvals, and audit are unchanged; the GPT only invokes the existing API.

---

## Files

| File | Purpose |
|------|--------|
| `openapi.yaml` | OpenAPI 3.0 schema for the execute-action operation. Import this (or its URL) into your Custom GPT → Configure → Actions. |
| `README.md` | This setup guide. |

---

## Setup (Custom GPT)

1. **Create or edit a Custom GPT** (ChatGPT Plus / Team / Enterprise).
2. **Configure → Actions → Create new action**.
3. **Import schema:**
   - **Option A:** Paste the contents of `openapi.yaml` into the schema editor.
   - **Option B:** If the schema is hosted at a URL (e.g. your docs site), paste that URL.
   Update the **server URL** in the schema (or in the GPT UI if it overrides) to your **ops adapter base URL** (e.g. `https://ops-adapter.yourcompany.com`), with **no trailing slash**.
4. **Authentication (if required):**
   - If your ops adapter has `JWT_REQUIRED=1`, use **Bearer** auth in the GPT and supply a valid JWT (e.g. from Azure AD).
   - If you use API key auth, configure it in the GPT Action auth settings and ensure the ops adapter accepts it (custom middleware or reverse proxy).
   - If the adapter is open (e.g. internal only, behind VPN), you can leave auth off; the README in the repo root describes `JWT_REQUIRED` and env vars.
5. **Instructions (GPT instructions):** Add guidance so the GPT knows which agents and actions exist and when to call them. Point it to the list of allowed agents and actions (see below).

---

## Available agents and actions

The **source of truth** for allowed agents and their actions is:

- **`registry/agents.yaml`** (in this repo)

Each agent has an `allowed_actions` list. Examples:

- **m365-administrator:** `users.read`, `users.create`, `users.update`, `users.disable`, `licenses.assign`, …
- **project-manager:** `create-project`, `list-projects`, `update-project-status`, `archive-project`
- **teams-manager:** `create-workspace`, `add-workspace-members`, `create-channels`, `get-team-status`
- **outreach-coordinator:** `email.send_individual`, …
- **hr-generalist:** `employee.onboard`, …

The GPT must send a valid `agent` and `action` from this registry; otherwise the adapter returns 400. Parameter names and shapes per action are defined in the ops adapter code (e.g. `src/ops_adapter/actions.py`) and in the registry.

---

## Response behavior

- **`status: success`** — The action ran; `result` contains the response payload.
- **`status: pending_approval`** — The action requires approval; `approval_id` is returned. Approvers can use the ops adapter’s approval endpoints (e.g. `POST /approvals/{id}/approve` or `/deny`) or the configured Teams webhook.

---

## Security and operations

- Use **HTTPS** for the ops adapter base URL.
- Restrict access (e.g. VPN, private net, or auth) so only intended users (or the GPT’s identity) can call the adapter.
- If `JWT_REQUIRED=1`, the GPT must send a valid Bearer token; see repo root README and `src/ops_adapter/main.py` for JWT configuration.
- All invocations are subject to OPA policy and audit logging; no change to that behavior is introduced by the GPT.

---

## References

- Ops Adapter: repo root `README.md`, `src/ops_adapter/main.py`
- Agent registry: `registry/agents.yaml`
- Plan: `plans/gpt-actions-m365-integration/gpt-actions-m365-integration.md`
