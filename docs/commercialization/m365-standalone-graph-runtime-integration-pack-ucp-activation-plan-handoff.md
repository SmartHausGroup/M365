# UCP Activation Plan Handoff - M365 Standalone Graph Runtime Pack

**Plan:** `plan:m365-standalone-graph-runtime-integration-pack-fix:R7`
**Phase:** Fix R7 - UCP activation plan handoff (M365-side)
**Date:** 2026-04-26
**Owner:** SMARTHAUS

This document is the M365-side handoff for the missing UCP activation plan
(`F5`). M365 governance forbids this plan from editing UCP source, so the
sibling plan must be opened by a UCP-side planner. This document provides
the exact plan content the UCP planner needs.

## Truthful Boundary

- The M365-side fix pack is GO at `com.smarthaus.m365@1.1.1`.
- Live UCP install/launch/setup/auth/action acceptance through the
  installed pack is the responsibility of the sibling UCP plan
  `plan:ucp-m365-standalone-graph-runtime-pack-activation`.
- That plan does not yet exist under `/Users/smarthaus/Projects/GitHub/UCP/plans/`
  at the time of writing (verified by directory listing during the fix run).
- Until that plan exists and executes, this M365 fix pack records the
  M365-side artifact and acceptance evidence only; final cross-repo GO
  remains pending UCP-side execution.

## Recommended UCP Plan Layout

A UCP-side planner should create the following files inside
`/Users/smarthaus/Projects/GitHub/UCP/plans/ucp-m365-standalone-graph-runtime-pack-activation/`:

- `ucp-m365-standalone-graph-runtime-pack-activation.md`
- `ucp-m365-standalone-graph-runtime-pack-activation.yaml`
- `ucp-m365-standalone-graph-runtime-pack-activation.json`

And, under `/Users/smarthaus/Projects/GitHub/UCP/docs/prompts/`:

- `codex-ucp-m365-standalone-graph-runtime-pack-activation.md`
- `codex-ucp-m365-standalone-graph-runtime-pack-activation-prompt.txt`

## Recommended UCP Plan Content (verbatim)

### `ucp-m365-standalone-graph-runtime-pack-activation.md`

```markdown
# Plan: UCP M365 Standalone Graph Runtime Pack Activation

**Plan ID:** `ucp-m365-standalone-graph-runtime-pack-activation`
**Parent plan ID:** `m365-standalone-graph-runtime-integration-pack-fix` (sibling, in M365 repo)
**Status:** Draft
**Owner:** UCP
**Date:** 2026-04-26

## Mission

Activate the standalone Microsoft 365 Graph runtime Integration Pack
`com.smarthaus.m365@1.1.1` from the local Integration Pack store
(`/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/1.1.1/`) into UCP
runtime state. Drive setup/auth/health/action through the installed pack
runtime and record live read-only acceptance through UCP. M365 source is
not consulted at runtime.

## Phases

- `U1` Discover the local pack and verify SHA256SUMS.
- `U2` Read the manifest (`schema_version=0.2.0`) and the declared
  `runtime` block: `module=m365_runtime`, `entrypoint_command=["python","-m","m365_runtime"]`,
  `default_host=127.0.0.1`, `default_port=9300`,
  `health_path=/v1/health/readiness`, `auth_start_path=/v1/auth/start`,
  `auth_check_path=/v1/auth/check`, `auth_status_path=/v1/auth/status`,
  `auth_clear_path=/v1/auth/clear`, `actions_path=/v1/actions`,
  `invoke_path_template=/v1/actions/{action_id}/invoke`,
  `read_only=true`, `mutation_fence=true`.
- `U3` Render the packaged `setup_schema.json` to the operator. Reject
  `password` at the UI layer for symmetry with the runtime validator.
- `U4` Launch the runtime via the manifest entrypoint command from the
  install root, dynamically picking a free local port.
- `U5` Drive `POST /v1/auth/start` to begin the operator's selected flow
  (`auth_code_pkce`, `device_code`, `app_only_secret`,
  `app_only_certificate`).
- `U6` Drive `POST /v1/auth/check` until `state="signed_in"`.
- `U7` Poll `GET /v1/health/readiness`. Project `Ready=true` to the
  operator only when the runtime returns the literal `state="ready"` and
  `label="success"`.
- `U8` Invoke at least one read-only action through
  `POST /v1/actions/{action_id}/invoke` and verify `status_class=success`.
- `U9` Run `POST /v1/auth/clear` on operator request.
- `U10` Stop the runtime cleanly on uninstall.

## Acceptance

- Bundle integrity: SHA256SUMS in install dir matches.
- Manifest declares the full auth lifecycle.
- Runtime launches, exposes the declared endpoints on the chosen port,
  and stops cleanly.
- Auth flow completes against a live tenant.
- Readiness reports `ready/success` only after auth+token+graph+permission
  probes are all true.
- One read-only Graph action returns `success`.
- Mutation actions remain fenced.

## Stop Conditions

- `password` auth attempted -> abort.
- Token bytes leaked into UCP logs/audit -> abort.
- Source-repo dependency observed in installed runtime behavior -> abort.
- Graph write actions attempted before mutation-governance plan opens -> abort.
```

