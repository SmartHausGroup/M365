# Plan: M365 Incident Response War Room Workflow Enablement

**Plan ID:** `plan:m365-incident-response-war-room-workflow-enablement`
**Parent Plan ID:** `none`
**Status:** `complete`
**Date:** `2026-04-08`
**Owner:** `SMARTHAUS`
**Execution plan reference:** `plan:m365-incident-response-war-room-workflow-enablement:R4`
**North Star alignment:** `Operations/NORTHSTAR.md` — advance the M365-only self-service operating model by turning the existing incident response recipe into a real repo-direct workflow across Teams, SharePoint, Planner, and Outlook instead of leaving it as catalog-only metadata.
**Historical lineage:** follows the completed `plan:m365-team-status-workflow-enablement` package and the completed `plan:m365-direct-full-surface-certification` package, which left Planner writes and reusable multi-step workflow execution as the next truthful repo-direct gap.

## Objective

Make the direct repo runtime able to provision and validate a real incident response war room workflow:

- incident Team
- command channel
- SharePoint incident site
- runbook document
- Planner plan and first task
- activation email

## Problem Statement

The repo can currently describe the incident response workflow, but it cannot execute it truthfully.

- `incident_response_war_room` already exists in `registry/cross_workload_automation_recipes_v2.yaml`, but only as a discovery recipe.
- There is no composite repo-direct action that provisions the workflow end to end.
- There is no shared runtime module or operator script for the workflow.
- The most relevant live blocker from direct certification is still open: Planner writes were fenced by live Graph `403`, so a multi-step workflow that depends on plan/task creation has not yet been proven.

That means the repo can advertise the workflow pattern, but it cannot yet create the actual workspace truthfully through the direct runtime.

## Decision Rule

`IncidentWarRoomReady = WorkspaceProvisioning ∧ RunbookProvisioning ∧ TaskingProvisioning ∧ NotificationProvisioning ∧ ScenarioValidation`

`WorkspaceProvisioning = TeamProvisionable ∧ ChannelProvisionable ∧ SiteProvisionable`

`RunbookProvisioning = RunbookDocumentProvisionable`

`TaskingProvisioning = PlannerPlanProvisionable ∧ PlannerTaskProvisionable`

`NotificationProvisioning = ActivationMailProvisionable`

`ScenarioValidation = TeamVisible ∧ ChannelVisible ∧ SiteVisible ∧ RunbookVisible ∧ PlannerArtifactsVisible ∧ ActivationMailAccepted`

`GO = IncidentWarRoomReady ∧ ScenarioValidation`

If `GO` is false, the package remains open and reports the first remaining real blocker exactly.

## Scope

### In scope

- create the governed plan package and tracker activation
- freeze the deterministic workflow contract for the incident response war room
- add a bounded composite action for repo-direct workflow provisioning
- add the shared workflow runtime module and operator script
- wire the new action into the public instruction surface, routing, auth, approval, and contract docs
- add focused regression coverage
- run the agreed bounded validation set and publish the truthful outcome

### Out of scope

- UCP-side workflow orchestration
- generic unrestricted workflow-engine claims
- new external incident-management integrations
- silent bypass of Planner, approval, or tenant permission boundaries
- committing secrets or private keys

### File allowlist

- `plans/m365-incident-response-war-room-workflow-enablement/**`
- `plans/m365-incident-response-war-room-workflow-notebook-evidence-scope-correction/**`
- `docs/prompts/codex-m365-incident-response-war-room-workflow-enablement.md`
- `docs/prompts/codex-m365-incident-response-war-room-workflow-enablement-prompt.txt`
- `docs/prompts/codex-m365-incident-response-war-room-workflow-notebook-evidence-scope-correction.md`
- `docs/prompts/codex-m365-incident-response-war-room-workflow-notebook-evidence-scope-correction-prompt.txt`
- `docs/commercialization/m365-incident-response-war-room-workflow-enablement.md`
- `docs/ma/lemmas/L97_m365_incident_response_war_room_workflow_enablement_v1.md`
- `invariants/lemmas/L97_m365_incident_response_war_room_workflow_enablement_v1.yaml`
- `notebooks/m365/INV-M365-DI-incident-response-war-room-workflow-governance-alignment-v1.ipynb`
- `notebooks/m365/INV-M365-DJ-incident-response-war-room-workflow-enablement-v1.ipynb`
- `notebooks/lemma_proofs/L97_m365_incident_response_war_room_workflow_enablement_v1.ipynb`
- `artifacts/scorecards/scorecard_l97.json`
- `configs/generated/incident_response_war_room_workflow_governance_alignment_v1_verification.json`
- `configs/generated/incident_response_war_room_workflow_enablement_v1_verification.json`
- `src/smarthaus_common/incident_response_war_room.py`
- `src/provisioning_api/routers/m365.py`
- `src/smarthaus_graph/client.py`
- `scripts/ops/provision_incident_response_war_room.py`
- `registry/capability_registry.yaml`
- `registry/executor_routing_v2.yaml`
- `registry/auth_model_v2.yaml`
- `registry/approval_risk_matrix_v2.yaml`
- `docs/CAIO_M365_CONTRACT.md`
- `docs/contracts/caio-m365/ACTION_SPECIFICATION.md`
- `docs/contracts/M365_CAPABILITIES_UNIVERSE.md`
- `tests/test_incident_response_war_room.py`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `.env`
- `../UCP/**`
- any secret-bearing local file or certificate private key

