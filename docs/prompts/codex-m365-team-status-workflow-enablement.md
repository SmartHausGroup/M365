# Codex Prompt: M365 Team Status Workflow Enablement

Plan reference: `plan:m365-team-status-workflow-enablement`

## Objective

Make the repo able to provision and validate a real weekly team status workflow using Microsoft 365 only:

- recurring team meeting
- shared progress tracker
- Friday reminder
- weekly digest

## Required reads before mutating work

- `AGENTS.md`
- applicable `.cursor/rules/**/*.mdc`
- `Operations/NORTHSTAR.md`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`
- `plans/m365-team-status-workflow-enablement/m365-team-status-workflow-enablement.md`
- `docs/commercialization/m365-power-platform-executor-auth-remediation.md`
- `src/provisioning_api/routers/m365.py`
- `src/smarthaus_graph/client.py`
- `src/smarthaus_common/power_apps_client.py`
- `src/smarthaus_common/power_automate_client.py`
- `src/smarthaus_common/tenant_config.py`

## Required outputs

- truthful Power Platform environment access for the runtime identity
- repo surface for tracker provisioning
- bounded provisioning path for the weekly team status workflow
- live proof for the reference workflow or an exact blocker

## Hard constraints

- no UCP work
- no committed secrets or private keys
- no fake-green claims
- fail closed on missing environment or ambiguous Power Platform identity

## Execution order

1. `R1` tenant environment accessibility
2. `R2` repo surface completion
3. `R3` deterministic workflow contract
4. `R4` live provisioning
5. `R5` end-to-end validation
6. `R6` closeout

## Stop conditions

- stop only on a real blocker that cannot be cleared through the repo process, governance flow, or tenant-admin path
- if the blocker is governance admissibility, open the blocker-fix package and keep moving
