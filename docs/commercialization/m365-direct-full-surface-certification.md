# M365 Direct Full Surface Certification

## Status

`F1` is complete. The direct full-surface certification program has cleared its current environment and tenant enablement blockers, and `F2` read-path certification is now the next act.

## Purpose

This initiative exists because the repo is beyond partial smoke testing now. The user requirement is stronger: the direct M365 surface this repo claims to support must be locked, enabled, and tested truthfully enough that Claude or Codex can be asked to perform supported Microsoft 365 work with real confidence.

## F0 Universe Lock

The notebook-backed `F0` baseline is:

- Notebook: `notebooks/m365/INV-M365-CH-direct-full-surface-certification-universe-lock-v1.ipynb`
- Machine-readable artifact: `artifacts/diagnostics/m365_direct_full_surface_certification.json`

The locked baseline counts are:

- `59` agents
- `155` direct instruction actions
- `184` persona-facing allowed-action aliases
- `340` capability-registry actions
- `146` crosswalked canonical actions when the v2 expansion registries and cross-workload recipe catalog are combined

## What F0 Proved

The repo does not yet expose one single direct-certification surface. It currently has multiple overlapping action vocabularies:

- direct instruction actions in `src/provisioning_api/routers/m365.py`
- persona-facing aliases in `registry/agents.yaml`
- capability-registry actions in `registry/capability_registry.yaml`
- canonicalized v2 action mappings in the `*_expansion_v2.yaml` files plus `registry/cross_workload_automation_recipes_v2.yaml`

That means full certification must normalize these surfaces before any claim of “everything works” can be truthful.

## Current F0 Blockers

`F0` identified two blocker classes that matter for the rest of the program.

### 1. Legacy direct instruction actions outside the v2 crosswalk

The direct instruction surface still claims nine actions that are not yet represented in the expansion-backed canonical universe:

- `list_users`
- `get_user`
- `reset_user_password`
- `list_teams`
- `list_sites`
- `create_site`
- `create_team`
- `add_channel`
- `provision_service`

These actions are real runtime paths, but they still sit outside the current v2 expansion-backed normalization layer.

### 2. Persona-facing actions that are not real M365 execution yet

`F0` also proved that a material part of the persona-facing surface is not ready for honest full certification.

- `125` persona aliases are outside the current direct crosswalk.
- `41` actions across `8` agents are still implemented as legacy stub behavior in `src/ops_adapter/actions.py`.

The current legacy-stub agent set is:

- `it-operations-manager`
- `website-operations-specialist`
- `project-coordination-agent`
- `client-relationship-agent`
- `compliance-monitoring-agent`
- `recruitment-assistance-agent`
- `financial-operations-agent`
- `knowledge-management-agent`

These actions cannot be counted as “tested M365 functionality” until they are either implemented against real M365 behavior or explicitly fenced out of the certified surface.

## What F1 Had To Do

`F1` is now responsible for the enablement and truth decision boundary:

- identify which remaining failures are pure environment/tenant enablement blockers
- identify which remaining claimed actions are actually implementation-truth blockers
- remove the blockers that can be fixed safely inside scope
- reduce the claimed certified surface anywhere a truthful fix is not available yet

## Current Decision

The direct runtime is no longer the primary blocker. The program now moves forward with a clearer truth:

- some remaining failures are environment or tenant enablement blockers
- some remaining failures are surface-truth blockers caused by legacy action topology and stubbed behavior

Full certification can now proceed on a real baseline instead of on mixed assumptions.

## F1 Enablement Results

`F1` closed the blocker class that had kept the repaired direct runtime from being broadly testable.

### What changed

- collaboration executor Graph permissions were expanded to cover direct mail and calendar reads
- directory executor Graph permissions were expanded to cover reports and service health
- local Power Platform admin modules were installed and verified
- the `powerplatform` executor app was registered as a Power Platform management application through the documented tenant-admin operator path
- the Power Apps / Power Automate clients were hardened so PowerShell warning preambles no longer cause false parser failures

### What is now proven live from the direct repo runtime

- mail:
  - `list_messages` succeeds for the configured tenant user path
- calendar:
  - `list_events` succeeds
  - `get_schedule` succeeds when app-only input includes explicit `userId`
- service health:
  - the governed service-health overview path succeeds with the enabled directory executor roles
- Power Apps:
  - `list_powerapp_environments` succeeds through the `powerplatform` executor
- Power Automate:
  - `list_flows_admin` succeeds through the `powerplatform` executor and returns a truthful zero-flow result when no flows are present

### What F1 did not solve

`F1` did not certify the whole claimed surface. It removed the direct enablement blockers. The remaining work is now certification work:

- read-path certification across the supported surface
- mutation and approval-path certification
- truthful surface reduction where legacy stub behavior or crosswalk gaps still prevent honest certification
