# Codex Detailed Prompt: M365 Enterprise Commercialization Readiness

**Plan reference:** `plan:m365-enterprise-commercialization-readiness:R1`  
**Detailed plan:** `plans/m365-enterprise-commercialization-readiness/m365-enterprise-commercialization-readiness.md`  
**Approval status:** Planning artifact created. Do not implement the phases until explicit approval is given for execution.

---

## Executive summary

Bring the M365 repo to an enterprise-commercial ready v1 posture as a **standalone deterministic module** without overstating scope. The priority is not raw breadth. The priority is a narrow, provable, supportable, governable product boundary.

---

## Current state

- The repo has a credible M365 instruction and module architecture.
- The licensed module path is already documented in `docs/TAI_LICENSED_MODULE_MODEL.md`.
- The MA-backed M365 surface is real but narrow relative to the full capability universe.
- Production configuration is split between a stronger tenant config model and direct `.env` loading paths.
- Some verification surfaces can still pass in mock mode.
- Enterprise audit, packaging, onboarding, and collateral are not yet unified into one buyer-ready path.

---

## Target state

- One explicit M365 v1 supported-action surface.
- One canonical production config and identity model.
- Explicit enterprise governance, audit, and release-gate requirements.
- Live-tenant evidence for the enterprise-critical behaviors.
- One coherent install, onboarding, runbook, and pilot package.
- North Star synchronized if commercialization scope changes the product definition or success criteria.

---

## Required execution order

Execute phases strictly in order. Do not skip ahead.

1. `P0` Commercial Boundary Lock
2. `P1` Canonical Config and Identity Model
3. `P2` Governance and Audit Hardening
4. `P3` Live Tenant Evidence and Release Gates
5. `P4` Packaging, Install, and Operator Onboarding
6. `P5` Enterprise Collateral and Pilot Acceptance

---

## Phase guidance

### P0

- Lock the v1 supported-action matrix.
- Write explicit non-goals.
- Define target buyer, operator, and deployment model.
- Decide whether `Operations/NORTHSTAR.md` requires synchronization.

### P1

- Make tenant configuration the canonical production contract.
- Demote `.env` to local development and secret-injection support where appropriate.
- Define certificate, delegated, and app-only expectations.
- Eliminate ambiguous config loading rules.

### P2

- Define enterprise audit requirements and missing runtime surfaces.
- Close fail-open ambiguities that are unacceptable for enterprise claims.
- Align permission tiers, approval boundaries, and administrative traceability.

### P3

- Define live-tenant evidence requirements.
- Separate mock validation from release acceptance.
- Produce deterministic release gates for enterprise-critical behaviors.

### P4

- Define the canonical install and bootstrap path.
- Produce the operator onboarding and support runbook.
- Keep standalone M365 packaging compatible with the TAI-hosted module story.

### P5

- Produce the customer-facing product, security, operations, and pilot artifacts.
- Make sure sales, delivery, and engineering all use the same supported-action boundary.

---

## Execution rules

- Do not expand product claims beyond the currently proven v1 surface unless the plan explicitly approves a scope change.
- If any phase materially changes product definition, target operator, supported scope, or success metrics, update `Operations/NORTHSTAR.md` and log the rationale.
- Keep implementation claims tied to validated evidence, not roadmap intent.
- No tenant-impacting validation without explicit approval for the relevant phase.

---

## Validation expectations

- Keep `Operations/EXECUTION_PLAN.md` synchronized with current phase status.
- Keep `Operations/ACTION_LOG.md` updated for every planning or implementation action.
- Ensure every deliverable maps cleanly back to `plans/m365-enterprise-commercialization-readiness/m365-enterprise-commercialization-readiness.md`.

---

## References

- `plans/m365-enterprise-commercialization-readiness/m365-enterprise-commercialization-readiness.md`
- `Operations/NORTHSTAR.md`
- `Operations/EXECUTION_PLAN.md`
- `docs/M365_MA_INDEX.md`
- `docs/contracts/README.md`
- `docs/TAI_LICENSED_MODULE_MODEL.md`
