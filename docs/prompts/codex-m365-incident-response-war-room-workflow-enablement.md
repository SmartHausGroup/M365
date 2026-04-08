# Codex Prompt: M365 Incident Response War Room Workflow Enablement

Plan reference: `plan:m365-incident-response-war-room-workflow-enablement`

## Objective

Make the repo able to provision and validate a real incident response war room workflow using Microsoft 365 only:

- incident Team
- command channel
- SharePoint incident site
- runbook document
- Planner plan and first task
- activation email

## Required reads before mutating work

- `AGENTS.md`
- applicable `.cursor/rules/**/*.mdc`
- `Operations/NORTHSTAR.md`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`
- `plans/m365-incident-response-war-room-workflow-enablement/m365-incident-response-war-room-workflow-enablement.md`
- `registry/cross_workload_automation_recipes_v2.yaml`
- `docs/commercialization/m365-team-status-workflow-enablement.md`
- `docs/commercialization/m365-direct-full-surface-certification.md`
- `src/provisioning_api/routers/m365.py`

## Required outputs

- bounded public composite action for incident response war room provisioning
- shared workflow runtime with deterministic reuse behavior
- operator script for repo-direct execution
- focused regression proof or an exact blocker

## Hard constraints

- no UCP work
- no committed secrets or private keys
- no fake-green claims
- fail closed on Planner, approval, or tenant permission blockers

## Execution order

1. `R1` deterministic workflow contract
2. `R2` repo surface completion
3. `R3` focused validation surface
4. `R4` truthful closeout

## Stop conditions

- stop only on a real blocker that cannot be cleared through the repo process, governance flow, or tenant-admin path
- if the blocker is governance admissibility, open the blocker-fix package and keep moving
