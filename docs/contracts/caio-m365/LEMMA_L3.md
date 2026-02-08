# Lemma L3 — CAIO-M365 Authentication (Key Required ⇒ Missing/Invalid ⇒ 401) {#lemma-l3}

**Invariant:** [`invariants/INV-CAIO-M365-003.yaml`](../../invariants/INV-CAIO-M365-003.yaml)

**Status:** Draft

**Backed by:** `docs/contracts/caio-m365/MATHEMATICS.md` — Eq. 4.

---

## Assumptions

- When `CAIO_API_KEY` is set in the environment, the provider requires a valid key in `X-CAIO-API-Key` or `X-CAIO-Token`.
- Requests without the header, or with a wrong value, are rejected before execution.

---

## Claim

If the provider is configured with `CAIO_API_KEY` set and a request \(R\) has \(\mathtt{keyMissingOrInvalid}(H)\), then the response has HTTP status 401 and no instruction is executed.

---

## Derivation

1. By MATHEMATICS.md Eq. 4: \(\mathtt{keyMissingOrInvalid}(H) \Rightarrow \mathtt{status}(S) = 401\).
2. Implementation: `_validate_caio_api_key(request)` returns false when key is required and missing or wrong; handler returns 401 before `execute_instruction_contract`.
3. Verification: with `CAIO_API_KEY` set, send request without key or with wrong key; assert status 401.

---

## Verification

- **Producer:** `scripts/ci/verify_m365_auth.py` or `notebooks/ma_m365_auth.ipynb`.
- **Artifact:** `configs/generated/m365_auth_verification.json` with `auth_pass == true`.
