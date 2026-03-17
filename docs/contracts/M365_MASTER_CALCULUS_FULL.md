# M365 Master Calculus — Full Capability Surface

**Purpose:** Define a **master equation** and the **full set of operations** that constitute "everything we can do" to manage M365 in any way—Azure AD/Entra, SharePoint, Teams, OneDrive, Mail, Calendar, Planner, and every other resource exposed by the Microsoft 365 platform. The math is then the single source of truth for what the M365 agent can do; every implemented command must map into this surface.

**Sources (Microsoft Learn):**

- [Microsoft 365 developer documentation](https://learn.microsoft.com/en-us/microsoft-365/developer/?view=o365-worldwide) — Platform overview, Copilot extensibility, Teams, Graph, SharePoint, Power Apps.
- [Microsoft Graph REST API v1.0](https://learn.microsoft.com/en-us/graph/api/overview?view=graph-rest-1.0) — User-centric and group-centric use cases; endpoint pattern `https://graph.microsoft.com/v1.0/{resource}`.
- [Microsoft Graph permissions reference](https://learn.microsoft.com/en-us/graph/permissions-reference) — **Canonical list** of delegated and application permissions; pattern `{Resource}.{Operation}.{Constraint}` (e.g. `User.Read`, `Files.ReadWrite.All`, `Sites.ReadWrite.All`). This page (and the programmatic read via `GET .../servicePrincipals(appId='00000003-0000-0000-c000-000000000000')?$select=...,appRoles,oauth2PermissionScopes,resourceSpecificApplicationPermissions`) defines the **max capability** over Graph.
- [Overview of Microsoft Graph permissions](https://learn.microsoft.com/en-us/graph/permissions-overview) — Delegated vs application; naming pattern; RSC.
- [Microsoft Teams developer platform](https://learn.microsoft.com/en-us/microsoftteams/platform/overview?view=msteams-client-js-latest) — Agents and apps in Teams; deployment across Teams, Outlook, M365; [RSC permissions](https://learn.microsoft.com/en-us/microsoftteams/platform/graph-api/rsc/resource-specific-consent).
- [SharePoint developer documentation](https://learn.microsoft.com/en-us/sharepoint/dev/) — SPFx, SharePoint Embedded, sites and content via Graph, REST, webhooks.
- [SharePoint sites and content API (Graph)](https://learn.microsoft.com/en-us/graph/sharepoint-concept-overview) — Sites, lists, document libraries (drive), team sites, communications sites.

---

## 1. Master equation (full M365)

Let:

- **\(\mathcal{O}\)** = the set of all **M365 operations** that are definable and authorized over the platform API surface (Graph, Teams, SharePoint). An operation is a (resource, action, scope) triple—e.g. (driveItem, upload, group), (user, resetPassword, tenant)—subject to the permissions granted to the app and to policy.
- **\(\mathcal{P}\)** = the pipeline that wraps execution: AuthGate ∘ IdempotencyLookup ∘ Execute ∘ Audit (as in the [CAIO-M365 master calculus](caio-m365/M365_MASTER_CALCULUS.md)).

Then the **master equation** for full M365 management is:

\[
\boxed{
  \forall \,\text{request } R \colon \;
  \texttt{action}(R) \in \mathcal{O}
  \;\Rightarrow\;
  S = \mathcal{P}(R)
  \;\wedge\;
  \mathtt{ok}(S) \Rightarrow \mathtt{shape}(\mathtt{result}(S)) \in \mathcal{S}_{\texttt{action}(R)}
  \;\wedge\;
  \text{(idempotency, auth, audit as in Eq. 3--5)}.
}
\]

**In words:** Every request whose action is in the full operation set \(\mathcal{O}\) is processed by the same pipeline and satisfies the same postconditions (result shape, idempotency when keyed, auth when required, audit when enabled). **No operation outside \(\mathcal{O}\)** is executable by the agent. To "fully manage M365 in any way shape or form," we must **define \(\mathcal{O}\)** to be the maximal set of operations that the platform allows (Graph + Teams + SharePoint) and then implement or stub each member so the agent can do literally every command.

---

## 2. API surface (what defines \(\mathcal{O}\))

The **authorized API surface** is the union of:

| Surface | Scope | How to enumerate |
|--------|--------|-------------------|
| **Microsoft Graph (v1.0 + beta)** | Users, groups, teams, sites, drive/driveItem, mail, calendar, planner, applications, directory, access reviews, agents, etc. | [Graph permissions reference](https://learn.microsoft.com/en-us/graph/permissions-reference): every `{Resource}.{Operation}.{Constraint}` maps to one or more API operations (Read, ReadWrite, Create, Delete, etc.). [Graph API overview](https://learn.microsoft.com/en-us/graph/api/overview?view=graph-rest-1.0): resources and use cases. |
| **Teams** | Teams, channels, messages, tabs, RSC, Agents in Teams. | Graph: `/teams`, `/groups/{id}/team`, channels, messages. [Teams platform](https://learn.microsoft.com/en-us/microsoftteams/platform/overview); [RSC permissions](https://learn.microsoft.com/en-us/microsoftteams/platform/graph-api/rsc/resource-specific-consent). |
| **SharePoint** | Sites, lists, list items, document libraries (drive), pages. | Graph: [SharePoint API](https://learn.microsoft.com/en-us/graph/api/resources/sharepoint) (sites, lists, drive); [SharePoint concept](https://learn.microsoft.com/en-us/graph/sharepoint-concept-overview). Also SharePoint REST, webhooks, SPFx for custom UI. |
| **OneDrive** | User and group drives; file/folder CRUD. | Graph: `/users/{id}/drive`, `/groups/{id}/drive`, `/sites/{id}/drive`; driveItem [put content](https://learn.microsoft.com/en-us/graph/api/driveitem-put-content). |

So:

\[
\mathcal{O} = \mathcal{O}_{\mathrm{Graph}} \cup \mathcal{O}_{\mathrm{Teams}} \cup \mathcal{O}_{\mathrm{SharePoint}} \cup \mathcal{O}_{\mathrm{Drive}},
\]

where each \(\mathcal{O}_*\) is derived from the corresponding permissions and API reference (see §4).

---

## 3. Capability domains (from Learn and permissions reference)

From the [Graph API overview](https://learn.microsoft.com/en-us/graph/api/overview?view=graph-rest-1.0) and [permissions reference](https://learn.microsoft.com/en-us/graph/permissions-reference), the following **domains** partition the set of resources and operations. Each domain corresponds to a family of permissions and API resources; the full list of permissions under each is in the permissions reference (and can be ingested programmatically).

| Domain | Resources / areas | Example permissions / operations |
|--------|-------------------|-----------------------------------|
| **Identity / Directory** | User, Application, ServicePrincipal, Group, Device, AdministrativeUnit, DirectoryRole | User.Read.All, User.ReadWrite.All, Group.ReadWrite.All, Directory.ReadWrite.All |
| **Access & governance** | AccessReview, EntitlementManagement, PrivilegedAccess | AccessReview.ReadWrite.All, Agreement.Read.All |
| **Agents** | AgentCard, AgentIdentity, AgentInstance, AgentCollection | AgentCard.ReadWrite.All, AgentIdentity.ReadWrite.All |
| **Teams** | Team, Channel, Chat, Message, Tab; RSC | Team.ReadWrite.All, Channel.ReadWrite.All, ChannelMessage.Read.All |
| **SharePoint / Sites** | Site, List, ListItem, Drive (document library) | Sites.ReadWrite.All, Sites.FullControl.All |
| **Drive / Files** | Drive, DriveItem (group, site, user) | Files.ReadWrite.All, Files.ReadWrite.AppFolder |
| **Mail** | Message, Mailbox, MailFolder | Mail.ReadWrite, Mail.Send, MailboxSettings.ReadWrite |
| **Calendar** | Event, Calendar, Schedule | Calendars.ReadWrite, OnlineMeetings.ReadWrite |
| **Planner** | Plan, Task, Bucket | Tasks.ReadWrite, Group.ReadWrite.All (for group plans) |
| **OneNote** | Notebook, Section, Page | Notes.ReadWrite.All |
| **Reports / Analytics** | Report, Activity | Report.Read.All, Analytics.Read |
| **Security** | IdentityProtection, ThreatAssessment | (see permissions reference) |
| **Compliance** | eDiscovery, Retention | (see permissions reference) |
| **Other** | OrgContact, Subscription, SchemaExtensions, etc. | (see permissions reference) |

**Teams-specific (RSC):** [Resource-specific consent](https://learn.microsoft.com/en-us/microsoftteams/platform/graph-api/rsc/resource-specific-consent) adds scoped permissions per team/chat; these extend \(\mathcal{O}_{\mathrm{Teams}}\).

**SharePoint (beyond Graph):** [SharePoint REST](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/get-to-know-the-sharepoint-rest-service), [webhooks](https://learn.microsoft.com/en-us/sharepoint/dev/apis/webhooks/overview-sharepoint-webhooks), and [SPFx](https://learn.microsoft.com/en-us/sharepoint/dev/spfx/sharepoint-framework-overview) add operations that may not be 1:1 with Graph permissions; they still belong in \(\mathcal{O}\) when we intend to support them.

---

## 4. Ingesting max capability (building \(\mathcal{O}\) in practice)

To make \(\mathcal{O}\) **literal and complete**:

1. **Graph permissions (canonical list)**  
   Call Microsoft Graph (with an app that has `Application.Read.All` or equivalent):
   ```http
   GET https://graph.microsoft.com/v1.0/servicePrincipals(appId='00000003-0000-0000-c000-000000000000')?$select=id,appId,displayName,appRoles,oauth2PermissionScopes,resourceSpecificApplicationPermissions
   ```
   Parse `appRoles` (application permissions) and `oauth2PermissionScopes` (delegated). Each permission has a **value** (e.g. `Files.ReadWrite.All`) that maps to a **resource** and **operation**. Use the [permissions reference](https://learn.microsoft.com/en-us/graph/permissions-reference) as the human-readable source; the API gives the same list programmatically. Enumerate every permission and map it to one or more **commands** (e.g. `Files.ReadWrite.All` → upload, create, update, delete on driveItem).

2. **Graph API reference (resource + method)**  
   For each resource (user, group, team, site, drive, driveItem, message, event, etc.), the [Graph API reference](https://learn.microsoft.com/en-us/graph/api/overview?view=graph-rest-1.0) lists HTTP methods (GET, POST, PUT, PATCH, DELETE). Cross-map: (resource, method) → required permission(s). That yields the full set of **API operations**; our \(\mathcal{O}\) is the set of (action name, params, result shape) we expose, each backed by one or more Graph (or Teams/SharePoint) calls.

3. **Teams RSC and platform**  
   Add [RSC permissions](https://learn.microsoft.com/en-us/microsoftteams/platform/graph-api/rsc/resource-specific-consent) and any Teams-specific APIs (e.g. [Agents in Teams](https://learn.microsoft.com/en-us/microsoftteams/platform/agents-in-teams/overview)) so \(\mathcal{O}_{\mathrm{Teams}}\) is complete.

4. **SharePoint**  
   [SharePoint sites and content](https://learn.microsoft.com/en-us/graph/sharepoint-concept-overview) in Graph (sites, lists, drive) are already covered by Graph permissions (Sites.*, Files.*). Add SharePoint REST or SPFx operations only if we expose them as agent commands.

5. **Single master list**  
   Produce a **registry** (e.g. YAML or JSON): for each operation in \(\mathcal{O}\), store action name, resource, required permissions, parameter schema, result shape, and mutating flag. The CAIO-M365 [ACTION_SPECIFICATION](caio-m365/ACTION_SPECIFICATION.md) and [MATHEMATICS](caio-m365/MATHEMATICS.md) then reference this registry so that every implemented action is part of the master equation.

   **Implemented:** The canonical registry is **`registry/capability_registry.yaml`**. It lists every action in \(\mathcal{O}\) with `status: implemented` or `status: planned`. Ingest script: **`scripts/ci/ingest_graph_permissions.py`** (run with `--live` when Graph auth env is set to fetch full permissions; without auth it emits a static subset). Verification: **`scripts/ci/verify_capability_registry.py`** asserts that every implemented action in the contract appears in the registry with `status: implemented` and writes `configs/generated/capability_registry_verification.json`.

---

## 5. Relation to the existing CAIO-M365 calculus

The [CAIO-M365 master calculus](caio-m365/M365_MASTER_CALCULUS.md) defines the **pipeline** and **response guarantees** (Eq. 1–5) for the **instruction API**. The **set of actions** in that calculus is currently the small set \(\mathcal{A}\) in [ACTION_SPECIFICATION](caio-m365/ACTION_SPECIFICATION.md) (list_users, create_team, etc.).

This document **extends** the scope:

- **Master equation (full):** \(\mathcal{O}\) is the **entire** set of operations we can ever support (everything possible over Graph, Teams, SharePoint). The pipeline \(\mathcal{P}\) and the postconditions (result shape, idempotency, auth, audit) apply to **any** action in \(\mathcal{O}\) once implemented.
- **Implementation:** We implement actions in **phases**. Each implemented action must be in \(\mathcal{O}\), have a parameter schema and result shape in the registry, and be wired through \(\mathcal{P}\). So we build toward "literally every command" by (1) defining \(\mathcal{O}\) from the permissions reference and API surface above, (2) maintaining the master registry, and (3) implementing and documenting each action so it satisfies the master equation.

---

## 6. Full enumeration of \(\mathcal{O}\) (master calculus for all)

**\(\mathcal{O}\) is fully enumerated.** The canonical list is:

- **Registry:** `registry/capability_registry.yaml` — every action with action name, resource, domain, required_permissions, mutating, status (implemented | planned). Built from the universe list; run `scripts/ci/build_capability_registry.py` to regenerate from `M365_CAPABILITIES_UNIVERSE.md`.
- **Universe list:** `M365_CAPABILITIES_UNIVERSE.md` — human-readable list of all capabilities.
- **Master calculus for all actions:** `M365_MASTER_CALCULUS_ACTIONS.md` — defines \(\mathcal{O}\), \(\mathcal{O}_m\), and \(\mathcal{S}_{\texttt{action}}\) (or TBD) for every action; states that the master equation applies to all 260.

**Count:** 9 implemented, 251 planned = **260 total in \(\mathcal{O}\)**. The master equation and pipeline \(\mathcal{P}\) apply to every one.

---

## 7. Summary

| Item | Description |
|------|-------------|
| **Master equation** | Every request with \(\texttt{action}(R) \in \mathcal{O}\) is processed by \(\mathcal{P}\) and satisfies postcondition, idempotency, auth, audit. No operation outside \(\mathcal{O}\) is executable. |
| **\(\mathcal{O}\)** | 260 actions (registry); union of Graph, Teams, SharePoint, Drive, Mail, Calendar, etc. from [Graph permissions reference](https://learn.microsoft.com/en-us/graph/permissions-reference) + API overview + [Teams](https://learn.microsoft.com/en-us/microsoftteams/platform/overview) + [SharePoint](https://learn.microsoft.com/en-us/sharepoint/dev/). |
| **Per-action calculus** | See `M365_MASTER_CALCULUS_ACTIONS.md`: mutating and \(\mathcal{S}_{\texttt{action}}\) for every action; implemented have full result shapes, planned have TBD until specified. |
| **References** | All links above point to [Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-365/developer/?view=o365-worldwide); the permissions reference is the canonical list for Graph; Teams and SharePoint docs extend the surface. |

This gives a **master calculus for the full universe**: one equation, one pipeline, and a defined (or TBD) result shape for every one of the 260 capabilities.
