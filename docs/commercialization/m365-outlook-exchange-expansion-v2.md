# SMARTHAUS M365 Outlook / Exchange Expansion v2

## Purpose

`E2B` turns mail, calendar, contact, and mailbox operations into a real instruction-api workload instead of leaving them fragmented between legacy ops-adapter handlers and partially surfaced routing contracts.

## What E2B Closes

Before `E2B`, the repo already had significant messaging runtime in `src/ops_adapter/actions.py`, but the public M365 instruction API still did not expose the full Outlook / Exchange slice through the v2 control plane.

`E2B` closes that gap by making the instruction API, shared Graph runtime, and the v2 registries agree on the expanded messaging surface:

- mail
  - `list_messages`
  - `get_message`
  - `send_mail`
  - `move_message`
  - `delete_message`
  - `list_mail_folders`
  - `get_mailbox_settings`
  - `update_mailbox_settings`
- calendar
  - `list_events`
  - `create_event`
  - `get_event`
  - `update_event`
  - `delete_event`
  - `get_schedule`
- contacts
  - `list_contacts`
  - `get_contact`
  - `create_contact`
  - `update_contact`
  - `delete_contact`
  - `list_contact_folders`

## Deterministic Rule

`E2B_GO = InstructionApiExpanded ∧ GraphClientBacked ∧ CapabilityRegistryImplemented ∧ MessagingRouteBounded ∧ HybridAuthBounded ∧ ApprovalProfilesSynced`

## Shared Mailbox Handling

Shared mailbox handling is not a separate executor domain.

It is modeled through the same messaging actions by supplying explicit mailbox context:

- `userId`
- `userPrincipalName`
- `mailbox`

If no explicit mailbox context is present, the messaging auth model may prefer delegated `/me` execution for self-context requests. If the runtime is app-only and no mailbox owner is provided, the Graph client fails closed instead of guessing a mailbox target.

## Runtime Projection

The expansion is projected through:

- instruction API surface
  - `src/provisioning_api/routers/m365.py`
- shared Graph runtime
  - `src/smarthaus_graph/client.py`
- capability and workload authority
  - `registry/capability_registry.yaml`
  - `registry/outlook_exchange_expansion_v2.yaml`
- v2 control-plane alignment
  - `registry/executor_routing_v2.yaml`
  - `registry/auth_model_v2.yaml`
  - `registry/approval_risk_matrix_v2.yaml`
- contract and verification
  - `docs/CAIO_M365_CONTRACT.md`
  - `docs/contracts/caio-m365/ACTION_SPECIFICATION.md`
  - `scripts/ci/verify_caio_m365_contract.py`
  - `scripts/ci/verify_capability_registry.py`
  - `scripts/ci/verify_outlook_exchange_expansion.py`

## Result

After `E2B`, the M365 pack can honestly claim that Outlook / Exchange messaging work is no longer just a planned capability family. It is now:

- instruction-addressable
- graph-backed through the shared client
- capability-registered
- executor-routed to `messaging`
- auth-bounded to `hybrid`
- approval-profiled for low-risk reads and medium-operational mutations

## Next Dependency

`E2C` is next. SharePoint, OneDrive, files, and broader site content work now inherit the same v2 control-plane pattern that `E2A` applied to directory work and `E2B` applied to messaging work.
