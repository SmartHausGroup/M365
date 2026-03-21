# SMARTHAUS M365 Entra / Directory Expansion v2

## Purpose

`E2A` turns Entra and directory administration into a real instruction-api workload instead of leaving it split between docs, ops-adapter-only handlers, and legacy planned aliases.

## What E2A Closes

Before `E2A`, the repo already had substantial directory runtime in `src/ops_adapter/actions.py`, but the public M365 instruction API still exposed only the bounded `9`-action launch slice.

`E2A` closes that gap by making the instruction API and the v2 registries agree on the expanded Entra surface:

- user lifecycle
  - `create_user`
  - `update_user`
  - `disable_user`
  - `reset_user_password`
- group administration
  - `list_groups`
  - `get_group`
  - `create_group`
  - `list_group_members`
  - `add_group_member`
  - `remove_group_member`
- license administration
  - `assign_user_license`
- directory metadata and roles
  - `list_directory_roles`
  - `list_directory_role_members`
  - `list_domains`
  - `get_organization`
- application and service-principal inventory
  - `list_applications`
  - `get_application`
  - `update_application`
  - `list_service_principals`

## Deterministic Rule

`E2A_GO = InstructionApiExpanded ∧ GraphClientBacked ∧ CapabilityRegistryImplemented ∧ DirectoryRouteBounded ∧ AppOnlyAuthBounded ∧ ApprovalProfilesSynced`

## Runtime Projection

The expansion is projected through:

- instruction API surface
  - `src/provisioning_api/routers/m365.py`
- Graph client support
  - `src/smarthaus_graph/client.py`
- capability and workload authority
  - `registry/capability_registry.yaml`
  - `registry/entra_directory_expansion_v2.yaml`
- v2 control-plane alignment
  - `registry/executor_routing_v2.yaml`
  - `registry/auth_model_v2.yaml`
  - `registry/approval_risk_matrix_v2.yaml`
- contract and verification
  - `docs/CAIO_M365_CONTRACT.md`
  - `docs/contracts/caio-m365/ACTION_SPECIFICATION.md`
  - `scripts/ci/verify_caio_m365_contract.py`
  - `scripts/ci/verify_capability_registry.py`
  - `scripts/ci/verify_entra_directory_expansion.py`

## Result

After `E2A`, the M365 pack can honestly claim that Entra and directory administration is no longer just a planned capability family. It is now:

- instruction-addressable
- graph-backed
- capability-registered
- executor-routed to `directory`
- auth-bounded to `app_only`
- approval-profiled for low-risk reads and high-impact mutations

## Next Dependency

`E2B` is next. Mail, calendar, shared mailbox, and broader Exchange work now inherit the same v2 control-plane pattern that `E2A` applied to Entra and directory administration.
