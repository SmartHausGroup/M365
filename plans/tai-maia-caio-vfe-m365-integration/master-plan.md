# Master Plan: TAI, MAIA, CAIO, VFE, and M365 Integration

**Plan ID:** `tai-maia-caio-vfe-m365-integration`
**Type:** Overarching high-level overview (cross-repo)
**Status:** Draft (Pending Approval)
**Date:** 2026-02-06
**Owner:** SmartHaus
**North Star Alignment:** M365 — `Operations/NORTHSTAR.md` (AI Workforce, M365-only orchestration); TAI/MAIA/CAIO/VFE — respective North Star docs.
**Governance:** Per-repo work follows the strictest rules across all repos. Plan-first, identify-document-plan-approve, MA process where mathematical/algorithmic. No implementation without approved per-repo plan and explicit "go."

---

## Objective

Enable **voice-driven M365 execution**: user speaks to TAI → intent is classified by MAIA → CAIO orchestrates and routes to the M365 service → M365 Provisioning API executes the action → TAI speaks back the result. Integration spans five repositories (TAI, MAIA, CAIO, VFE, M365) with one overarching flow and **per-repository detailed plans** (no monolithic cross-repo implementation plan).

---

## Scope (High-Level Only)

- **In scope:** End-to-end flow definition, repo responsibilities, interfaces and contracts, dependency order, success criteria, and references to per-repo detailed plans.
- **Out of scope:** Implementation tasks (those live in each repo’s detailed plan).

---

## End-to-End Flow

```
User (voice)
    → TAI (STT, session, optional chat)
    → MAIA (intent classification: domain, action, params)
    → TAI / CAIO (orchestration request with intent)
    → CAIO (route by intent to M365 service)
    → M365 adapter (CAIO) → M365 Provisioning API (Graph, Teams, SharePoint, etc.)
    → Result back to CAIO → TAI
    → TAI (TTS) → User (speak back)
```

- **VFE:** Required for inference-backed M365 actions (for example drafting Teams message bodies or OneNote note content). VFE remains inference-only and does not execute M365 actions. This step is complete (discovery + `POST /api/v1/inference/m365/generate` in vfe-core; CAIO draft wiring in caio-core).
- **M365** is a **registered service in CAIO**; CAIO routes “M365” intents to the M365 adapter, which calls the M365 Provisioning API.

---

## Repositories and Responsibilities

| Repo   | Responsibility | Detailed plan location |
|--------|----------------|-------------------------|
| **M365** | Expose instruction/command API consumable by CAIO adapter; auth (Graph); existing Provisioning API and orchestrator. | `plans/tai-maia-caio-vfe-m365-integration/m365-repo-plan.md` (this repo) |
| **TAI**  | Voice I/O; send transcript + context to MAIA for intent; call CAIO with structured intent; TTS for response; fallback when MAIA/CAIO unavailable. | TAI repo: `plans/tai-maia-caio-vfe-m365-integration/tai-repo-plan.md` |
| **MAIA** | Intent classification (e.g. domain=M365, action=create_team, params); attention/context; output structured intent for CAIO/TAI. MA process applies where intent logic is mathematical/algorithmic. | MAIA repo: `plans/tai-maia-caio-vfe-m365-integration/maia-repo-plan.md` |
| **CAIO** | Register M365 as a service; M365 adapter (translate orchestrate request → M365 API call); route by intent to M365; return result. | CAIO repo: `plans/tai-maia-caio-vfe-m365-integration/caio-repo-plan.md` |
| **VFE**  | Remain the inference engine; discoverable via CAIO; no M365-specific logic. Required for inference-backed M365 actions (draft message, draft note); optional for structured-only M365 path. | VFE repo: `plans/tai-maia-caio-vfe-m365-integration/vfe-repo-plan.md` |

---

## Interfaces and Contracts (Overview)

- **TAI → MAIA:** Transcript (and optionally history) → structured intent (domain, action, parameters). Contract: request/response schema (defined in TAI and MAIA detailed plans).
- **TAI → CAIO:** Orchestration request containing MAIA intent + context. Contract: CAIO’s existing orchestrate API and intent shape.
- **CAIO → M365:** Adapter issues HTTP calls to M365 Provisioning API (or agreed M365 “instruction” endpoint). Contract: M365 repo defines the API; CAIO adapter implements the client.
- **CAIO ↔ VFE:** Existing inference contract; required for inference-backed M365 drafting flow and optional for structured-only M365 actions.

