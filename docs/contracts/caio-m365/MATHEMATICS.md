# CAIO ↔ M365 Instruction API — Mathematics

**MA Phase:** 2 — Mathematical Foundation
**Status:** Draft
**Source:** `docs/CAIO_M365_CONTRACT.md`

---

## Overview

This document formalizes the CAIO–M365 instruction API contract: valid requests, success/error responses, response shapes per action, idempotency, and authentication. All guarantees are expressed as definitions and constraints so they can be tied to invariants and verified.

---

## Notation

- **\(R\)** — Request body (JSON).
- **\(H\)** — Request headers (e.g. `Idempotency-Key`, `X-CAIO-API-Key`).
- **\(S\)** — Response body (JSON).
- **\(\mathcal{O}\)** — Set of all M365 capability names (260; see `registry/capability_registry.yaml`, `M365_MASTER_CALCULUS_ACTIONS.md`). No action outside \(\mathcal{O}\) is executable.
- **\(\mathcal{A}\)** — Set of **implemented** action names (subset of \(\mathcal{O}\); currently 9).
- **\(\mathcal{A}_m\)** — Set of mutating actions (subset of \(\mathcal{A}\)).
- **\(\mathcal{S}_{\texttt{action}}\)** — Set of valid result shapes for a given `action`.
- **\(\mathcal{E}\)** — Set of error codes/messages (e.g. `Unknown action`, `m365_mutations_disabled`).
- **\(\texttt{ok}(S)\)** — Boolean field `ok` in \(S\).
- **\(\texttt{result}(S)\)** — Field `result` in \(S\).
- **\(\texttt{error}(S)\)** — Field `error` in \(S\).
- **\(\texttt{trace_id}(S)\)** — Field `trace_id` in \(S\) (optional but recommended).

---

## Definitions

### Valid request

\(R\) is **valid** iff:

1. \(R\) is a JSON object with key `"action"`.
2. \(\texttt{action}(R) \in \mathcal{O}\) (and if implemented, \(\texttt{action}(R) \in \mathcal{A}\); otherwise the provider may return "action not implemented" or equivalent).
3. If present, `params` is a JSON object; keys and types match the action’s parameter schema (see contract table).
4. Mutating actions \(\texttt{action}(R) \in \mathcal{A}_m\) are allowed only when provider has mutations enabled (environment); otherwise the provider may reject with `m365_mutations_disabled`.

### Success response

\(S\) is a **success response** iff:

- \(\texttt{ok}(S) = \texttt{true}\).
- \(\texttt{result}(S)\) is present and non-null.
- The shape of \(\texttt{result}(S)\) belongs to \(\mathcal{S}_{\texttt{action}}\) for the action that was executed.
- \(\texttt{error}(S)\) may be null or absent.

### Error response

\(S\) is an **error response** iff:

- \(\texttt{ok}(S) = \texttt{false}\).
- \(\texttt{error}(S)\) is present and non-null; \(\texttt{error}(S) \in \mathcal{E}\) (or a string message).
- \(\texttt{result}(S)\) may be null or absent.

### Idempotency

For a given provider instance (or cluster with shared idempotency store): if two requests share the same `Idempotency-Key` header value and the same \((action, params)\), and the first request returned a success response, then the second request returns the **same** response (cached) without re-executing the action.

---

## Equations and Constraints

### Postcondition (success)

\[
\mathtt{ok}(S) = \mathtt{true} \;\Rightarrow\; \mathtt{result}(S) \neq \mathtt{null} \;\wedge\; \mathtt{shape}(\mathtt{result}(S)) \in \mathcal{S}_{\mathtt{action}}.
\tag{Eq. 1}
\]

### Postcondition (error)

\[
\mathtt{ok}(S) = \mathtt{false} \;\Rightarrow\; \mathtt{error}(S) \neq \mathtt{null}.
\tag{Eq. 2}
\]

### Idempotency (same key and body)

