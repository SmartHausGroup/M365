# M365 System Capabilities and Agents

---

## 1. M365 system capabilities (in chat)

**Instruction API (CAIO / TAI flow)** — POST `/api/m365/instruction`:

| Capability | Action | Mutating | Description |
|------------|--------|----------|-------------|
| List users | `list_users` | No | List M365 users (top, select) |
| List teams | `list_teams` | No | List Teams workspaces |
| List sites | `list_sites` | No | List SharePoint site collections |
| Get user | `get_user` | No | Get one user by id or UPN |
| Reset password | `reset_user_password` | Yes | Set temp password; force change at next sign-in |
| Create site | `create_site` | Yes | Create SharePoint site with group |
| Create team | `create_team` | Yes | Create Teams workspace |
| Add channel | `add_channel` | Yes | Add channel to team |
| Provision service | `provision_service` | Yes | Provision from config by key |
| Upload file to drive | `upload_to_drive` | Yes | Upload file to any Teams site, SharePoint site (incl. communications), or OneDrive (Graph client + script; instruction action optional) |

**Other APIs:**

- **GET** `/api/m365/actions` — Instruction action schema (for dashboards/CAIO).
- **GET** `/api/m365/agents` — Agent registry from `registry/agents.yaml`.
- **GET** `/api/m365/status` — Graph connectivity, action count, mutations-allowed.
- **Health** — `/health`, `/status` (provisioning API); ops-adapter has `/health` on its port.

**Ops-adapter (policy layer):**

- Policy-checked actions via OPA (e.g. `/actions/<agent_id>/<action>`).
- Approvals queue, Teams webhook for approval cards, audit logs.

**Dashboards / UIs:**

- Simple dashboard, enterprise dashboard, agent command center, agent workstation, business operations, unified dashboard (various ports when run via Docker).

---

## 2. M365 agents — what/who they are and whether we use them

**What they are:**  
M365 “agents” in this repo are **personas/roles** defined in `registry/agents.yaml`. Each has a **name**, **department**, **risk_tier**, **allowed_actions** (list of action names), and optional **approval_rules**. They are **not** conversational AI agents; they are **identity/role definitions** used for:

1. **Ops-adapter:** When a request hits `/actions/<agent_id>/<action>`, the adapter loads the registry, checks that the agent has that action in `allowed_actions`, and (optionally) consults OPA and approval rules. So the **ops-adapter uses the registry** for policy and routing.
2. **Provisioning API:** **GET** `/api/m365/agents` returns this registry (so dashboards or CAIO can list “who” exists). The **instruction API** itself does **not** take an agent_id in the request — it just takes `action` + `params`. So for the **CAIO ↔ M365 instruction API**, we are **not** currently “using” agents in the sense of “CAIO sends agent_id”. We **are** using the registry to **expose** the list of personas (e.g. for a future dashboard or for approval routing in ops-adapter).

**Who they are (examples from `registry/agents.yaml`):**

- **m365-administrator** — Operations; users/groups/teams/sites, licenses; high risk; some actions need HR/security approval.
- **website-manager** — Deployment, content, analytics; deployment.production needs engineering-lead approval.
- **hr-generalist** — HR; onboard, offboard, policy, review; offboard needs hr-manager/department-head approval.
- **outreach-coordinator** — Communication; email, meeting, campaign; bulk email >100 recipients needs marketing-lead approval.
- **project-manager**, **platform-manager**, **teams-manager** — Projects, provisioning, Teams.
- **it-operations-manager**, **website-operations-specialist** — IT ops, website/CDN/DNS.
- **email-processing-agent**, **calendar-management-agent**, **project-coordination-agent**, **client-relationship-agent**, **compliance-monitoring-agent**, **recruitment-assistance-agent**, **financial-operations-agent**, **knowledge-management-agent** — Various departments with allowed_actions and approval_rules.
- **Engineering:** ai-engineer, backend-architect, devops-automator, frontend-developer, etc. (many with empty allowed_actions).
- **Marketing, design, etc.** — More roles, some with empty allowed_actions.

**Summary:**  
We **are** using the agents in the **ops-adapter** (policy + approvals). We **expose** them via **GET /api/m365/agents** for the provisioning/dashboard side. The **instruction API** used by CAIO does **not** require an agent_id; it is a single API that executes actions. So “M365 agents” = registry of personas/roles used for policy and visibility; the instruction API is agent-agnostic.

**Design note (personas as real roles, edge contract for VFE):**  
See **`docs/PERSONAS_AGENTS_AND_CAIO_EDGE.md`**. Personas should map to real subsets of the M365 capability set \(\mathcal{O}\); the contract on the edge (agent ↔ CAIO) is the **entire response** so it can be handed off to VFE and the person is “talking back” to the user. Not yet implemented — captured for when we do it.