---

## Dependencies and Sequence

1. **M365:** Define and expose the instruction/command API (or document existing endpoints) that the CAIO M365 adapter will call. No dependency on TAI/MAIA/CAIO for this step.
2. **CAIO:** Implement M365 service registration and M365 adapter (calls M365 API). Depends on M365 API contract.
3. **MAIA:** Extend intent model/schema to include M365 domain and actions (and MA process where applicable). May depend on agreed intent schema with TAI/CAIO.
4. **TAI:** Integrate MAIA for intent and CAIO for orchestration; pass intent to CAIO; handle response and TTS. Depends on MAIA intent contract and CAIO orchestrate API.
5. **VFE:** Required for inference-backed actions (draft generation); discoverable and callable by CAIO via `/api/v1/inference/m365/generate`.

Execution order for implementation: **M365 (API/contract) → CAIO (adapter + registration) → MAIA (intent for M365) → TAI (wire MAIA + CAIO + voice).**

---

## Success Criteria (Overarching)

- User can speak an M365-related instruction to TAI.
- MAIA classifies intent (e.g. M365 action + params).
- CAIO routes the request to the M365 service and returns the result.
- M365 performs the requested action (or returns a clear error).
- TAI speaks back the outcome to the user.
- Each repo’s work is specified and executed only via its own detailed plan and governance (plan-first, MA where applicable, approval before implementation).

---

## Per-Repo Detailed Plans and Prompts

- **Detailed plans** live in each repository and specify only that repo’s work. They follow that repo’s plan format and the strictest governance (MA Phases 1–5 where the work is mathematical/algorithmic; notebook-first per `.cursor/rules/ma-process-mandatory.mdc` and `.cursor/rules/notebook-first-mandatory.mdc`).
- **Codex execution prompts** (two-file: detailed prompt `.md` + kick-off `.txt`) live in each repo under `docs/prompts/` and reference that repo’s detailed plan. No implementation without explicit approval (“go”).

| Repo  | Detailed plan path | Prompts (reference only) |
|-------|--------------------|---------------------------|
| M365  | `plans/tai-maia-caio-vfe-m365-integration/m365-repo-plan.md` | `docs/prompts/codex-m365-voice-integration.md` + `codex-m365-voice-integration-prompt.txt` |
| TAI   | TAI repo: `plans/tai-maia-caio-vfe-m365-integration/tai-repo-plan.md`  | TAI repo: `docs/prompts/codex-tai-voice-m365-integration.md` + `-prompt.txt` |
| MAIA  | MAIA repo: `plans/tai-maia-caio-vfe-m365-integration/maia-repo-plan.md` | MAIA repo: `docs/prompts/codex-maia-m365-intent.md` + `-prompt.txt` |
| CAIO  | CAIO repo: `plans/tai-maia-caio-vfe-m365-integration/caio-repo-plan.md`  | CAIO repo: `docs/prompts/codex-caio-m365-adapter.md` + `-prompt.txt` |
| VFE   | VFE repo: `plans/tai-maia-caio-vfe-m365-integration/vfe-repo-plan.md`   | VFE repo: `docs/prompts/codex-vfe-integration.md` + `-prompt.txt` (optional) |

---

## Integration Status

All five repos (M365, CAIO, MAIA, TAI, VFE) have completed their plans as of 2026-02-06.
CAIO wires to VFE for draft generation when an M365 action requires LLM-drafted content.

---

## References

- M365: `Operations/NORTHSTAR.md`, `Operations/EXECUTION_PLAN.md`
- TAI: `docs/NORTH_STAR_V3.md`, service-registry-architecture plan
- MAIA: `docs/NORTH_STAR.md`, MAIA Intent Calculus
- CAIO: `docs/NORTH_STAR.md`, orchestration and gateway docs
- Rules: `.cursor/rules/plan-first-execution.mdc`, `.cursor/rules/ma-process-mandatory.mdc`, `.cursor/rules/identify-document-plan-approve.mdc`, `.cursor/rules/codex-prompt-creation.mdc` (strictest across repos)
