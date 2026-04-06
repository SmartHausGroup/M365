# M365 Direct Function Validation

## Result

The bounded direct-function-validation package is complete.

The repo-local M365 runtime is now directly testable for specific function families without tripping on known local import, routing, or harness defects. The validation wave did not expose any new repo-local defects.

## What Worked Directly

### Instruction surface

- `list_sites`
- `list_teams`

### Governed action surface

- `ucp-administrator / admin.get_tenant_config`
- `teams-manager / teams.list`
- `m365-administrator / sites.get`

## What Failed for External Reasons

- Email:
  - `list_messages`
  - `mail.list`
  - Current boundary: Microsoft Graph `ErrorAccessDenied`
- Calendar:
  - `list_events`
  - `calendar.availability`
  - Current boundary: Microsoft Graph `ErrorAccessDenied`
- Power Apps:
  - `list_powerapp_environments`
  - Current boundary: local machine missing `Microsoft.PowerApps.Administration.PowerShell`
- Power Automate:
  - `list_flows_admin`
  - Current boundary: local machine missing `Microsoft.PowerApps.Administration.PowerShell`
- Service health:
  - `health.overview`
  - Current boundary: Microsoft Graph `UnknownError`

## Meaning

This repo is now in the state the user asked for: direct function tests can be requested and executed from the repo version itself.

That does not mean every live M365 function is green yet. It means the remaining failures are now truthful tenant or workstation prerequisites rather than broken local code.

## Next Dependency Boundary

Any further advance now requires one of two separate acts:

- external enablement:
  - tenant permissions for mail and calendar
  - local Power Apps / Power Automate admin PowerShell modules
  - Microsoft service-health surface access
- or a separate governed write-path test plan if the next request is to perform live mutations such as sending mail or creating meetings instead of read-only or safe validation

