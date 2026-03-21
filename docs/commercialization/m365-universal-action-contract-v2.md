# SMARTHAUS Universal Action Contract v2

## Purpose

Define one canonical action contract that can represent the expanded workforce action surface across the three action dialects already present in the repo:

- CAIO / instruction API snake_case actions
- capability-registry snake_case actions
- agent-registry dotted, snake_case, and hyphenated actions

## Root Problem

The repo currently has one workforce goal but multiple action languages:

- [CAIO_M365_CONTRACT.md](/Users/smarthaus/Projects/GitHub/M365/docs/CAIO_M365_CONTRACT.md) exposes a narrow request envelope with `9` supported snake_case actions
- [capability_registry.yaml](/Users/smarthaus/Projects/GitHub/M365/registry/capability_registry.yaml) tracks a `270`-action capability universe, also mostly snake_case
- [agents.yaml](/Users/smarthaus/Projects/GitHub/M365/registry/agents.yaml) exposes `184` distinct allowed actions, mostly dotted, with some snake_case and hyphenated legacy names

Without a universal contract, later phases would have to keep translating ad hoc between those surfaces.

## Core Rule

Every future workforce action must be representable as:

`UniversalActionV2 = Identity × Semantics × Execution × Governance × Evidence`

Where:

- `Identity`
  - canonical action key
  - workload family
  - capability family
  - resource
  - operation
  - legacy aliases
- `Semantics`
  - mutating or not
  - input contract
  - result contract
  - idempotency expectations
  - implementation status
- `Execution`
  - executor domain
  - auth class
  - required permissions
- `Governance`
  - risk class
  - approval profile
  - allowed persona classes
- `Evidence`
  - source surfaces
  - docs, notebooks, invariants, tests

## Canonical Key

The canonical key format is now:

`<executor_domain>.<resource>.<operation>`

Rules:

- lower-case only
- exactly three segments
- resource is singular
- operation can use underscores, but not extra dots

Examples:

- `directory.user.list`
- `directory.user.password_reset`
- `sharepoint.site.create`
- `collaboration.team.create`
- `messaging.mail.send`
- `workmanagement.task.create`

## Request Envelope v2

Minimum request envelope:

```json
{
  "action_key": "directory.user.list",
  "params": {},
  "persona_id": "m365-administrator",
  "requestor": "phil@smarthausgroup.com",
  "executor_hint": "directory",
  "idempotency_key": "optional-but-required-for-mutations",
  "correlation_id": "optional-trace-id",
  "evidence_mode": "optional"
}
```

Rules:

- `action_key` must be canonical
- legacy aliases are resolved before execution
- `params` must be an object
- mutating orchestration paths require idempotency support

## Response Envelope v2

Minimum response envelope:

```json
{
  "ok": true,
  "result": {},
  "error": null,
  "trace_id": "uuid",
  "action_key": "directory.user.list",
  "executor_domain": "directory",
  "auth_class": "app_only",
  "approval_required": false,
  "evidence_refs": []
}
```

This extends, not replaces, the existing v1 response envelope by adding the control-plane metadata future waves will need.

## Projection From Existing Surfaces

### CAIO / instruction API

Current v1 request:

```json
{
  "action": "list_users",
  "params": {}
}
```

V2 projection:

- resolve `list_users` -> `directory.user.list`
- preserve `params`
- add persona / requestor / executor context upstream when available

### Capability registry

Current shape:

- `action: list_users`
- `domain: identity`
- `status: implemented`

V2 projection:

- treat `action` as an alias, not the final canonical key
- project into the v2 identity, semantics, execution, governance, and evidence fields

### Agent registry

Current shape:

- `allowed_actions: ["users.list", "sites.provision", "mail.send", ...]`

V2 projection:

- treat agent-registry strings as persona-facing aliases
- resolve them into the canonical key before executor routing and policy evaluation

## What This Resolves

`E1A` resolves the main action-surface ambiguity:

- one canonical key format
- one universal definition schema
- one request envelope
- one response envelope
- one alias model from the old surfaces into the new surface

## What This Does Not Yet Resolve

- expanded workload implementation
- department-pack and persona-runtime rollout

Those remaining phases begin at:

- `E2A` through `E9E`

## Structured Authority

The machine-readable authority for this act is:

- [universal_action_contract_v2.yaml](/Users/smarthaus/Projects/GitHub/M365/registry/universal_action_contract_v2.yaml)

That file is now the canonical v2 contract source for later control-plane phases.
