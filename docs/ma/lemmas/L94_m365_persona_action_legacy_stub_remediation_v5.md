# L94: M365 Persona-Action Legacy-Stub Remediation v5

## Scope

- `infrastructure.monitor`
- `backup.verify`
- `security.scan`

## Replacement Modes

- `infrastructure.monitor -> health_overview`
- `security.scan -> security_secure_score`
- `backup.verify -> explicit unsupported M365-only failure`

## Deterministic Claim

The fifth bounded `P2` wave is valid only if the IT-operations aliases stop returning synthetic success payloads and instead route to existing real M365 health/security handlers or fail closed with an explicit unsupported result.
