# SMARTHAUS M365 SharePoint / OneDrive / Files Expansion v2

## Purpose

`E2C` turns SharePoint site content, SharePoint list content, OneDrive, and drive-item operations into a real instruction-api workload instead of leaving them fragmented between legacy ops-adapter handlers and partially surfaced routing contracts.

## What E2C Closes

Before `E2C`, the repo already had significant SharePoint and files runtime in `src/ops_adapter/actions.py`, but the public M365 instruction API still did not expose the broader SharePoint / OneDrive / files slice through the v2 control plane.

`E2C` closes that gap by making the instruction API, shared Graph runtime, and the v2 registries agree on the expanded SharePoint / files surface:

- SharePoint sites and lists
  - `get_site`
  - `list_site_lists`
  - `get_list`
  - `list_list_items`
  - `create_list_item`
- drives and files
  - `list_drives`
  - `get_drive`
  - `list_drive_items`
  - `get_drive_item`
  - `create_folder`
  - `upload_file`

## Deterministic Rule

`E2C_GO = InstructionApiExpanded ∧ GraphClientBacked ∧ CapabilityRegistryImplemented ∧ SharePointRouteBounded ∧ AuthBounded ∧ ApprovalProfilesSynced`

## Auth Boundary

`E2C` deliberately keeps two auth classes inside one workload family:

- SharePoint site/list reads and list-item creation remain `app_only`
- drive and file operations are `hybrid`

That keeps site/list governance deterministic while still allowing `/me`-style drive work when delegated context is appropriate.

## Runtime Projection

The expansion is projected through:

- instruction API surface
  - `src/provisioning_api/routers/m365.py`
- shared Graph runtime
  - `src/smarthaus_graph/client.py`
- capability and workload authority
  - `registry/capability_registry.yaml`
  - `registry/sharepoint_onedrive_files_expansion_v2.yaml`
- v2 control-plane alignment
  - `registry/executor_routing_v2.yaml`
  - `registry/auth_model_v2.yaml`
  - `registry/approval_risk_matrix_v2.yaml`
- contract and verification
  - `docs/CAIO_M365_CONTRACT.md`
  - `docs/contracts/caio-m365/ACTION_SPECIFICATION.md`
  - `scripts/ci/verify_caio_m365_contract.py`
  - `scripts/ci/verify_capability_registry.py`
  - `scripts/ci/verify_sharepoint_onedrive_files_expansion.py`

## Result

After `E2C`, the M365 pack can honestly claim that SharePoint content and drive/file work is no longer just a planned capability family. It is now:

- instruction-addressable
- graph-backed through the shared client
- capability-registered
- executor-routed to `sharepoint`
- auth-bounded to expected `app_only` or `hybrid` behavior
- approval-profiled for low-risk reads and medium-operational content mutations

## Next Dependency

`E2D` is next. Teams, groups, and Planner workspace depth inherit the same v2 control-plane pattern that `E2A` applied to directory work, `E2B` applied to messaging work, and `E2C` applies to SharePoint / files work.
