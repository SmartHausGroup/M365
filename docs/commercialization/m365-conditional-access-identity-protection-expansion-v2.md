# M365 Conditional Access / Identity Protection Expansion v2

## Purpose

`E4D` makes bounded conditional-access and identity-protection administration real inside the shared workforce control plane.

## Implemented Surface

- `list_conditional_access_policies`
- `get_conditional_access_policy`
- `create_conditional_access_policy`
- `update_conditional_access_policy`
- `delete_conditional_access_policy`
- `list_named_locations`
- `list_risk_detections`

## Boundary

This slice covers conditional-access policy administration, named-location inspection, and identity-protection risk-detection inspection. It does not claim What-If simulation, authentication-strength administration, risky-user remediation, or full Entra portal parity.

## Deterministic Guarantees

1. Every implemented action is routed to the bounded `identity_security` executor.
2. Every implemented action resolves to `app_only` auth in the v2 auth model.
3. Read actions remain non-approval-bearing even though they expose sensitive security state.
4. Policy mutations are approval-bearing and fail closed under the high-impact profile.
5. Runtime, contracts, registries, and verifiers all agree on the same seven-action surface.
