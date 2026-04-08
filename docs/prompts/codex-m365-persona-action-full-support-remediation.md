# Execution Prompt — Persona-Action Full-Support Remediation

Plan Reference: `plan:m365-persona-action-full-support-remediation`
North Star Reference: `Operations/NORTHSTAR.md`
Execution Plan Reference: `Operations/EXECUTION_PLAN.md`

**Mission:** Take the completed persona-action certification result and drive the non-green workforce surface toward truthful full support. Fix what can truthfully work. Retire or reduce what cannot.

## Governance Lock

Before any write or mutating action:

1. Read:
- `AGENTS.md`
- applicable `.cursor/rules/**/*.mdc`
- `Operations/NORTHSTAR.md`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`
- `plans/m365-persona-action-full-support-remediation/m365-persona-action-full-support-remediation.md`
- predecessor certification artifacts:
  - `plans/m365-persona-action-certification/m365-persona-action-certification.md`
  - `docs/commercialization/m365-persona-action-certification.md`
  - `artifacts/diagnostics/m365_persona_action_certification.json`
  - `configs/generated/persona_action_route_certification_v1_verification.json`

2. Cite:
- `plan:m365-persona-action-full-support-remediation:R0` through `R6`
- `P0` through `P5`

3. Stop immediately if:
- the work escapes the allowlist
- UCP-side edits are required
- truthful support would require undocumented tenant or governance bypasses

## Execution Order

1. `P0` remediation baseline lock
2. `P1` dead-route remediation
3. `P2` legacy-stub remediation
4. `P3` permission and alias remediation
5. `P4` policy-fence remediation
6. `P5` final re-certification closeout

## Hard rule

Do not preserve a persona/action claim just because it exists in a registry.

Every remediated pair must end as one of:

- `green`
- `approval-gated`
- `actor-tier-gated`
- `permission-blocked`
- `fenced`
- `legacy-stubbed`
- `dead-routed`
- or `orphaned`

If a capability cannot be made truthful:

- reduce the claim
- do not bypass governance
- do not leave it implied
