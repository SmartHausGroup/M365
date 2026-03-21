# Lemma L36 — M365 Forms / Approvals / Connectors Expansion v2

## Statement

`E3D` is complete only when the bounded approvals-app and Microsoft 365 connector workload authority, runtime projection, instruction surface, capability registry, executor routing, auth model, approval matrix, and verification artifacts all agree on the same implemented action family.

## Scope

The lemma covers:

- Approval solution inspection
- Approval item inventory, inspection, creation, request inspection, and response submission
- Microsoft 365 connector inventory and inspection
- External connection creation and schema registration
- External item inspection and upsert
- External group creation and membership addition

## Proof Sketch

1. The workload authority fixes the exact supported action family, canonical keys, permissions, and result-shape claims.
2. The instruction router exposes those actions and normalizes only the bounded parameter shapes.
3. The runtime adapter resolves approval actions through delegated or hybrid auth and connector actions through the documented executor domains, failing closed when the auth contract is violated.
4. The capability registry, auth model, executor routing, and approval matrix all record the same action family as implemented.
5. The verifier and tests prove the instruction surface, routing, auth, approvals, and result-shape claims remain aligned.

## Failure Boundary

If any declared action is missing from the router, missing from the implemented registry set, routed to the wrong executor, assigned the wrong auth class, assigned the wrong approval profile, or exposed with a mismatched result shape, `L36` fails closed.
