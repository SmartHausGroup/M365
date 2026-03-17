# L2 — CAIO M365 Idempotency

## Claim

For the same successful logical request and the same idempotency key, replay returns the cached response rather than executing a divergent mutation.

## Existing Proof Sources

- `docs/contracts/caio-m365/LEMMA_L2.md`
- `docs/contracts/caio-m365/MATHEMATICS.md`
- `configs/generated/m365_idempotency_verification.json`

## Acceptance Evidence

- `idempotency_pass == true`

## Source Invariant

- `invariants/INV-CAIO-M365-002.yaml`
