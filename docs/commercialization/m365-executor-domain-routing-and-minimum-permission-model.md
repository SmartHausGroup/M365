# M365 Executor-Domain Routing and Minimum-Permission Model

## Purpose

Replace the single giant executor target with a bounded executor-domain architecture.

## Decision

SMARTHAUS should use a small set of bounded executor domains, not one god-mode executor and not one app per persona.

## Recommended Domain Split

### Operator Identity App

- purpose: human Entra login only
- not the app-only Microsoft executor

### SharePoint / Files Executor

- approvals
- sites, lists, libraries
- document storage and file workflows

### Collaboration Executor

- Teams
- groups
- Planner
- channels

### Messaging / Calendar Executor

- mail
- calendar
- communications workflows

### Directory / Admin Executor

- users
- licenses
- directory administration

### Power Platform / Analytics Executor

- Power Automate
- Power Apps
- Power BI
- only when that surface is explicitly in scope

## Routing Rule

Every governed action must map deterministically to one executor domain.

`Executor(action) -> exactly_one_domain`

No action may fan out into ambiguous app selection.

## Permission Rule

Each executor domain must target the minimum viable permission envelope for its supported actions.

The product must avoid:

- tenant-wide god-mode permissions where narrower domain permissions are sufficient
- token bloat from irrelevant Microsoft Graph roles
- certification against a permission posture broader than the supported surface

## Long-Term SharePoint Rule

The approvals backend belongs to the SharePoint / Files executor.

This domain should be the first proof point for narrow routing, bounded permissions, and stable certification.

## Active v1 Runtime State After B7D

`B7D` turns the bounded-executor model from a recommendation into the live
SMARTHAUS runtime contract.

The active split is now:

- `SMARTHAUS M365 Operator Identity` (`e6fd71d3-4116-401e-a4f1-b2fda4318a8b`)
  for human Entra sign-in and API audience only.
- `SMARTHAUS SharePoint Executor`
  (`fe34434f-0de8-4807-a239-9ee093d4780c`) for approvals and SharePoint-backed
  workflows.
- `SMARTHAUS Collaboration Executor`
  (`98826c42-1dd6-47c8-8353-7f1e539f89bc`) for Teams and group-backed
  collaboration workflows.
- `SMARTHAUS Directory Executor`
  (`f1aba812-90b1-4d5f-9204-c7d61e7680bb`) for user and directory operations.

The previous monolithic executor app
`720788ac-1485-4073-b0c8-1a6294819a87` is no longer the active default and is
now explicitly demoted to `SMARTHAUS Legacy M365 Executor`.

The active tenant contract outside the repo now projects:

- `default_executor = sharepoint`
- `approvals -> sharepoint`
- `sharepoint -> sharepoint`
- `collaboration -> collaboration`
- `directory -> directory`

## Active v1 Permission Matrix

| Domain | Live app registration | Supported v1 actions | Minimum Graph application roles |
| --- | --- | --- | --- |
| `sharepoint` | `SMARTHAUS SharePoint Executor` (`fe34434f-0de8-4807-a239-9ee093d4780c`) | `list_sites`, `create_site`, `provision_service`, approval-backend access | `Sites.Read.All`, `Sites.ReadWrite.All`, `Group.ReadWrite.All` |
| `collaboration` | `SMARTHAUS Collaboration Executor` (`98826c42-1dd6-47c8-8353-7f1e539f89bc`) | `list_teams`, `create_team`, `add_channel`, Teams leg of `provision_service` | `Team.ReadBasic.All`, `Team.Create`, `Channel.Create`, `Group.ReadWrite.All` |
| `directory` | `SMARTHAUS Directory Executor` (`f1aba812-90b1-4d5f-9204-c7d61e7680bb`) | `list_users`, `get_user`, `reset_user_password` | `User.Read.All`, `User.ReadWrite.All` |

## Runtime Projection Rule

The bounded runtime now projects executor identity in the provisioning and
instruction surfaces, not only in the ops-adapter path.

- `src/provisioning_api/routers/m365.py` projects directory, collaboration, and
  SharePoint actions to their bounded executors before constructing
  `GraphClient`.
- `src/provisioning_api/m365_provision.py` projects SharePoint site/group
  creation to the SharePoint executor and Teams workspace creation to the
  collaboration executor.

This keeps the v1 instruction and provisioning surfaces aligned with the same
bounded executor contract that already governs approvals and persona-aware
delegation.

## Validation Rule

`B7D` is only green if each bounded executor proves one representative app-only
Graph route with the exact active role set and the live tenant contract no
longer defaults to the legacy monolithic executor.

For the live SMARTHAUS state proved in `B7D`:

- SharePoint executor returns `200` on the approvals list probe.
- Collaboration executor returns `200` on the Teams listing probe.
- Directory executor returns `200` on the users listing probe.

Messaging/calendar and Power Platform/analytics remain planned executor domains,
not active v1 runtime domains, until their supported surfaces are implemented
and bound to real permissions.
