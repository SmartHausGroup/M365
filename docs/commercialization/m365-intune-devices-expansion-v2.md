# M365 Intune / Devices Expansion v2

## Purpose

`E4A` opens the enterprise-control workload family with a bounded Intune / managed-devices slice.

## Implemented surface

- `list_devices`
- `get_device`
- `list_device_compliance_summaries`
- `execute_device_action`

## Boundaries

- The slice targets managed-device inventory, compliance-summary visibility, and explicit lifecycle actions.
- It does not claim arbitrary device enrollment or unmanaged endpoint provisioning.
- Device lifecycle mutations stay approval-bearing and fail closed through the shared risk matrix.

## Deterministic guarantees

- All actions route to the `devices` executor domain.
- All actions use app-only auth in the bounded runtime.
- Inventory and compliance reads are low-observe.
- Explicit device actions are high-impact and approval-bearing.
