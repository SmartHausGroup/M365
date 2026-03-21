# SMARTHAUS Auth Model v2

## Purpose

Define one deterministic auth-selection contract for the workforce control plane so action routing and token acquisition no longer drift apart.

## Root Problem

Before `E1C`, the repo already supported `app_only`, `delegated`, and `hybrid` tenant auth modes, but action-level selection was still scattered:

- executor routing was centralized in `E1B`
- token acquisition could already prefer delegated mode
- user-context actions still decided `/me` versus `/users/{id}` ad hoc inside individual handlers

That left the control plane with a bounded executor model but no shared answer to:

`Which auth class should this action use, and when should hybrid actions prefer delegated self-context?`

## Core Rule

`AuthModeV2(agent, action, params, delegated_state) -> exactly_one_auth_class and one delegated-preference decision`

Resolution order is deterministic:

1. exact action policy
2. dotted-prefix action policy
3. executor-domain default
4. fail closed

## Machine Authority

The machine-readable auth authority is:

- [auth_model_v2.yaml](/Users/smarthaus/Projects/GitHub/M365/registry/auth_model_v2.yaml)

The shared runtime resolver is:

- [auth_model.py](/Users/smarthaus/Projects/GitHub/M365/src/smarthaus_common/auth_model.py)

The primary runtime consumer in this act is:

- [actions.py](/Users/smarthaus/Projects/GitHub/M365/src/ops_adapter/actions.py)

## Deterministic Contract

### `app_only`

Use service-principal execution only.

This is the default for:

- directory and tenant admin actions
- site and team provisioning
- bounded executor admin surfaces

Examples:

- `list_users`
- `get_user`
- `reset_user_password`
- `create_site`
- `create_team`
- `add_channel`
- `provision_service`

### `delegated`

Use the signed-in operator only.

This class is reserved for future actions that cannot execute correctly without a real user token. `E1C` does not need new delegated-only runtime extraction yet, but the class remains part of the v2 contract.

### `hybrid`

Prefer app-only for explicit resource targets and delegated self-context when the request omits an explicit owner.

This is the current runtime rule for:

- `mail.*`
- `calendar.*`
- `chat.*`
- `files.*`
- `drives.*`
- `email.send_individual`
- `mail.send`
- `meeting.organize`
- `availability.check`

Examples:

- `mail.send` with no `from` -> delegated `/me/sendMail`
- `mail.send` with explicit `from` -> app-only `/users/{sender}/sendMail`
- `files.list` with no `siteId`, `driveId`, or `userId` -> delegated `/me/drive/...`
- `files.list` with explicit `siteId` -> app-only `/sites/{siteId}/drive/...`

### `mixed`

Reserved for later multi-surface workloads that still span Graph and non-Graph execution paths and cannot yet be normalized to one runtime shape.

## What E1C Resolves

`E1C` closes the auth-selection gap between `E1A` and `E1B`:

- one machine-readable auth authority
- one shared auth resolver
- one deterministic answer for hybrid self-context selection
- one runtime extraction path for mail, calendar, chat, files, and drives

## What E1C Does Not Yet Resolve

- workload-by-workload auth extraction beyond the current user-context action families
- later workload, persona, certification, and launch phases

Those remaining phases begin at:

- `E2A` through `E9E`