\[
\mathtt{sameKey}(H_1, H_2) \wedge \mathtt{sameBody}(R_1, R_2) \wedge \mathtt{success}(S_1) \;\Rightarrow\; S_2 = S_1 \text{ (cached)}.
\tag{Eq. 3}
\]

### Authentication

If provider requires API key (e.g. `CAIO_API_KEY` set):

\[
\mathtt{keyMissingOrInvalid}(H) \;\Rightarrow\; \mathtt{status}(S) = 401.
\tag{Eq. 4}
\]

### Audit (one record per execution)

When audit logging is enabled (`ENABLE_AUDIT_LOGGING` true): for every instruction execution (success, error, or blocked), the system writes **exactly one** audit record. Record schema: unified audit schema v2 with `schema_version`, `timestamp`, `ts`, `correlation_id`, `surface`, `action`, `status`, `user`, `details`, and `result`, where `details` carries the request or execution inputs and `result` carries the outcome, trace, and replay flags.

\[
\mathtt{auditEnabled}() \wedge \text{execution completed} \;\Rightarrow\; \exists \text{ exactly one audit record for this request}.
\tag{Eq. 5}
\]

---

## Master equation

The system-level composition (AuthGate ∘ IdempotencyLookup ∘ Execute ∘ Audit) and the guarantee that every response satisfies Eq. 1–2, and when applicable Eq. 3–5, are formalized in **`M365_MASTER_CALCULUS.md`**.

---

## Result Shapes \(\mathcal{S}_{\texttt{action}}\)

| action | result shape |
|--------|--------------|
| `list_users` | `{ "users": array, "count": number }` |
| `list_teams` | `{ "teams": array, "count": number }` |
| `list_sites` | `{ "sites": array, "count": number }` |
| `get_user` | `{ "user": object }` |
| `reset_user_password` | `{ "user": string, "password_reset": true }` |
| `create_site`, `create_team`, `add_channel`, `provision_service` | Action-specific (site_id, team, etc.) |
| **Batch 1 (spec + notebook):** `list_groups` | `{ "groups": array, "count": number }` |
| `get_group` | `{ "group": object }` |
| `create_group` | `{ "group_id": string, "display_name": string, "mail_nickname": string }` |
| `list_group_members` | `{ "members": array, "count": number }` |
| `add_group_member` | `{ "group_id": string, "member_id": string, "added": true }` |

---

## Assumptions

1. **Single or shared idempotency:** Provider is single-instance or uses a shared store for Idempotency-Key; otherwise Eq. 3 may not hold across instances.
2. **Clock and env:** Provider’s notion of “same request” is based on key + body; no assumption on clock skew beyond normal HTTP.
3. **Schema stability:** \(\mathcal{A}\) and \(\mathcal{S}_{\texttt{action}}\) are versioned with the API; changes require contract and invariant updates.

---

## Invariants

- **INV-CAIO-M365-001:** Response postcondition — every response satisfies Eq. 1 and Eq. 2. See `invariants/INV-CAIO-M365-001.yaml`, LEMMA_L1.md.
- **INV-CAIO-M365-002:** Idempotency — same key + same body + first success ⇒ second response = first (Eq. 3). See INV-CAIO-M365-002.yaml, LEMMA_L2.md.
- **INV-CAIO-M365-003:** Authentication — key required and missing/invalid ⇒ status 401 (Eq. 4). See INV-CAIO-M365-003.yaml, LEMMA_L3.md.
- **INV-M365-AUDIT-001:** Audit — when enabled, every instruction execution produces exactly one audit record (Eq. 5). See INV-M365-AUDIT-001.yaml, LEMMA_L4.md.

---

## Verification

- **Producer:** Script or notebook that calls the instruction API (or mocks it) for a set of actions and checks response shape and postconditions.
- **Artifact:** `configs/generated/caio_m365_contract_verification.json` with at least `response_schema_pass`, `postcondition_pass` (and optionally `idempotency_pass`, `auth_pass`).
