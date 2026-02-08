# Lemma L2 — CAIO-M365 Idempotency (Same Key + Same Body ⇒ Cached Response) {#lemma-l2}

**Invariant:** [`invariants/INV-CAIO-M365-002.yaml`](../../invariants/INV-CAIO-M365-002.yaml)

**Status:** Draft

**Backed by:** `docs/contracts/caio-m365/MATHEMATICS.md` — Eq. 3.

---

## Assumptions

- Provider uses a single instance or shared idempotency store keyed by `Idempotency-Key`; body identity is `request_hash = hash(action, params)`.
- Two requests with the same `Idempotency-Key` and same (action, params) are treated as the same logical request.

---

## Claim

If the provider receives two requests \((R_1, H)\) and \((R_2, H)\) with the same `Idempotency-Key` and \(\mathtt{sameBody}(R_1, R_2)\), and the first request returned a success response \(S_1\), then the second response satisfies \(S_2 = S_1\) (cached) and the action is not re-executed.

---

## Derivation

1. By MATHEMATICS.md Eq. 3: \(\mathtt{sameKey}(H_1, H_2) \wedge \mathtt{sameBody}(R_1, R_2) \wedge \mathtt{success}(S_1) \Rightarrow S_2 = S_1\) (cached).
2. Implementation: `_get_idempotency_record(key)` returns stored response when `request_hash` matches; otherwise execute and `_store_idempotency_record`.
3. Verification: send two POSTs with same `Idempotency-Key` and body; assert second response body equals first and (if observable) no duplicate side effects.

---

## Verification

- **Producer:** `scripts/ci/verify_m365_idempotency.py` or `notebooks/ma_m365_idempotency.ipynb`.
- **Artifact:** `configs/generated/m365_idempotency_verification.json` with `idempotency_pass == true`.
