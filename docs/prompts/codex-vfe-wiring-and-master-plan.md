# Codex: Add Full VFE Wiring (CAIO → VFE for Drafting) + Master Plan Update

**Plan reference:** `plan:tai-maia-caio-vfe-m365-integration` (follow-on: inference wiring)
**You are approved to implement.** Execute in order below. Update action logs and execution/status docs in each repo when done.

---

## Part 1 — CAIO (caio-core repo)

**Goal:** When an M365 action requires LLM-drafted text (e.g. Teams message body, OneNote note content), CAIO calls VFE `POST /api/v1/inference/m365/generate`, gets the draft text, merges it into the params sent to the M365 instruction API, then calls M365 as today. VFE contract: `docs/api/VFE_M365_INFERENCE_CONTRACT.md` in vfe-core (or M365 repo pointer to that contract).

### 1.1 VFE M365 client in caio-core

- Add a small client (e.g. `caio/clients/vfe_m365_client.py` or under `caio/gateway/`) that:
  - Reads base URL from `VFE_URL` or `VFE_API_URL` (env).
  - Exposes a method e.g. `generate_draft(action: str, prompt: str, context: dict | None = None) -> str | None`.
  - Calls `POST {base_url}/api/v1/inference/m365/generate` with body:
    - `action`: string (e.g. `teams.send_message.draft`, `onenote.create_note.draft`)
    - `prompt`: string
    - `context`: optional dict
  - Response shape: `{ "ok": bool, "trace_id": str, "result"?: { "text": str, ... }, "error"?: { ... } }`.
  - Returns `result["text"]` when `ok` is true, else `None` (log errors).
  - Timeout and connection errors: return `None`, do not raise into orchestrator (graceful fallback).

### 1.2 Extend M365 adapter to use VFE when action needs draft

- In `caio/gateway/adapters/m365.py`:
  - **Draft-needing actions:** Consider an action as needing a draft when either:
    - The action is one of: `send_teams_message`, `teams_send_message`, `create_onenote_note`, `onenote_create_note`, `send_message`, `create_note` (or equivalent from intent), OR
    - `intent.params` contains `draft_prompt` or `prompt_for_body` or `draft_instruction` (user’s instruction for what to write).
  - **Flow:** Before building the final payload for M365:
    1. If the action needs draft and there is a prompt (from `params.get("draft_prompt")` or `params.get("prompt_for_body")` or `params.get("draft_instruction")` or a fallback from transcript/context), call the VFE M365 client `generate_draft(action=..., prompt=..., context=params)`.
    2. If VFE returns a non-empty string, set it as the body for M365: e.g. `params["body"] = draft_text` or `params["content"] = draft_text` (use the key the M365 instruction API expects; if unknown, use `body` and document).
    3. Remove or keep `draft_prompt` / `prompt_for_body` from params as appropriate (do not send internal keys to M365 if not in contract).
  - If VFE is unavailable or returns `None`, either leave params unchanged (no body) or set a short error message in params/response so the user sees “draft unavailable” rather than a silent failure. Prefer no body over crashing.
- **Config:** Document `VFE_URL` (or `VFE_API_URL`) in caio-core README or env template. If unset, skip VFE draft step (current behavior).

### 1.3 Tests and docs

- Add unit tests for: (a) VFE M365 client (mock HTTP: success returns text, 4xx/5xx or timeout returns None). (b) M365 adapter: when intent has `draft_prompt` and action is draft-capable, adapter calls VFE (mocked) and merges result into params before calling M365 (mocked).
- Update caio-core docs (README or gateway/adapter docs) to state that for inference-backed M365 actions (e.g. drafting Teams/OneNote content), CAIO calls VFE at `POST /api/v1/inference/m365/generate` and documents `VFE_URL` / `VFE_API_URL`.

### 1.4 Governance in caio-core

- Update `CODEX_ACTION_LOG` (or repo action log) with plan reference `plan:tai-maia-caio-vfe-m365-integration` and a short description of VFE wiring.
- Update execution/status plan in caio-core if present (e.g. “VFE drafting wiring complete”).

---

## Part 2 — M365 repo (master plan and log)

**Goal:** Master plan clearly states VFE is required for inference-backed M365 actions and that all five repos (including VFE) are complete. Optional: add a one-line integration-complete note.

### 2.1 Edit master plan

- File: `plans/tai-maia-caio-vfe-m365-integration/master-plan.md`
- Changes:
  1. In the “End-to-End Flow” section, replace or extend the VFE bullet so it says: **VFE is required for inference-backed M365 actions** (e.g. drafting Teams message bodies, OneNote note content). VFE remains inference-only; it does not execute M365 actions. The VFE step is complete (discovery + `POST /api/v1/inference/m365/generate` in vfe-core).
  2. In the Repositories table, for VFE row: change “Optional for voice→M365 flow” to **Required for inference-backed M365 actions** (draft message, draft note). Optional for the minimal “structured-only” M365 path.
  3. Add a short **Integration status** subsection (or at bottom): “All five repos (M365, CAIO, MAIA, TAI, VFE) have completed their plans as of 2026-02-06. CAIO wires to VFE for draft generation when an M365 action requires LLM-drafted content.”

### 2.2 Action log in M365

- In `Operations/ACTION_LOG.md`, add an entry (newest first) with: date/time, brief description that VFE wiring was added in CAIO (call VFE for M365 draft text, then M365 instruction) and master plan updated to state VFE required for inference-backed actions and integration complete. Plan reference: `plan:tai-maia-caio-vfe-m365-integration`.

---

## Validation

- CAIO: New tests pass; existing M365 adapter tests still pass.
- M365: Master plan reads correctly; action log has the new entry.

---

## Success criteria

- [ ] CAIO has a VFE M365 client and M365 adapter calls it when action needs draft and prompt is present.
- [ ] When VFE is unavailable, CAIO falls back without crashing (no draft body or clear message).
- [ ] Master plan states VFE is required for inference-backed M365 actions and notes completion.
- [ ] Both repos’ logs/status updated.
