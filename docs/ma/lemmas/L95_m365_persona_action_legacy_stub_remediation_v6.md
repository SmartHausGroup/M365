# L95: M365 Persona-Action Legacy-Stub Remediation v6

## Scope

- `deployment.production`
- `website.deploy`
- `cdn.purge`
- `dns.update`
- `ssl.renew`
- `performance.optimize`
- `backup.restore`

## Replacement Mode

Every target alias must fail closed as `unsupported_m365_only_action`.

## Deterministic Claim

The sixth bounded `P2` wave is valid only if the website/non-M365 aliases stop returning synthetic success payloads and instead emit deterministic explicit failure that the M365-only runtime does not support those operations.
