# SMARTHAUS M365 Capability Taxonomy and Feasibility Map

## Purpose

Turn the locked workload-family inventory into one canonical taxonomy that later phases can implement, route, certify, and commercialize without blurring together feasibility, licensing, API exposure, and auth posture.

## Inputs

- locked roster: [m365-department-persona-census.md](/Users/smarthaus/Projects/GitHub/M365/docs/commercialization/m365-department-persona-census.md)
- locked workload-family inventory: [m365-workload-universe-inventory.md](/Users/smarthaus/Projects/GitHub/M365/docs/commercialization/m365-workload-universe-inventory.md)
- prior auth/API framing: [m365-capability-api-license-auth-matrix.md](/Users/smarthaus/Projects/GitHub/M365/docs/commercialization/m365-capability-api-license-auth-matrix.md)
- repo runtime surface: `registry/agents.yaml` with `184` distinct allowed actions

## Core Rule

Every future capability must be classified across **five separate axes**:

1. workload family
2. capability family
3. implementation status
4. feasibility class
5. auth and licensing class

No later phase may use the phrase “supported” unless all five axes are explicit.

## Taxonomy Values

### Implementation status

- `certified-core`
  - implemented and already live-certified in the bounded standalone v1 surface
- `registry-backed`
  - represented in `registry/agents.yaml` but not yet certified or fully runtime-implemented
- `docs-backed`
  - represented in repo docs or planned architecture but not yet materially implemented
- `planned-only`
  - required by the workforce target but not yet represented in runtime or concrete docs

### Feasibility class

- `implemented-now`
  - already operational in the repo/runtime
- `feasible-graph`
  - primarily achievable through Microsoft Graph or existing repo patterns
- `feasible-mixed-api`
  - requires Graph plus another Microsoft-native API/admin surface
- `delegated-sensitive`
  - feasible, but some operations will likely require delegated user context for correctness or safety
- `template-or-workflow-driven`
  - feasible mainly through file/template/workflow composition rather than one clean CRUD API
- `tenant-or-license-dependent`
  - feasible only when the specific tenant product, entitlement, or admin configuration exists

### Auth class

- `app-only`
  - bounded executor can safely own the capability
- `delegated`
  - user context should be primary
- `hybrid`
  - some actions fit app-only while others require delegated user context
- `mixed`
  - capability family spans multiple subpatterns and must be split later

### Licensing class

- `core-m365`
  - broadly aligned with core Microsoft 365 licensing
- `workload-specific`
  - tied to one specific workload or add-on family
- `premium-admin-security`
  - typically tied to security, compliance, or admin-entitlement surfaces
- `power-platform`
  - tied to Power Platform / analytics entitlements
- `tenant-config-dependent`
  - availability depends on tenant enablement or product rollout, not just a user license

## Canonical Taxonomy

