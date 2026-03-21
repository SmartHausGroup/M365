# L3 — CAIO M365 Authentication

## Claim

When the CAIO API key gate is enabled, missing or invalid auth input is rejected fail-closed.

## Existing Proof Sources

- `docs/contracts/caio-m365/LEMMA_L3.md`
- `docs/contracts/caio-m365/MATHEMATICS.md`
- `configs/generated/m365_auth_verification.json`

## Acceptance Evidence

- `auth_pass == true`

## Source Invariant

- `invariants/INV-CAIO-M365-003.yaml`
