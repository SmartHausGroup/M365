# CAIO ↔ M365 Instruction API — Intent & Description

**MA Phase:** 1 — Intent & Description  
**Contract:** CAIO (consumer) ↔ M365 Provisioning API (provider)  
**Single endpoint:** POST `/api/m365/instruction`

---

## Problem Statement

TAI (voice) → CAIO (orchestrator) → M365 (instruction API). CAIO must call M365 in a single, well-defined way so that:

- Actions (list users, list teams, create site, reset password, etc.) are unambiguous.
- Responses are predictable (success vs error shape; result shape per action).
- Mutations are gated by configuration and optional idempotency.
- Authentication is explicit when required.

Without a formal contract, provider and consumer can drift; guarantees cannot be verified or enforced.

---

## Context

- **Current state:** M365 exposes POST `/api/m365/instruction` with a set of actions; CAIO (or other callers) use it for TAI-driven M365 operations.
- **What needs to change:** Contract is documented in `docs/CAIO_M365_CONTRACT.md`. It must be formalized (mathematics, invariants, lemmas) and verified so that compliance is mathematically guaranteed.
- **Stakeholders:** CAIO (consumer), M365 (provider), TAI/voice flow (end user), operators (dashboard, status, agents endpoints).

---

## Success Criteria

1. **Formal spec:** Every request/response guarantee is written in MATHEMATICS.md (notation, definitions, postconditions, idempotency, auth).
2. **Invariants:** YAML invariants define machine-checkable guarantees; acceptance checks reference a verification artifact.
3. **Lemmas:** Each guarantee has a lemma (claim, derivation, verification reference).
4. **Verification:** A script or notebook produces `caio_m365_contract_verification.json` with at least:
   - Response schema and postcondition checks pass for sampled actions.
   - Idempotency and auth checks pass when applicable.
5. **CI:** Verification runs in CI; failure blocks deployment or merge when contract compliance is required.
6. **Traceability:** Implementation (M365 router, CAIO adapter) and docs reference the contract invariants and lemmas.

---

## Out of Scope

- Ops-adapter direct calls from CAIO for this flow (contract is instruction API only).
- Graph API or Microsoft API guarantees (only the M365 instruction API surface is contracted).
- Non-deterministic or best-effort behaviors that are explicitly documented as such.
