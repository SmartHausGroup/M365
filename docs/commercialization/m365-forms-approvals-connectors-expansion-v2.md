# M365 Forms / Approvals / Connectors Expansion v2

## Scope

`E3D` closes the bounded Power Platform gap between Power BI and cross-workload recipes.

Implemented runtime surface:

- Approvals app APIs through Microsoft Graph beta.
- Microsoft 365 Copilot connector APIs for connections, schemas, items, and external groups.

Explicit boundary:

- Direct Microsoft Forms authoring and native response APIs are not claimed as implemented runtime
  actions in this act.
- Forms-triggered automation remains indirect through connector-backed or workbook-backed flows.

## Implemented actions

- `get_approval_solution`
- `list_approval_items`
- `get_approval_item`
- `create_approval_item`
- `list_approval_item_requests`
- `respond_to_approval_item`
- `list_external_connections`
- `get_external_connection`
- `create_external_connection`
- `register_external_connection_schema`
- `get_external_item`
- `upsert_external_item`
- `create_external_group`
- `add_external_group_member`

## Auth and routing

- Approvals app actions:
  - executor domain: `powerplatform`
  - auth class: `delegated`
  - note: approvals app APIs are beta-backed and fail closed unless delegated or hybrid auth is configured
- Connector actions:
  - executor domain: `knowledge`
  - auth class: `app_only`

## Risk posture

- low observe:
  - `get_approval_solution`
  - `list_approval_items`
  - `get_approval_item`
  - `list_approval_item_requests`
  - `list_external_connections`
  - `get_external_connection`
  - `get_external_item`
- medium operational:
  - `create_approval_item`
  - `upsert_external_item`
  - `create_external_group`
  - `add_external_group_member`
- high impact:
  - `respond_to_approval_item`
  - `create_external_connection`
  - `register_external_connection_schema`

## Deterministic guarantees

- Every E3D action projects into one canonical action key.
- Approvals actions fail closed when delegated or hybrid auth is unavailable.
- Connector actions fail closed when Graph identity is unavailable.
- The pack does not over-claim Forms runtime support beyond the documented indirect boundary.
