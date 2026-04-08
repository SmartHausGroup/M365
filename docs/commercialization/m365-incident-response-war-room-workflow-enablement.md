# M365 Incident Response War Room Workflow Enablement

## Status

`R0` through `R4` are complete. The direct repo runtime now exposes a bounded composite incident-workflow action locally, and a bounded live tenant proof run has been recorded. The package does not close live-green: the probe created the M365 group and SharePoint site, but the Team endpoint still returned `404` during the probe window and Planner access returned Graph `403`.

## Purpose

This initiative exists to turn the existing `incident_response_war_room` recipe into a real repo-direct workflow instead of leaving it as catalog-only metadata. The bounded workflow is:

- incident Team
- command channel
- SharePoint incident site
- runbook document
- Planner plan and seed task
- activation email

## What Changed

### `R1` deterministic workflow contract

The incident workflow is now frozen around one shared M365 group-backed workspace identity.

Truthful contract:

- `teamName` and `siteName` must resolve to one shared workspace identity
- if they do not, the caller must provide explicit `mailNickname`
- the workflow creates or reuses one command channel, one runbook document, one Planner plan, one Planner bucket, and one seed task
- activation mail is bounded to an explicit sender mailbox and explicit recipient set
- Planner remains a fail-closed live boundary

The notebook-backed evidence chain is:

- [INV-M365-DI-incident-response-war-room-workflow-governance-alignment-v1.ipynb](/Users/smarthaus/Projects/GitHub/M365/notebooks/m365/INV-M365-DI-incident-response-war-room-workflow-governance-alignment-v1.ipynb)
- [L97_m365_incident_response_war_room_workflow_enablement_v1.md](/Users/smarthaus/Projects/GitHub/M365/docs/ma/lemmas/L97_m365_incident_response_war_room_workflow_enablement_v1.md)
- [L97_m365_incident_response_war_room_workflow_enablement_v1.yaml](/Users/smarthaus/Projects/GitHub/M365/invariants/lemmas/L97_m365_incident_response_war_room_workflow_enablement_v1.yaml)
- [INV-M365-DJ-incident-response-war-room-workflow-enablement-v1.ipynb](/Users/smarthaus/Projects/GitHub/M365/notebooks/m365/INV-M365-DJ-incident-response-war-room-workflow-enablement-v1.ipynb)
- [L97_m365_incident_response_war_room_workflow_enablement_v1.ipynb](/Users/smarthaus/Projects/GitHub/M365/notebooks/lemma_proofs/L97_m365_incident_response_war_room_workflow_enablement_v1.ipynb)
- [scorecard_l97.json](/Users/smarthaus/Projects/GitHub/M365/artifacts/scorecards/scorecard_l97.json)

### `R2` repo surface completion

The repo now has a bounded provisioning implementation in:

- [incident_response_war_room.py](/Users/smarthaus/Projects/GitHub/M365/src/smarthaus_common/incident_response_war_room.py)
- [m365.py](/Users/smarthaus/Projects/GitHub/M365/src/provisioning_api/routers/m365.py)
- [client.py](/Users/smarthaus/Projects/GitHub/M365/src/smarthaus_graph/client.py)
- [provision_incident_response_war_room.py](/Users/smarthaus/Projects/GitHub/M365/scripts/ops/provision_incident_response_war_room.py)

What is now implemented locally:

- workspace creation or reuse through one shared group-backed identity
- command-channel creation or reuse
- top-level runbook document upload with deterministic create-vs-update status
- Planner plan, bucket, and seed-task create-or-reuse behavior
- activation mail send-on-create behavior with optional forced resend

### `R3` focused regression surface

Focused regression coverage now exists for:

- idempotent reuse behavior
- instruction-contract execution
- workspace-identity mismatch fail-closed behavior

See [test_incident_response_war_room.py](/Users/smarthaus/Projects/GitHub/M365/tests/test_incident_response_war_room.py).

## Validation

The agreed local `R4` validation slice is now green:

- `python3 -m py_compile src/provisioning_api/routers/m365.py src/smarthaus_common/incident_response_war_room.py scripts/ops/provision_incident_response_war_room.py tests/test_incident_response_war_room.py`
- `PYTHONPATH=src .venv/bin/pytest -q tests/test_incident_response_war_room.py` -> `4 passed`
- `PYTHONPATH=src .venv/bin/pytest -q tests/test_teams_groups_planner_expansion_v2.py tests/test_endpoints.py tests/test_ops_adapter.py` -> `144 passed`, `32` warnings
- `git diff --check`

The `32` warnings come from existing short-key JWT fixtures in `tests/test_ops_adapter.py`; they did not fail the bounded regression slice.

### Live tenant proof

Bounded live proof run on `2026-04-08`:

- incident name: `Codex IR Validation 2026-04-08 174211`
- mail nickname: `codex-ir-validation-20260408-174211`
- group id: `b36a0d62-2694-4870-9a1a-79eec455e271`
- site root: `200` at `https://smarthausgroup.sharepoint.com/sites/codex-ir-validation-20260408-174211`
- Team read: `404` during the probe window
- channel list read: `404` during the probe window because the Team thread was not yet visible
- Planner plan read: `403` with a live Graph required-permissions failure on `/groups/{groupId}/planner/plans`

The original CLI provisioning process stalled after the downstream readiness waits. After the direct Graph proof captured the exact boundary, that long-running process was terminated rather than left hanging.

## Truthful Closeout

What is now true:

- the repo exposes a bounded `provision_incident_response_war_room` action locally
- the action is notebook-backed and governed
- the workflow contract no longer pretends Team and site are separate identities
- the bounded local validation slice is green after the child notebook-evidence blocker package reopened code extraction truthfully
- the live repo-direct path can create the backing M365 group and SharePoint incident site for the workflow
- this package is complete as a truthful closeout, because the live tenant result is now recorded exactly

What remains true:

- Planner is the exact remaining hard external blocker: the tenant returned live Graph `403` on `/groups/{groupId}/planner/plans`
- Team readiness was not yet observable during the bounded probe window, so `/teams/{groupId}` and `/teams/{groupId}/channels` still returned `404`
- any further advance now requires a separate tenant-permission or readiness follow-on rather than more local extraction work inside this package
