# M365 Team Status Workflow Enablement

## Status

`R0` through `R6` are complete. The direct repo runtime can now provision a real weekly team status workflow across Teams, Outlook, SharePoint, and Power Automate, and the Power Platform executor path no longer depends on a SmartHaus-only engine contract.

## Purpose

This initiative exists to make one concrete operating loop work end to end through the repo instead of leaving the workflow surface at the level of recipe claims or partial admin reads. The target loop is:

- recurring weekly Teams meeting
- shared SharePoint progress tracker
- Friday reminder automation
- weekly digest automation

## What Changed

### `R1` environment accessibility

The runtime can now see a usable Power Platform environment.

Final visible environment:

- environment name: `Default-6c4cb441-342c-430f-9a9d-79c3cdb18b75`
- display name: `The SmartHaus Group (default)`
- `IsDefault=true`

That closes the earlier workflow blocker where the direct repo runtime had no environment to place Power Automate assets into.

### `R2` repo surface completion

The repo now exposes the missing workflow-building surfaces needed for the weekly operating loop:

- SharePoint list creation is exposed through the public M365 instruction surface.
- The team-status workflow now has a bounded provisioning implementation in:
  - [m365.py](/Users/smarthaus/Projects/GitHub/M365/src/provisioning_api/routers/m365.py)
  - [team_status_workflow.py](/Users/smarthaus/Projects/GitHub/M365/src/smarthaus_common/team_status_workflow.py)
  - [provision_team_status_workflow.py](/Users/smarthaus/Projects/GitHub/M365/scripts/ops/provision_team_status_workflow.py)

The credential model is also corrected at the engine layer:

- Power Platform resolution now prefers an explicit tenant executor when one exists.
- Fallback env names are now tenant-generic first:
  - `POWERPLATFORM_TENANT_ID`
  - `POWERPLATFORM_CLIENT_ID`
  - `POWERPLATFORM_CLIENT_SECRET`
  - `POWERPLATFORM_CLIENT_CERTIFICATE_PATH`
  - `M365_POWERPLATFORM_*`
- Legacy `SMARTHAUS_PP_*` names remain only as compatibility fallback for local bootstrap, not as the engine contract.
- Shared Graph and Azure env aliases are no longer accepted as implicit Power Platform credentials.

That means the engine is now tenant-generic even though the current local bootstrap still supports the legacy SmartHaus variables during transition.

### `R3` deterministic workflow contract

The weekly status workflow contract is now frozen as:

- recurring weekly meeting
- tracker list with fixed status-update schema
- Friday reminder flow
- weekly digest flow

The recurrence payload, environment selection logic, and Power Automate definition envelope are all locked and covered by focused regression tests.

### `R4` live provisioning

The live reference workflow now provisions successfully.

Provisioned reference result:

- site:
  - display name: `Founding Team`
  - web url: `https://smarthausgroup.sharepoint.com/sites/FoundingTeam`
- tracker list:
  - status: `reused`
  - display name: `Codex Weekly Status Tracker`
  - list id: `582f39f9-d80c-47b6-9e74-24edefaf22f6`
  - web url: `https://smarthausgroup.sharepoint.com/sites/FoundingTeam/Lists/Codex%20Weekly%20Status%20Tracker`
- meeting:
  - status: `created`
  - subject: `Codex Weekly Status Meeting`
- reminder flow:
  - status: `created`
  - id: `27f4f6b3-83fe-47f8-ad14-0da29c61302f`
  - display name: `Codex Weekly Status - Friday reminder`
- digest flow:
  - status: `created`
  - id: `4d65d1a1-7295-4733-8418-4d0d8b22b08a`
  - display name: `Codex Weekly Status - Weekly digest`

### `R5` end-to-end validation

The live path exposed and fixed four real blockers during execution:

1. Power Platform environment payload shape differed from the helper assumptions.
2. SharePoint list creation required `Sites.Manage.All`, not the previously declared `Sites.ReadWrite.All`.
3. Graph recurring-event creation required a stricter recurrence payload shape.
4. Power Automate operator-token acquisition had to prefer the Azure tenant GUID over the tenant slug, and flow creation required the full workflow-definition envelope including `"$schema"`.

Each of those blockers is now fixed in the repo and covered by focused tests.

## Validation

Focused validation passed:

- `PYTHONPATH=src .venv/bin/pytest -q tests/test_tenant_config_powerplatform.py tests/test_sharepoint_onedrive_files_expansion_v2.py tests/test_power_automate_expansion_v2.py tests/test_team_status_workflow.py`
- result: `21 passed`

Additional focused reruns passed during the live repair loop:

- `8 passed`
- `14 passed`
- `18 passed`

Compile validation passed for the touched runtime and provisioning files.

Live repo-direct validation passed for:

- Power Platform environment visibility
- SharePoint tracker provisioning
- recurring meeting creation
- reminder-flow creation
- digest-flow creation

## Truthful Closeout

This initiative is complete.

What is now true:

- the engine-side Power Platform credential model is tenant-generic
- the repo can provision the weekly team status workflow end to end
- the workflow is backed by real tenant assets, not just contract claims
- no secrets or private keys were committed

What remains true:

- the current local bootstrap still supports legacy `SMARTHAUS_PP_*` variables as a temporary compatibility path
- tenant-specific executor configuration still belongs in tenant config outside this repo, not in hardcoded engine assumptions

## Next Act

None for this package. Any follow-on work should be a separate package, such as:

- merge this branch into `development`
- generalize the weekly workflow into broader reusable workflow packs
- add more live Power Automate scenarios beyond the team-status loop
