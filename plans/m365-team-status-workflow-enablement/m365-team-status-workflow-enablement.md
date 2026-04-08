# Plan: M365 Team Status Workflow Enablement

**Plan ID:** `plan:m365-team-status-workflow-enablement`
**Parent Plan ID:** `plan:m365-power-platform-executor-auth-remediation`
**Status:** `in_progress`
**Date:** `2026-04-08`
**Owner:** `SMARTHAUS`
**Execution plan reference:** `plan:m365-team-status-workflow-enablement:R0`
**North Star alignment:** `Operations/NORTHSTAR.md` — advance the M365-only self-service operating model by making a real cross-workload weekly team operating loop provisionable through Teams, Outlook, SharePoint, and Power Automate instead of leaving workflow automation at the recipe-catalog or admin-read stage.
**Governance evidence:** `notebooks/m365/INV-M365-DH-team-status-workflow-plan-governance-alignment-v1.ipynb`, `configs/generated/team_status_workflow_plan_governance_alignment_v1_verification.json`

## Objective

Make the direct repo runtime able to provision and validate a real weekly team status workflow:

- recurring team meeting
- shared progress tracker
- Friday reminder automation
- consolidated weekly digest automation

## Problem Statement

The current repo is close, but not yet able to do the workflow the user actually wants.

- Power Platform auth drift is repaired, but the selected runtime identity currently sees `0` accessible Power Platform environments.
- The public instruction surface can create recurring calendar events and create SharePoint list items, but it does not yet expose SharePoint list creation even though the Graph client already supports it.
- The Power Automate surface can read and administer existing flows, but it does not yet expose a bounded provisioning path for a new flow or a reusable workflow package.

That means the repo can describe the workflow, but it cannot yet provision the full operating loop truthfully.

## Decision Rule

`WeeklyStatusWorkflowReady = EnvironmentAccessible ∧ TrackerProvisioning ∧ FlowProvisioning ∧ ScenarioValidation`

`EnvironmentAccessible = VisiblePowerPlatformEnvironment(runtime_identity) ∧ ConnectorBaselineKnown`

`TrackerProvisioning = CreateListSupported ∧ ListSchemaLocked`

`FlowProvisioning = ReminderFlowProvisionable ∧ DigestFlowProvisionable`

`ScenarioValidation = RecurringMeetingCreated ∧ TrackerCreated ∧ ReminderFlowLive ∧ DigestFlowLive`

`GO = WeeklyStatusWorkflowReady ∧ ScenarioValidation`

If `GO` is false, the package remains open and reports the first remaining real blocker exactly.

## Scope

### In scope

- create the governed plan package and tracker activation
- diagnose and fix Power Platform environment accessibility for the runtime identity
- expose the missing repo surface needed to create the tracker
- add a bounded provisioning path for the weekly team status automation
- define the deterministic workflow contract and template assets
- provision and validate a real reference workflow end-to-end
- publish truthful diagnostics and closeout

### Out of scope

- UCP-side packaging or marketplace work
- generic unrestricted workflow-engine claims
- committing live secrets or private keys
- pretending the workflow is green without live tenant proof

### File allowlist

- `plans/m365-team-status-workflow-enablement/**`
- `docs/prompts/codex-m365-team-status-workflow-enablement.md`
- `docs/prompts/codex-m365-team-status-workflow-enablement-prompt.txt`
- `notebooks/m365/INV-M365-DH-team-status-workflow-plan-governance-alignment-v1.ipynb`
- `configs/generated/team_status_workflow_plan_governance_alignment_v1_verification.json`
- `docs/commercialization/m365-team-status-workflow-enablement.md`
- `artifacts/diagnostics/m365_team_status_workflow_enablement.json`
- `src/provisioning_api/routers/m365.py`
- `src/smarthaus_graph/client.py`
- `src/smarthaus_common/power_automate_client.py`
- `src/smarthaus_common/power_apps_client.py`
- `src/smarthaus_common/tenant_config.py`
- `src/smarthaus_common/team_status_workflow.py`
- `scripts/ops/provision_team_status_workflow.py`
- `registry/sharepoint_onedrive_files_expansion_v2.yaml`
- `registry/power_automate_expansion_v2.yaml`
- `registry/capability_registry.yaml`
- `registry/executor_routing_v2.yaml`
- `registry/auth_model_v2.yaml`
- `registry/approval_risk_matrix_v2.yaml`
- `registry/cross_workload_automation_recipes_v2.yaml`
- `docs/CAIO_M365_CONTRACT.md`
- `docs/contracts/caio-m365/ACTION_SPECIFICATION.md`
- `docs/contracts/M365_CAPABILITIES_UNIVERSE.md`
- `tests/test_sharepoint_onedrive_files_expansion_v2.py`
- `tests/test_power_automate_expansion_v2.py`
- `tests/test_team_status_workflow.py`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `.env`
- `../UCP/**`
- any secret-bearing local file or certificate private key

## Requirements

### R0 — Governed package activation

- create the plan triplet, prompt pair, governance notebook, and tracker activation

### R1 — Tenant environment accessibility

- determine whether a usable Power Platform environment exists for the runtime identity
- if not, create or expose one through the bounded tenant-admin path
- prove the runtime identity can see the environment and the baseline connectors needed for the workflow

### R2 — Repo surface completion

- expose SharePoint list creation on the public instruction surface
- add a bounded provisioning path for the weekly team status automation instead of leaving it as manual portal work

### R3 — Deterministic workflow contract

- lock the tracker schema, meeting recurrence, reminder rule, and digest rule
- freeze the reference workflow inputs and expected outputs

### R4 — Live provisioning

- provision a real reference workflow in the tenant:
  - recurring weekly meeting
  - progress tracker
  - Friday reminder
  - weekly digest

### R5 — End-to-end validation

- prove the created workflow assets are visible and actionable through the repo
- manually simulate or directly invoke the reminder/digest path if waiting for clock time is unnecessary

### R6 — Truthful closeout

- publish the final live result and any remaining external boundary exactly

## Execution Order

1. `R0`
2. `R1`
3. `R2`
4. `R3`
5. `R4`
6. `R5`
7. `R6`

## Success Criteria

- the runtime identity can see at least one usable Power Platform environment
- the repo can create the progress tracker from the public instruction surface
- the repo can provision the reminder and digest automation path truthfully
- the reference weekly status workflow is created and inspectable
- the final state is documented as green or blocked with the exact remaining reason

## Validation

- focused tests for any new repo surfaces
- live repo-direct validation for environment visibility, tracker creation, meeting creation, and automation visibility
- `pre-commit run --all-files`
- `git diff --check`

## Execution Status

- `R0` is active.
- No tenant changes or runtime changes have been executed under this package yet.
- The next act is `R1`, the tenant environment accessibility repair.