## Requirements

### R0 — Governed package activation

- create the plan triplet, prompt pair, and tracker activation

### R1 — Deterministic workflow contract

- freeze the workflow inputs, expected outputs, reuse rules, and failure boundaries
- define the bounded public action contract for the new composite workflow action

### R2 — Repo surface completion

- add the bounded repo-direct workflow runtime and operator script
- wire the workflow into the public instruction surface and supporting registries

### R3 — Focused validation surface

- add focused regression coverage for input parsing, idempotent reuse behavior, and instruction-contract execution

### R4 — Truthful closeout

- run the agreed validation set
- publish the truthful result and any exact remaining external blocker

## Execution Order

1. `R0`
2. `R1`
3. `R2`
4. `R3`
5. `R4`

## Success Criteria

- the repo exposes a bounded composite action for incident response war room provisioning
- the workflow runtime can create or reuse the expected Team, channel, site, runbook, plan, task, and notification assets
- the composite action is covered by focused regression tests
- the final state is documented as green or blocked with the exact remaining reason

## Validation

- `python3 -m py_compile src/provisioning_api/routers/m365.py src/smarthaus_common/incident_response_war_room.py scripts/ops/provision_incident_response_war_room.py tests/test_incident_response_war_room.py`
- `PYTHONPATH=src .venv/bin/pytest -q tests/test_incident_response_war_room.py`
- `PYTHONPATH=src .venv/bin/pytest -q tests/test_teams_groups_planner_expansion_v2.py tests/test_endpoints.py tests/test_ops_adapter.py`
- `git diff --check`

## Execution Status

- `R0` and `R1` are complete, and the notebook-backed `L97` evidence chain remains the governing proof surface for the workflow package.
- The bounded child blocker package `plan:m365-incident-response-war-room-workflow-notebook-evidence-scope-correction` is complete. It reopened the blocked code-scope `validate_action(file_edit)` call under child-plan authority and handed the parent initiative back to runtime extraction.
- `R2` and `R3` are complete locally. The repo now includes the bounded workflow runtime, router and Graph wiring, operator script, contract and registry synchronization, and focused regression coverage for the incident workflow.
- The agreed local `R4` validation slice is green:
  - `python3 -m py_compile ...` passed
  - `PYTHONPATH=src .venv/bin/pytest -q tests/test_incident_response_war_room.py` passed (`4 passed`)
  - `PYTHONPATH=src .venv/bin/pytest -q tests/test_teams_groups_planner_expansion_v2.py tests/test_endpoints.py tests/test_ops_adapter.py` passed (`144 passed`) with `32` existing JWT key-length warnings from `tests/test_ops_adapter.py`
  - `git diff --check` passed
- `R4` is now complete. A bounded live tenant proof run on `2026-04-08` created the workflow group-backed workspace identity at group `b36a0d62-2694-4870-9a1a-79eec455e271` and SharePoint site `https://smarthausgroup.sharepoint.com/sites/codex-ir-validation-20260408-174211`.
- The same bounded live probe recorded the exact remaining external blockers:
  - `/teams/{groupId}` returned `404` during the probe window, so Team and channel visibility were not yet observable.
  - `/groups/{groupId}/planner/plans` returned live Graph `403`, making Planner the exact hard external blocker for full live-green workflow completion.
- The original long-running CLI provisioning process stalled after downstream readiness waits and was terminated once the exact external blocker was captured.
- The package closes truthfully with a live recorded blocker instead of a fake-green result. Any further advance now requires a separate tenant-permission or readiness follow-on package rather than more local extraction work inside this one.
