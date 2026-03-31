# M365 Service Auth / Runtime Repair

## Purpose

Record the actual execution result of `plan:m365-token-provider-runtime-repair`
without inventing a local M365 fix that would weaken the governed auth
contract.

## Observed Truth

The current cross-repo boundary is:

- UCP reaches the M365 service over HTTP service mode.
- The M365 service still requires `Authorization: Bearer <token>` on
  `/actions/*`.
- The current UCP HTTP client in
  `../UCP/packs/m365_pack/client.py` sends only:
  - `Content-Type`
  - `X-Correlation-ID`
- The current UCP caller does **not** send:
  - `Authorization`
  - `X-User-Email`
  - `X-Principal-Email`

That means the M365 service never crosses its own JWT gate. It fails closed at:

- `401 missing_bearer_token`

and does so before Graph token acquisition or Microsoft permission evaluation.

## Root Cause

This phase proved that the remaining defect is not a hidden M365-local parsing
bug. The remaining defect is that the sibling UCP caller still does not satisfy
the service-auth contract the M365 service already enforces.

The M365 service currently supports:

- bounded dev mode: HS256 bearer validation via `JWT_HS256_SECRET`
- production mode: issuer / audience / JWKS validation

Those paths only activate when a bearer token is actually present.

## Why No Local M365 Patch Was Applied

No bounded M365-only repair can make the current caller succeed without one of
the following contract violations:

- weakening the bearer requirement
- reintroducing header-only actor identity by default
- synthesizing actor identity that the caller never supplied

All three violate the fail-closed service-auth boundary and the cross-repo
contract note.

## Decision

`NO-GO`

The phase stops on scope drift:

- the next required change is sibling UCP caller alignment
- live token classification is still downstream of that change
- end-to-end acceptance remains blocked

## Preserved Guarantees

- JWT-backed actor identity remains fail-closed
- local service-auth failures remain distinct from downstream Microsoft failures
- this repo does not claim Microsoft credential or permission failure when Graph
  was never reached

## Next Valid Boundary

The next valid act is in the sibling UCP repo:

1. add the caller-side bearer path that satisfies the M365 service contract
2. rerun UCP token acquisition validation
3. only then rerun end-to-end acceptance
