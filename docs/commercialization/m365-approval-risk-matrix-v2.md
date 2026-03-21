# M365 Approval and Risk Matrix v2

## Purpose

`E1D` closes the governance gap between:

- persona-level approval posture from `E0D`
- v2 action identity from `E1A`
- bounded executor and auth projection from `E1B` and `E1C`
- the governed ops-adapter runtime that still needed one shared approval/risk authority

The goal is one deterministic source for:

1. `risk_class`
2. `approval_profile`
3. `approval_required`
4. default approver projection for approval-bearing actions

## Deterministic Rule

`ApprovalRiskV2(agent, action, params) = ExactPolicy(action) ∨ PrefixPolicy(action) ∨ DomainDefault(Route(agent, action))`

`ApprovalRequired = ExactRequirement(action, params) ∨ PrefixRequirement(action, params) ∨ DomainRequirement(Route(agent, action))`

`PersonaApprovalProfile = ActionOverride ∨ PersonaMap(agent) ∨ medium-operational`

This keeps approval and risk classification deterministic even while the workforce grows beyond the current standalone v1 slice.

## Risk Classes

| Risk class | Meaning |
| --- | --- |
| `low` | Read-only, inspect, or low-blast-radius work with no tenant-state mutation. |
| `medium` | Routine operational mutation with bounded blast radius and recoverable impact. |
| `high` | Privileged, externally visible, tenant-shaping, or identity-impacting mutation. |
| `critical` | Regulated, personnel-state, destructive, security-sensitive, or compliance-sensitive mutation. |

## Approval Profiles

| Approval profile | Human approvals | Default posture |
| --- | --- | --- |
| `low-observe-create` | `0` | No approval for read, research, draft, or internal-prep work; approval only when an exact or prefix policy marks the action as outward-facing or privileged. |
| `medium-operational` | `1` | Department-owner approval for routine internal mutations when the action policy explicitly marks the mutation as approval-bearing. |
| `high-impact` | `1` | Human approval for tenant, identity, public-facing, financial, or organization-wide changes; fail closed if approvers are missing. |
| `critical-regulated` | `2` | Dual human approval and explicit sign-off for regulated, destructive, legal, personnel-state, security, or compliance-sensitive mutations. |

## Current Exact Approval-Bearing Actions

The machine-readable authority is [approval_risk_matrix_v2.yaml](/Users/smarthaus/Projects/GitHub/M365/registry/approval_risk_matrix_v2.yaml).

Current exact approval-bearing overrides include:

- `users.create`
- `users.update`
- `users.disable`
- `reset_user_password`
- `groups.create`
- `groups.add_member`
- `licenses.assign`
- `teams.create`
- `teams.add_channel`
- `channels.create`
- `sites.provision`
- `create_site`
- `create_team`
- `add_channel`
- `provision_service`
- `deployment.production`
- `employee.offboard`
- `email.send_bulk` when `recipients_count > 100`

These preserve the currently proven high-impact governance behaviors while giving the expanded control plane one deterministic authority instead of scattered legacy heuristics.

## Read and Observe Prefixes

The matrix also locks a low-risk, no-approval baseline for read-only and inspect-oriented surfaces, including:

- `users.list`
- `users.read`
- `groups.list`
- `groups.get`
- `groups.list_members`
- `sites.list`
- `sites.get`
- `sites.root`
- `lists.list`
- `lists.get`
- `lists.items`
- `files.list`
- `files.get`
- `files.search`
- `drives.list`
- `mail.list`
- `mail.read`
- `mail.folders`
- `mailbox.settings`
- `calendar.list`
- `calendar.get`
- `calendar.availability`
- `chat.list`

## Runtime Projection

The shared runtime resolver is [approval_risk.py](/Users/smarthaus/Projects/GitHub/M365/src/smarthaus_common/approval_risk.py).

The governed ops-adapter path now projects:

- `risk_class`
- `approval_profile`
- `approval_required_by_matrix`
- `approval_rule_source`

into the action params before policy and approval execution in [main.py](/Users/smarthaus/Projects/GitHub/M365/src/ops_adapter/main.py).

This means:

1. old OPA rules can remain the allow/deny engine
2. the v2 approval matrix can still force approval fail-closed where the old OPA surface is incomplete
3. approval records and audit payloads inherit deterministic approval/risk metadata

## What E1D Resolves

`E1D` resolves the approval-authority split:

- one machine-readable approval/risk matrix
- one shared runtime resolver
- one deterministic way to decide approval-bearing actions
- one shared metadata projection for approval and audit surfaces

## What E1D Does Not Yet Resolve

- unified audit schema normalization across all workforce surfaces
- complete workload-by-workload runtime implementation beyond the current bounded surfaces
- live workforce certification for the expanded action universe

Those remaining phases begin at:

- `E2A` through `E9E`
