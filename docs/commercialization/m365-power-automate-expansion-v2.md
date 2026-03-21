# SMARTHAUS M365 Power Automate Expansion v2

## Purpose

`E3A` turns Power Automate into a governed workload slice instead of leaving flows as out-of-band portal objects.

## What E3A Closes

Before `E3A`, the M365 pack could describe workflows, but it could not honestly claim a Power Automate execution surface. There was no bounded instruction contract for flow discovery, owner governance, lifecycle control, or explicit callback invocation.

`E3A` closes that gap by making the instruction API, runtime adapter, and v2 registries agree on this bounded Power Automate surface:

- discovery
  - `list_flows_admin`
  - `get_flow_admin`
  - `list_http_flows`
  - `list_flow_owners`
  - `list_flow_runs`
- governance and lifecycle
  - `set_flow_owner_role`
  - `remove_flow_owner_role`
  - `enable_flow`
  - `disable_flow`
  - `delete_flow`
  - `restore_flow`
- explicit invocation
  - `invoke_flow_callback`

## Deterministic Rule

`E3A_GO = InstructionApiExpanded ∧ PowerAutomateRuntimeBounded ∧ CapabilityRegistryImplemented ∧ PowerPlatformRouteBounded ∧ AuthBounded ∧ ApprovalProfilesSynced`

## Auth Boundary

`E3A` keeps Power Automate on the `powerplatform` executor and intentionally bounds the administrative service-principal path to the official Power Apps / Power Automate PowerShell modules.

That means:

- the executor must carry a client-secret-backed service principal for `Add-PowerAppsAccount`
- flow inventory and lifecycle actions are administrative surfaces, not maker-designer editing
- callback invocation is explicit and bounded to a provided callback URL instead of pretending the pack can synthesize any arbitrary flow trigger

## Runtime Projection

The expansion is projected through:

- instruction API surface
  - `src/provisioning_api/routers/m365.py`
- bounded Power Automate runtime
  - `src/smarthaus_common/power_automate_client.py`
- capability and workload authority
  - `registry/capability_registry.yaml`
  - `registry/power_automate_expansion_v2.yaml`
- v2 control-plane alignment
  - `registry/executor_routing_v2.yaml`
  - `registry/auth_model_v2.yaml`
  - `registry/approval_risk_matrix_v2.yaml`
- contract and verification
  - `docs/CAIO_M365_CONTRACT.md`
  - `docs/contracts/caio-m365/ACTION_SPECIFICATION.md`
  - `scripts/ci/verify_caio_m365_contract.py`
  - `scripts/ci/verify_capability_registry.py`
  - `scripts/ci/verify_power_automate_expansion.py`

## Result

After `E3A`, the M365 pack can honestly claim a first bounded Power Automate slice that covers:

- admin inventory
- HTTP-triggered flow discovery
- owner-role governance
- lifecycle control
- flow-run monitoring
- explicit callback invocation

## Boundary

`E3A` is intentionally bounded:

- no visual designer editing
- no connector-secret authoring
- no run-only-user mutation surface yet
- no promise of arbitrary flow execution beyond explicit callback invocation
- no Power Apps or Power BI claim; those remain `E3B` and `E3C`

## Next Dependency

`E3B` is next. With Power Automate now under the v2 control plane, the expansion can move into Power Apps without pretending workflow automation is still absent from the workload universe.
