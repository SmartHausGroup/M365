# L91 — Persona-Action Legacy-Stub Remediation v2

## Intent

Freeze the second bounded `P2` legacy-stub remediation wave so it can be implemented under explicit notebook-backed authority instead of ad hoc alias rewrites.

## Alias Set

- `followup.create`
- `client.follow-up`
- `satisfaction.survey`
- `interview.schedule`

## Replacement Modes

- `followup.create -> calendar_create`
- `client.follow-up -> calendar_create`
- `satisfaction.survey -> mail_send`
- `interview.schedule -> calendar_create`

## Deterministic Claim

If the bounded second-wave alias set is preserved exactly and each alias routes through the stated replacement mode, the second bounded `P2` implementation wave can be validated as a truthful reduction of the legacy-stub surface.
