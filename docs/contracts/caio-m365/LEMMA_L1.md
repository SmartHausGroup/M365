# Lemma L1 — CAIO-M365 Instruction API Response Postcondition {#lemma-l1}

**Invariant:** [`invariants/INV-CAIO-M365-001.yaml`](../../invariants/INV-CAIO-M365-001.yaml)

**Status:** Draft

**Backed by:** `docs/contracts/caio-m365/MATHEMATICS.md` — Eq. 1 (success), Eq. 2 (error).

---

## Assumptions

- Provider (M365 instruction API) implements the contract described in MATHEMATICS.md.
- Verification script or notebook runs against a live or mocked endpoint with the declared action set and result shapes.

---

## Constants & Provenance

- Postconditions: Eq. 1 and Eq. 2 from MATHEMATICS.md.
- Verification artifact: `configs/generated/caio_m365_contract_verification.json` (response_schema_pass, postcondition_pass).

---

## Who Relies on It

- **CAIO:** Expects every response to have either (ok, result) or (¬ok, error) in a known shape.
- **M365:** Implementation must satisfy these postconditions for all returned responses.
- **TAI/voice flow:** Relies on CAIO getting predictable responses from M365.

---

## Supporting Verification

Producer: `scripts/ci/verify_caio_m365_contract.py` (or equivalent notebook).  
Artifact: `configs/generated/caio_m365_contract_verification.json`.

---

## Claim

If the provider returns a response \(S\) for a valid request \(R\), then:

1. \(\texttt{ok}(S) = \texttt{true} \Rightarrow \texttt{result}(S) \neq \texttt{null}\) and the shape of \(\texttt{result}(S)\) is in \(\mathcal{S}_{\texttt{action}}\).
2. \(\texttt{ok}(S) = \texttt{false} \Rightarrow \texttt{error}(S) \neq \texttt{null}\).

---

## Derivation

1. By contract design (CAIO_M365_CONTRACT.md and MATHEMATICS.md), the provider guarantees a single response shape: `{ ok, result?, error?, trace_id? }`.
2. Success is defined as `ok === true` with a non-null `result` whose shape depends on `action`.
3. Error is defined as `ok === false` with a non-null `error` string.
4. The verification script (or notebook) issues requests for a subset of actions and asserts that each response satisfies (1) and (2). The artifact records pass/fail.

---

## Verification

- **What it checks:** For each of a set of actions, request is sent; response is validated for presence of `ok`; if `ok` then `result` is present and matches the expected shape for that action; if `¬ok` then `error` is present.
- **Assertions:** `response_schema_pass == true`, `postcondition_pass == true` in artifact.
- **Artifact path:** `configs/generated/caio_m365_contract_verification.json`.

---

## Failure Modes

- **Provider bug:** Returns `ok: true` with null `result` or wrong shape → verification fails; fix implementation.
- **Contract change:** New action or new result shape → update MATHEMATICS.md, invariant, and verification.
- **Artifact missing:** CI must fail when artifact is not produced or path is wrong.

---

## Why This Matters

Without this lemma, CAIO and other consumers cannot rely on a stable contract. The mathematical formulation and invariant allow CI to enforce that the provider never drifts from the guaranteed postconditions.
