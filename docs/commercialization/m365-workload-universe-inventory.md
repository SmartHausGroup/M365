# SMARTHAUS M365 Workload Universe Inventory

## Purpose

Define the full workload universe the SMARTHAUS workforce program must eventually cover so later phases can build against an explicit boundary instead of growing the action surface ad hoc.

## Authority and Source Anchors

This inventory is grounded in:

- the locked roster at [m365-department-persona-census.md](/Users/smarthaus/Projects/GitHub/M365/docs/commercialization/m365-department-persona-census.md)
- the current repo action surface in `registry/agents.yaml` with `184` distinct allowed actions
- official Microsoft references:
  - [Microsoft Graph overview](https://learn.microsoft.com/en-us/graph/overview)
  - [Microsoft 365 and Office 365 platform service description](https://learn.microsoft.com/en-us/office365/servicedescriptions/office-365-platform-service-description/office-365-platform-service-description)
  - [Office 365 app suite in Conditional Access](https://learn.microsoft.com/en-us/entra/identity/conditional-access/reference-office-365-application-contents)
  - [Product names and service plan identifiers for licensing](https://learn.microsoft.com/en-us/entra/identity/users/licensing-service-plan-reference)

The workload families below are an inference from those official sources plus the repo’s current runtime and registry surfaces.

## Inventory Rule

A workload family belongs in the workforce universe if it is:

- part of Microsoft 365 or a first-party Microsoft admin/control surface used to operate Microsoft 365
- relevant to corporate work, administration, governance, reporting, or content production
- licensable, exposable, or governable through Microsoft APIs, Microsoft admin surfaces, or adjacent first-party integration paths

## Locked Workload Families

| Workload family | Representative services | Why it is in scope | Current repo baseline | Planned follow-up |
| --- | --- | --- | --- | --- |
| Identity, directory, and tenant administration | Entra ID, users, groups, domains, service principals, licensing, org settings, activity reports, service health | Microsoft Graph includes identity and access services; Microsoft 365 service descriptions include account management and reports | Certified subset plus broader registry/admin coverage | `E2A`, `E4D`, `E4E` |
| Mail, calendar, contacts, and bookings | Exchange Online, Outlook, calendar, people/contacts, shared mailbox operations, Bookings | Microsoft Graph includes calendar, Outlook/Exchange, and people; Microsoft 365 service descriptions include Bookings | Registry-present, not yet expanded beyond the standalone core | `E2B` |
| Collaboration, meetings, and communities | Teams, chats, channels, meetings, Microsoft 365 Groups, Viva Engage/community surfaces | Microsoft Graph includes Teams; Conditional Access Office 365 reference includes Teams and Groups services | Certified subset plus broader registry coverage | `E2D`, `E7` |
| Content, intranet, and files | SharePoint Online, OneDrive, sites, pages, lists, libraries, files, permissions | Microsoft Graph includes SharePoint and OneDrive | Certified subset plus broader registry coverage | `E2C` |
| Tasks, scheduling, and work management | Planner, To Do, Project for the web, approvals, scheduling surfaces | Microsoft Graph includes Planner and To Do; service descriptions include Project for the web | Registry-present, not yet certified | `E2D`, `E3D` |
| Documents, notes, and workspace productivity | Word, Excel, PowerPoint, OneNote, Loop | Microsoft Graph includes Excel and OneNote; Microsoft 365 service descriptions cover Office apps; Conditional Access reference includes Loop | Mostly unmodeled beyond file substrate | `E2E` |
| Knowledge, search, and employee experience | Microsoft Search, Delve/People Skills, Viva Insights, broader Viva surfaces | Microsoft Graph includes Microsoft Search and Viva Insights; service descriptions include People Skills and Viva items | Mostly unmodeled | `E2E`, `E5`, `E7` |
| Low-code, workflow, and analytics | Power Automate, Power Apps, Forms, Power BI, connector-backed automation | Microsoft 365 service descriptions include Power Automate, Power Apps, Forms, and Power BI-related availability; repo docs already reference Power Apps and Power BI | Docs-present, limited runtime implementation | `E3A` through `E3E` |
| Security, compliance, and data governance | Defender, Purview, eDiscovery, audit, retention, DLP, Secure Score | Microsoft Graph includes security and compliance services; Microsoft 365 service descriptions include Purview and Defender features | Registry-present, partially implemented audit/admin evidence | `E4B`, `E4C` |
| Devices, endpoint management, and adjacent Windows admin surfaces | Intune, device compliance, device actions, app protection, Universal Print where relevant | Microsoft Graph includes devices and Intune-related services; Microsoft 365 service descriptions include Intune | Registry-present, not yet implemented | `E4A` |
| Media, publishing, and extended communications | Stream, Sway, media publishing, broader publishing surfaces | Microsoft 365 service descriptions include Stream and Sway | Mostly unmodeled | `E6C`, `E9A` |

## What E0B Does Not Lock

This act does **not** yet normalize:

- capability-by-capability action taxonomy
- exact auth posture per capability
- exact licensing gate per capability
- executor-domain assignment per capability

Those are the next acts:

- `E0C` for capability taxonomy and feasibility mapping
- `E0D` for persona-to-capability and risk mapping
- `E1` for control-plane, auth, routing, and audit normalization

## Current Repo Baseline

- Certified standalone v1 surface: the previously completed bounded `9`-action release
- Registry action surface: `184` distinct allowed actions in `registry/agents.yaml`
- Workload coverage reality: broad registry and doc hints exist, but the runtime and certification surface still cover only a narrow subset of the full workload universe above

## Result

The workload universe is now locked at the family level. The program will not treat “anything in M365” as a vague slogan anymore; it now has an explicit workload map that later acts must normalize, implement, route, certify, and release.

## Next Dependency

`E0C` is now the next act. It must turn this workload-family inventory into a canonical capability taxonomy with feasibility, licensing, API, and auth normalization.
