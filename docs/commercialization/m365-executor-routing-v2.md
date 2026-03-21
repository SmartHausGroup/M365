# SMARTHAUS Executor Routing v2

## Purpose

Define one deterministic routing authority for workforce actions so the runtime no longer depends on scattered hardcoded tables.

## Root Problem

Before `E1B`, executor routing lived in multiple places:

- hardcoded prefix and override tables in `src/ops_adapter/actions.py`
- a second hardcoded action map in `src/provisioning_api/routers/m365.py`
- persona-domain derivation that depended on the ops-adapter table indirectly

That meant the control plane had a canonical action contract from `E1A`, but no single runtime authority for choosing bounded executors.

## Core Rule

`ExecutorRouteV2(agent, action) -> exactly_one_executor_domain`

Routing resolves in this strict order:

1. agent-specific override
2. canonical v2 action key first segment
3. exact legacy action alias
4. legacy dotted-prefix route
5. fail closed

If none of those produce exactly one bounded executor domain, execution must stop.

## Authority Surface

The machine-readable routing authority is now:

- [executor_routing_v2.yaml](/Users/smarthaus/Projects/GitHub/M365/registry/executor_routing_v2.yaml)

The runtime consumers are now:

- [executor_routing.py](/Users/smarthaus/Projects/GitHub/M365/src/smarthaus_common/executor_routing.py)
- [actions.py](/Users/smarthaus/Projects/GitHub/M365/src/ops_adapter/actions.py)
- [personas.py](/Users/smarthaus/Projects/GitHub/M365/src/ops_adapter/personas.py)
- [m365.py](/Users/smarthaus/Projects/GitHub/M365/src/provisioning_api/routers/m365.py)

## Deterministic Contract

### Canonical v2 actions

Canonical keys from `E1A` route by their first segment if that segment is a known bounded executor domain.

Examples:

- `directory.user.list` -> `directory`
- `sharepoint.site.create` -> `sharepoint`
- `collaboration.team.create` -> `collaboration`

### Legacy exact aliases

The current CAIO/instruction actions and selected capability-registry actions route through exact aliases.

Examples:

- `list_users` -> `directory`
- `create_site` -> `sharepoint`
- `create_team` -> `collaboration`
- `send_mail` -> `messaging`

### Legacy dotted aliases

The current agent-registry dotted actions route through prefix rules.

Examples:

- `sites.get` -> `sharepoint`
- `teams.create` -> `collaboration`
- `mail.send` -> `messaging`
- `users.disable` -> `directory`

### Agent overrides

Only the explicit small set of business-facing aliases that cannot be inferred from canonical keys, exact aliases, or dotted prefixes use agent-specific overrides.

Examples:

- `website-manager` + `deployment.preview` -> `sharepoint`
- `hr-generalist` + `employee.onboard` -> `directory`
- `outreach-coordinator` + `email.send_individual` -> `messaging`

## What E1B Resolves

`E1B` resolves the executor-authority split:

- one routing registry
- one shared resolver
- one fail-closed routing order
- one path for ops-adapter routing, persona-domain derivation, and instruction-router executor projection

## What E1B Does Not Yet Resolve

- expanded workload implementation on top of the bounded executor domains
- later persona, certification, and launch phases

Those remaining phases begin at:

- `E2A` through `E9E`