### `ucp-m365-standalone-graph-runtime-pack-activation.yaml`

```yaml
plan_id: ucp-m365-standalone-graph-runtime-pack-activation
sibling_plan_id: m365-standalone-graph-runtime-integration-pack-fix
sibling_repo: /Users/smarthaus/Projects/GitHub/M365
status: Draft
date: "2026-04-26"
owner: UCP
target_artifact:
  pack_id: com.smarthaus.m365
  version: "1.1.1"
  install_root: /Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/1.1.1
  bundle_file: com.smarthaus.m365-1.1.1.ucp.tar.gz
runtime_contract_paths:
  health: /v1/health/readiness
  auth_start: /v1/auth/start
  auth_check: /v1/auth/check
  auth_status: /v1/auth/status
  auth_clear: /v1/auth/clear
  actions: /v1/actions
  invoke: /v1/actions/{action_id}/invoke
phases:
  U1: integrity_verify
  U2: manifest_read
  U3: setup_render
  U4: runtime_launch
  U5: auth_start
  U6: auth_check
  U7: readiness_project
  U8: read_only_action
  U9: auth_clear
  U10: stop_clean
```

### `ucp-m365-standalone-graph-runtime-pack-activation.json`

```json
{
  "plan_id": "ucp-m365-standalone-graph-runtime-pack-activation",
  "sibling_plan_id": "m365-standalone-graph-runtime-integration-pack-fix",
  "status": "Draft",
  "owner": "UCP",
  "target_artifact": {
    "pack_id": "com.smarthaus.m365",
    "version": "1.1.1",
    "install_root": "/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/1.1.1"
  },
  "phase_status": {
    "U1": "pending",
    "U2": "pending",
    "U3": "pending",
    "U4": "pending",
    "U5": "pending",
    "U6": "pending",
    "U7": "pending",
    "U8": "pending",
    "U9": "pending",
    "U10": "pending"
  }
}
```

### `codex-ucp-m365-standalone-graph-runtime-pack-activation-prompt.txt`

```text
Execute the governed UCP activation plan at:

`docs/prompts/codex-ucp-m365-standalone-graph-runtime-pack-activation.md`

Repo: /Users/smarthaus/Projects/GitHub/UCP

Plan: plans/ucp-m365-standalone-graph-runtime-pack-activation/ucp-m365-standalone-graph-runtime-pack-activation.md

Activate the standalone M365 pack `com.smarthaus.m365@1.1.1` from
`/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/1.1.1/` into UCP
runtime state. Do not edit M365 source. Continue until U10 is green
unless a true hard blocker is reached.
```

## What This Document Does Not Do

- It does not create any file under `/Users/smarthaus/Projects/GitHub/UCP/`.
  Doing so from the M365 fix pack would violate the M365/UCP boundary
  lock recorded in `m365-standalone-graph-runtime-integration-pack-intent-and-boundary.md`.
- It does not claim cross-repo GO. The M365-side fix pack ships truthful
  M365 evidence; the UCP-side plan must produce its own evidence under
  UCP governance.

## Closure

- This document is the M365-side `F5` deliverable.
- A UCP-side planner can drop the recommended files into the UCP repo
  verbatim to open the sibling plan.
- Until the UCP-side plan executes, the cross-repo "live UCP through the
  installed pack" target remains explicitly deferred and any release
  language must reflect that boundary.
