# Plan: ChatGPT Custom GPT Actions — M365 Agent Control

**Plan ID:** `gpt-actions-m365-integration`
**Status:** Approved
**Date:** 2026-02-06
**Owner:** SmartHaus
**Execution plan reference:** `plan:gpt-actions-m365-integration:1`
**North Star alignment:** `Operations/NORTHSTAR.md` — M365 AI Workforce, 39 agents, policy-enforced actions, self-service platform. This plan only documents and exposes the existing ops adapter API for Custom GPT; no new platform or tooling.

**MA process:** This plan is documentation and OpenAPI schema only (no mathematical operations or algorithms). MA Phases 1–5 are not required.

---

## Objective

Enable employees to control M365 agents via a ChatGPT Custom GPT by providing an OpenAPI schema and setup documentation. The Custom GPT uses one Action that calls the existing SmartHaus Ops Adapter (`POST /actions/{agent}/{action}`). Natural language in ChatGPT is interpreted by the GPT, which then invokes the appropriate agent and action with parameters.

---

## Scope (M365 repo only)

- **In scope:** OpenAPI 3.0 schema for the ops adapter “execute action” endpoint; README with steps to add the Action to a Custom GPT, configure server URL and auth, and reference to available agents/actions in `registry/agents.yaml`.
- **Out of scope:** Changes to ops adapter behavior, new endpoints, CAIO/TAI/MAIA/VFE integration, or any code outside `docs/gpt-actions/` and this plan.

---

## Prerequisites

- Ops Adapter running and exposing `POST /actions/{agent}/{action}` (see `src/ops_adapter/main.py`, `registry/agents.yaml`).
- Policy (OPA), approvals, and audit already in place; no changes required for this plan.

---

## Requirements

### Functional

- [x] **R1** OpenAPI 3.0 schema describing one operation: execute M365 agent action (path `/actions/{agent}/{action}`, method POST, body `params` object). Schema suitable for import into ChatGPT Custom GPT → Actions.
- [x] **R2** README in `docs/gpt-actions/` with: (1) how to add the Action to a Custom GPT (paste schema URL or contents), (2) server URL configuration (ops adapter base URL), (3) authentication (API key or Bearer if `JWT_REQUIRED`), (4) pointer to `registry/agents.yaml` for allowed agents and actions.
- [x] **R3** No modification to ops adapter code or registry; schema and docs only.

### Non-functional

- [x] Schema validates as OpenAPI 3.0 (tool or manual check).
- [x] README is sufficient for an admin to configure the GPT Action once the ops adapter URL (and optional auth) is known.

---

## Detailed tasks

1. **Create plan directory and plan document** — `plans/gpt-actions-m365-integration/` with this markdown, README, and optional YAML/JSON.
2. **Add OpenAPI schema** — `docs/gpt-actions/openapi.yaml` with `openapi: 3.0.x`, server (placeholder), path `/actions/{agent}/{action}`, POST, requestBody with `params` (object), response 200 with `status`, `result`, optional `approval_id`.
3. **Add README** — `docs/gpt-actions/README.md` with setup steps, auth notes, and reference to `registry/agents.yaml`.
4. **Update Execution Plan** — Add initiative “ChatGPT Custom GPT — M365 agent control” to `Operations/EXECUTION_PLAN.md` with reference to this plan.
5. **Update Action Log** — Log completion in `Operations/ACTION_LOG.md` with plan reference and North Star alignment.

---

## Validation procedures

- OpenAPI schema: valid 3.0 (e.g. `openapi-spec-validator` or paste into Swagger Editor).
- README: follow steps manually (or review) to confirm an admin can add the Action to a Custom GPT given a base URL and auth.

---

## Success criteria

- [x] Plan exists in `plans/gpt-actions-m365-integration/` and is referenced in `Operations/EXECUTION_PLAN.md`.
- [x] `docs/gpt-actions/openapi.yaml` exists and describes the execute-action operation.
- [x] `docs/gpt-actions/README.md` exists with setup and auth instructions and pointer to registry.
- [x] Action log updated with completion entry.

---

## Risks and mitigation

- **Risk:** Exposing ops adapter URL to GPT users. **Mitigation:** Auth (JWT or API key) and existing OPA/approval policies; README states to use HTTPS and restrict access.
- **Risk:** Schema drift if ops adapter API changes. **Mitigation:** README and plan reference the adapter; future API changes should update the schema.

---

## References

- Ops Adapter: `src/ops_adapter/main.py`, `README.md` (repo root)
- Agent registry: `registry/agents.yaml`
- North Star: `Operations/NORTHSTAR.md`
- Execution Plan: `Operations/EXECUTION_PLAN.md`
