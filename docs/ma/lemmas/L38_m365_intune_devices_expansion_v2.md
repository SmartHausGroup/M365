# Lemma L38 — M365 Intune / Devices Expansion v2

## Statement

`E4A` is complete only when the bounded Intune/device workload authority, runtime projection, instruction surface, capability registry, executor routing, auth model, approval matrix, and verification artifacts all agree on the same implemented action family.

## Scope

The lemma covers:

- Managed-device inventory
- Managed-device inspection
- Device-compliance summary inspection
- Governed device lifecycle actions

## Proof Sketch

1. The workload authority fixes the exact supported device action family and expected result shapes.
2. The instruction router exposes those actions and normalizes only the bounded parameter shapes.
3. The runtime adapter resolves through the `devices` executor and fails closed outside the documented app-only/auth and approval boundaries.
4. The capability registry, auth model, executor routing, and approval matrix all record the same action family as implemented.
5. The verifier and tests prove the instruction surface, routing, auth, approvals, and result-shape claims remain aligned.

## Failure Boundary

If any supported device action is missing from the router, missing from the implemented registry set, routed to the wrong executor, assigned the wrong auth class, assigned the wrong approval profile, or exposed with a mismatched result shape, `L38` fails closed.