| Workload family | Capability family | Representative repo surface | Implementation status | Feasibility class | Auth class | Licensing class | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Identity, directory, and tenant administration | user lifecycle, groups, org metadata, roles, domains, licensing, service principals | `users.*`, `groups.*`, `directory.*`, `licenses.assign`, `apps.*`, `service_principals.list`, `reports.users_active`, `health.*` | `registry-backed` with a certified core subset | `feasible-graph` plus some `delegated-sensitive` admin edges | `hybrid` | `core-m365` plus `premium-admin-security` edges | strong admin and approval posture required |
| Mail, calendar, contacts, and bookings | mailbox operations, mail send/read, scheduling, reminders, shared mailbox work, contact surfaces | `mail.*`, `email.*`, `calendar.*`, `meeting.*`, `availability.check` | `registry-backed` | `feasible-graph` with delegated-sensitive user-context operations | `hybrid` | `core-m365` | some mailbox actions are safer or more correct with delegated user context |
| Collaboration, meetings, and communities | Teams, chats, channels, meetings, groups-backed workspaces, collaboration messaging | `teams.*`, `channels.*`, `chat.*`, `create-workspace`, `add-workspace-members`, `create-channels` | `registry-backed` with a certified core subset | `feasible-graph` | `app-only` for many admin tasks, `hybrid` overall | `core-m365` | community/Viva Engage style surfaces remain split and may need mixed treatment |
| Content, intranet, and files | sites, lists, libraries, files, drives, permissions, upload/share, content indexing | `sites.*`, `lists.*`, `files.*`, `drives.*`, `document.index`, `content.*`, current approvals backend | `registry-backed` with a certified core subset | `feasible-graph` plus some `feasible-mixed-api` file/content paths | `hybrid` | `core-m365` | this family already anchors approvals and site provisioning |
| Tasks, scheduling, and work management | Planner, task assignment, plan/bucket management, project/task orchestration, approvals and work queues | `task.*`, `create_plan`, `list_plans`, `create_bucket`, `list_buckets`, `create_task`, `deadline.track`, `status.update`, `report.generate` | `registry-backed` | `feasible-graph` and `feasible-mixed-api` | `hybrid` | `workload-specific` | approvals and tasking need later boundary cleanup to avoid concept drift |
| Documents, notes, and workspace productivity | document generation, workbook changes, presentations, notes, collaborative productivity objects | deterministic DOCX/XLSX/PPTX generation plus file-backed upload/runtime surface | `registry-backed` | `implemented-now` | `hybrid` | `core-m365` and `tenant-config-dependent` | bounded Office generation is real now; richer editing and collaborative authoring remain later |
| Knowledge, search, and employee experience | search, knowledge indexing, recommendations, training, employee-experience surfaces | `search.optimize`, `training.recommend`, `expert.connect`, broad Viva-style target from workload inventory | `docs-backed` with light registry hints | `feasible-mixed-api` and `tenant-or-license-dependent` | `mixed` | `workload-specific` and `tenant-config-dependent` | broad employee-experience surfaces are real but unevenly exposed |
| Low-code, workflow, and analytics | Power Automate, Power Apps, Power BI, Forms, connector-backed orchestration | repo docs reference Power Apps/Power BI; explicit phase targets `E3A`..`E3E` | `docs-backed` | `feasible-mixed-api` and `tenant-or-license-dependent` | `mixed` | `power-platform` | important to the vision, but not the same clean Graph-only story |
| Security, compliance, and data governance | alerts, incidents, secure score, audits, remediation, compliance checks, policy validation, retention/eDiscovery-style controls | `security.*`, `audit.*`, `compliance.check`, `policy.validate`, `remediation.plan`, `violation.report` | `registry-backed` with partial audit runtime already present | `feasible-graph` plus `tenant-or-license-dependent` admin surfaces | `app-only` and `delegated-sensitive` split by risk | `premium-admin-security` | highest governance burden in the workforce target |
| Devices, endpoint management, and adjacent Windows admin surfaces | managed devices, compliance, device actions, health checks, infrastructure scan ties | `devices.*`, `system.health-check`, `infrastructure.monitor`, `backup.*` | `registry-backed` | `feasible-graph` plus `feasible-mixed-api` | `app-only` and `hybrid` mix | `workload-specific` and `premium-admin-security` | some edges are Microsoft 365 adjacent rather than pure Graph |
| Media, publishing, and extended communications | publishing, media, storytelling, stream/sway-style outputs, campaign content surfaces | `campaign.create`, `content.create`, `content.update`, `seo.update`, doc references to Stream/Sway | `docs-backed` with light registry hints | `template-or-workflow-driven` and `tenant-or-license-dependent` | `mixed` | `workload-specific` | broad brand/publishing flows need later content model work |

## Current Baseline Classification

### What is real now

- `certified-core`
  - the previously shipped bounded `9`-action standalone surface

### What is broader than v1 but already present in the repo

- `registry-backed`
  - identity/admin
  - mail/calendar
  - collaboration
  - content/files
  - tasks/work management
  - documents/notes/productivity
  - security/compliance
  - devices/admin-adjacent operations

### What is named in architecture but still mostly doc-level

- `docs-backed`
  - knowledge/search/employee experience
  - Power Platform / analytics / forms
  - media/publishing/extended communications

## What E0C Resolves

`E0C` resolves the core ambiguity behind “anything in M365”:

- it is **not** one giant undifferentiated capability bucket
- it is **not** enough to say something is licensed
- it is **not** enough to say something exists in Microsoft Graph

Instead, every later capability must now be treated as:

`Capability = WorkloadFamily × CapabilityFamily × ImplementationStatus × FeasibilityClass × AuthClass × LicensingClass`

## What E0C Does Not Yet Resolve

This act still does **not** decide:

- which personas need which capability families
- which approval tiers map to which capability families
- which exact executor domain owns each capability family
- which specific actions form the canonical action universe

Those are next:

- `E0D` for persona-to-capability and risk mapping
- `E1` for action contract, auth model, executor routing, and unified audit

## Next Dependency

`E0D` is now the next act. It must bind the locked roster from `E0A` and the capability taxonomy from `E0C` into one department/persona-to-capability map with explicit risk and approval posture.
