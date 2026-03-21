# M365 Security / Defender Expansion v2

## Purpose

`E4B` opens the enterprise-control workload family with a bounded Microsoft 365 security / Defender slice that is honest about what the pack can administer today.

## Implemented Surface

- `list_security_alerts`
- `get_security_alert`
- `list_security_incidents`
- `get_security_incident`
- `list_secure_scores`
- `get_secure_score_profile`
- `update_security_incident`

## Boundary

This slice covers read-heavy security administration plus one bounded response mutation on incidents. It does not claim full Defender remediation, device isolation, hunt, or threat-intelligence automation.

## Deterministic Guarantees

1. Every implemented action is routed to the bounded `security` executor.
2. Every implemented action resolves to `app_only` auth in the v2 auth model.
3. Read actions remain low-observe and non-approval-bearing.
4. `update_security_incident` is approval-bearing and fail-closed under the critical-regulated profile.
5. Runtime, contracts, registries, and verifiers all agree on the same seven-action surface.
