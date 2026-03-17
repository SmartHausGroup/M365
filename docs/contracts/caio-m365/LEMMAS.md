# CAIO-M365 Contract — Lemmas Index

**MA Phase:** 3 — Lemmas linked to invariants
**Source:** `docs/contracts/caio-m365/`; invariants in `invariants/INV-CAIO-M365-*.yaml`

This index lists all lemmas that tie the CAIO-M365 instruction API contract to its mathematics and invariants. Each lemma is documented in its own file and referenced by the invariant acceptance criteria and verification.

---

## Lemma register

| Lemma | Name | Invariant | File | Status |
|-------|------|-----------|------|--------|
| **L1** | Response postcondition (ok⇒result, ¬ok⇒error) | INV-CAIO-M365-001 | [LEMMA_L1.md](LEMMA_L1.md) | Draft → Rev 1.0 when CI gate accepted |
| **L2** | Idempotency (same key + body ⇒ cached response) | INV-CAIO-M365-002 | [LEMMA_L2.md](LEMMA_L2.md) | Draft |
| **L3** | Authentication (key required ⇒ missing/invalid ⇒ 401) | INV-CAIO-M365-003 | [LEMMA_L3.md](LEMMA_L3.md) | Draft |
| **L4** | Audit (one record per instruction when enabled) | INV-M365-AUDIT-001 | [LEMMA_L4.md](LEMMA_L4.md) | Draft |

---

## Traceability

- **Intent:** [INTENT.md](INTENT.md)
- **Mathematics:** [MATHEMATICS.md](MATHEMATICS.md) — Eq. 1 (success), Eq. 2 (error), result shapes \(\mathcal{S}_{\texttt{action}}\)
- **Invariants:** `invariants/INDEX.yaml`, `invariants/INV-CAIO-M365-001.yaml`
- **Verification:** `scripts/ci/verify_caio_m365_contract.py` → `configs/generated/caio_m365_contract_verification.json`; `verify_m365_idempotency.py` → `m365_idempotency_verification.json`; `verify_m365_auth.py` → `m365_auth_verification.json`; `verify_m365_audit.py` → `m365_audit_verification.json`.
- **CI:** All MA verifications run in `.github/workflows/ci.yml`; failure blocks merge.

When adding a new lemma: add a row here, create `LEMMA_Ln.md`, and link the invariant YAML to the lemma.
