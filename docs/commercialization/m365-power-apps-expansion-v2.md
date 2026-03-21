# SMARTHAUS M365 Power Apps Expansion v2

## Purpose

`E3B` turns Power Apps into a governed workload slice instead of leaving apps and environment-role management as out-of-band admin work.

## What E3B Closes

Before `E3B`, the M365 pack could claim Power Platform workflow automation through `E3A`, but it could not honestly claim a bounded Power Apps administration surface. There was no instruction contract for Power App inventory, app-level role inspection, ownership transfer, environment-role inspection, or environment-role mutation.

`E3B` closes that gap by making the instruction API, runtime adapter, and v2 registries agree on this bounded Power Apps surface:

- app inventory and inspection
  - `list_powerapps_admin`
  - `get_powerapp_admin`
  - `list_powerapp_role_assignments`
- app governance
  - `set_powerapp_owner`
  - `remove_powerapp_role_assignment`
  - `delete_powerapp`
- environment inspection and governance
  - `list_powerapp_environments`
  - `get_powerapp_environment`
  - `list_powerapp_environment_role_assignments`
  - `set_powerapp_environment_role_assignment`
  - `remove_powerapp_environment_role_assignment`

## Deterministic Rule

`E3B_GO = InstructionApiExpanded ∧ PowerAppsRuntimeBounded ∧ CapabilityRegistryImplemented ∧ PowerPlatformRouteBounded ∧ AuthBounded ∧ ApprovalProfilesSynced`

## Auth Boundary

`E3B` keeps Power Apps on the `powerplatform` executor and intentionally bounds the administrative service-principal path to the official Power Apps administration PowerShell module.

That means:

- the executor must carry a client-secret-backed service principal for `Add-PowerAppsAccount`
- the slice is administrative and governance-oriented, not canvas-app authoring or designer editing
- environment role operations are bounded to the documented non-Dataverse environment-role cmdlets, which fail if called against Dataverse-backed environments

## Runtime Projection

The expansion is projected through:

- instruction API surface
  - `src/provisioning_api/routers/m365.py`
- bounded Power Apps runtime
  - `src/smarthaus_common/power_apps_client.py`
- capability and workload authority
  - `registry/capability_registry.yaml`
  - `registry/power_apps_expansion_v2.yaml`
- v2 control-plane alignment
  - `registry/executor_routing_v2.yaml`
  - `registry/auth_model_v2.yaml`
  - `registry/approval_risk_matrix_v2.yaml`
- contract and verification
  - `docs/CAIO_M365_CONTRACT.md`
  - `docs/contracts/caio-m365/ACTION_SPECIFICATION.md`
  - `scripts/ci/verify_caio_m365_contract.py`
  - `scripts/ci/verify_capability_registry.py`
  - `scripts/ci/verify_power_apps_expansion.py`

## Result

After `E3B`, the M365 pack can honestly claim a first bounded Power Apps slice that covers:

- admin inventory
- app inspection
- app-level permission inspection
- ownership transfer
- app role removal
- app deletion
- environment inspection
- environment role inspection and mutation

## Boundary

`E3B` is intentionally bounded:

- no canvas authoring or formula editing
- no solution packaging or import/export claim
- no Dataverse-table authoring claim
- no app publish lifecycle claim beyond the documented admin delete/ownership/role surfaces
- no Power BI claim; that remains `E3C`

## Next Dependency

`E3C` is next. With Power Apps now under the v2 control plane, the expansion can move into Power BI without pretending the Power Platform app surface is still absent from the workforce capability universe.
