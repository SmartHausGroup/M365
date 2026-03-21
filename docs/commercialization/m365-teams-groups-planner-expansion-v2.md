# SMARTHAUS M365 Teams / Groups / Planner Expansion v2

## Purpose

`E2D` turns the missing Teams depth and Planner workspace actions into a real instruction-api workload instead of leaving them split between legacy ops-adapter handlers, hidden Graph helpers, and planned-only capability entries.

## What E2D Closes

Before `E2D`, the repo could already create teams, add channels, and run some Planner orchestration internally, but the public M365 instruction API still did not expose the broader collaboration and task-management slice through the v2 control plane.

`E2D` closes that gap by making the instruction API, shared Graph runtime, and the v2 registries agree on this bounded collaboration / Planner surface:

- Teams and channels
  - `get_team`
  - `list_channels`
  - `create_channel`
- Planner
  - `list_plans`
  - `create_plan`
  - `list_plan_buckets`
  - `create_plan_bucket`
  - `create_plan_task`

## Deterministic Rule

`E2D_GO = InstructionApiExpanded ∧ GraphClientBacked ∧ CapabilityRegistryImplemented ∧ CollaborationRouteBounded ∧ AuthBounded ∧ ApprovalProfilesSynced`

## Auth Boundary

`E2D` keeps the whole bounded surface on the existing `collaboration` executor and therefore keeps every new action `app_only` for now.

That is deliberate:

- it stays aligned with the live executor split already in the tenant contract
- it avoids introducing a new `workmanagement` executor before the tenant contract is ready
- it makes the Planner slice usable now without scope-drifting into a fresh executor rollout

## Runtime Projection

The expansion is projected through:

- instruction API surface
  - `src/provisioning_api/routers/m365.py`
- shared Graph runtime
  - `src/smarthaus_graph/client.py`
- capability and workload authority
  - `registry/capability_registry.yaml`
  - `registry/teams_groups_planner_expansion_v2.yaml`
- v2 control-plane alignment
  - `registry/executor_routing_v2.yaml`
  - `registry/auth_model_v2.yaml`
  - `registry/approval_risk_matrix_v2.yaml`
- contract and verification
  - `docs/CAIO_M365_CONTRACT.md`
  - `docs/contracts/caio-m365/ACTION_SPECIFICATION.md`
  - `scripts/ci/verify_caio_m365_contract.py`
  - `scripts/ci/verify_capability_registry.py`
  - `scripts/ci/verify_teams_groups_planner_expansion.py`

## Result

After `E2D`, the M365 pack can honestly claim that the first deeper Teams and Planner operations are no longer just planned capability families. They are now:

- instruction-addressable
- graph-backed through the shared client
- capability-registered
- executor-routed to `collaboration`
- auth-bounded to `app_only`
- approval-profiled as low-risk reads, high-impact channel creation, and medium-operational Planner mutations

## Next Dependency

`E2E` is next. Documents, notes, and workspace productivity inherit the same v2 control-plane pattern that `E2A` applied to directory work, `E2B` applied to messaging work, `E2C` applied to SharePoint / files work, and `E2D` now applies to collaboration and Planner depth.
