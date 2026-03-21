# Lemma L41 — M365 Conditional Access / Identity Protection Expansion v2

## Statement

`E4D` is complete only when the bounded conditional-access and identity-protection workload authority, runtime projection, instruction surface, capability registry, executor routing, auth model, approval matrix, and verification artifacts all agree on the same implemented action family.

## Scope

The lemma covers:

- Conditional-access policy inventory and inspection
- Governed conditional-access policy creation, update, and deletion
- Named-location inventory
- Identity-protection risk-detection inventory

## Proof Sketch

1. The workload authority fixes the exact identity-security action family and result shapes.
2. The instruction router exposes those actions and normalizes only the bounded identity-security parameter shapes.
3. The runtime adapter resolves through the `identity_security` executor and fails closed outside the documented app-only and approval boundaries.
4. The capability registry, auth model, executor routing, and approval matrix all record the same identity-security slice as implemented.
5. The verifier and tests prove the instruction surface, routing, auth, approvals, and result-shape claims remain aligned.

## Failure Boundary

If any supported identity-security action is missing from the router, missing from the implemented registry set, routed to the wrong executor, assigned the wrong auth class, assigned the wrong approval profile, or exposed with a mismatched result shape, `L41` fails closed.
