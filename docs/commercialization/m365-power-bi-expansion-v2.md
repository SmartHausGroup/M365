# SMARTHAUS M365 Power BI Expansion v2

## Purpose

`E3C` turns Power BI into a governed workload slice instead of leaving workspace, report, dataset, and dashboard operations outside the M365 pack.

## What E3C Closes

Before `E3C`, the workforce could claim bounded Power Automate and Power Apps coverage, but it could not honestly claim bounded analytics coverage. There was no instruction contract for Power BI workspace inspection, report inspection, dataset inspection, dashboard inspection, or dataset refresh control.

`E3C` closes that gap by making the instruction API, runtime adapter, and v2 registries agree on this bounded Power BI surface:

- workspace inventory and inspection
  - `list_powerbi_workspaces`
  - `get_powerbi_workspace`
- report inventory and inspection
  - `list_powerbi_reports`
  - `get_powerbi_report`
- dataset inventory and inspection
  - `list_powerbi_datasets`
  - `get_powerbi_dataset`
  - `list_powerbi_dataset_refreshes`
  - `refresh_powerbi_dataset`
- dashboard inventory and inspection
  - `list_powerbi_dashboards`
  - `get_powerbi_dashboard`

## Deterministic Rule

`E3C_GO = InstructionApiExpanded ∧ PowerBIRuntimeBounded ∧ CapabilityRegistryImplemented ∧ PowerPlatformRouteBounded ∧ AuthBounded ∧ ApprovalProfilesSynced`

## Auth Boundary

`E3C` keeps Power BI on the `powerplatform` executor and intentionally bounds the service-principal path to the official Power BI REST API.

That means:

- the executor must carry an Entra application credential through the selected tenant contract
- reads remain inventory and analytics inspection only
- the only mutation in this slice is bounded dataset refresh initiation
- no Fabric authoring, semantic-model editing, gateway administration, or tenant-wide admin portal claim is made here

## Runtime Projection

The expansion is projected through:

- instruction API surface
  - `src/provisioning_api/routers/m365.py`
- bounded Power BI runtime
  - `src/smarthaus_common/power_bi_client.py`
- capability and workload authority
  - `registry/capability_registry.yaml`
  - `registry/power_bi_expansion_v2.yaml`
- v2 control-plane alignment
  - `registry/executor_routing_v2.yaml`
  - `registry/auth_model_v2.yaml`
  - `registry/approval_risk_matrix_v2.yaml`
- contract and verification
  - `docs/CAIO_M365_CONTRACT.md`
  - `docs/contracts/caio-m365/ACTION_SPECIFICATION.md`
  - `scripts/ci/verify_caio_m365_contract.py`
  - `scripts/ci/verify_capability_registry.py`
  - `scripts/ci/verify_power_bi_expansion.py`

## Result

After `E3C`, the M365 pack can honestly claim a first bounded Power BI slice that covers:

- workspace inventory
- report inventory and inspection
- dataset inventory and inspection
- dashboard inventory and inspection
- dataset refresh initiation and refresh-history inspection

## Boundary

`E3C` is intentionally bounded:

- no report creation or publishing
- no dashboard creation or tile authoring
- no dataset parameter editing or datasource rebinding
- no gateway administration
- no Fabric lakehouse, notebook, warehouse, or pipeline claim
- no tenant-level Power BI admin portal claim beyond the bounded workspace-level REST surface

## Next Dependency

`E3D` is next. With Power BI now under the v2 control plane, the expansion can move into workflow connectors and adjacent automation surfaces without pretending analytics is still absent from the workforce capability universe.
