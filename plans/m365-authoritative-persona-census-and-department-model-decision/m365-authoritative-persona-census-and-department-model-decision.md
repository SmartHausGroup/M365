# Plan: M365 Authoritative Persona Census and Department-Model Decision

**Plan ID:** `m365-authoritative-persona-census-and-department-model-decision`
**Parent Plan ID:** `m365-authoritative-persona-humanization-expansion`
**Status:** 🟠 Draft
**Date:** 2026-04-05
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-authoritative-persona-census-and-department-model-decision:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — preserve truthful workforce claims by keeping the current `39`-persona / `10`-department authority explicit until the `20` extra agents are deliberately evaluated, mapped, and approved.
**Canonical predecessor:** `plans/m365-authoritative-persona-humanization-expansion/m365-authoritative-persona-humanization-expansion.md`

**Draft vs Active semantics:** This child plan starts in **Draft**. It transitions to **Active** only when (1) the operator presents the approval packet and receives an explicit "go", and (2) no other child phase in the parent initiative is concurrently active. It transitions to **Complete** only after its own gate emits GO. The parent initiative may remain Active while this child plan is still Draft.

**Approval and governance gates:** Before execution, the operator must present the approval packet and wait for explicit "go". During execution, call MCP `validate_action` before any mutating action and obey the verdict. Stop on first red. Do not auto-advance to H2.

## Objective

Lock the authoritative census rebase contract from `39` to `59` and decide whether all `20` extra agents can be remapped into the existing `10` departments without distorting the current North Star or silently widening the department model.

## Decision Rule

`BaselineReady = (RuntimeAgents = 59) AND (AuthoritativePersonas = 39) AND (CurrentDepartments = 10) AND (ExtrasToMap = 20)`

`RemapValid = FOR ALL extra_agent IN ExtrasToMap: assigned_department(extra_agent) IN CurrentDepartmentSet`

`ProjectedTruthConsistent = (SUM(ProjectedDepartmentCounts) = 59) AND (COUNT(DISTINCT(ProjectedDepartmentSet)) = 10)`

`H1_GO = BaselineReady AND RemapValid AND ProjectedTruthConsistent`

If `H1_GO` is false, H1 must emit `NO-GO`, stop, and open a separate governed North Star / department-model change before any authoritative roster rebase continues.

## Scope

### In scope

- restate the current authoritative baseline: `59` runtime agent definitions, `39` authoritative named personas, `34` active authoritative personas, and `10` departments
- evaluate all `20` extra agents against the current `10`-department set only
- publish the proposed mapping matrix and projected authoritative department counts
- produce an explicit H1 decision artifact and diagnostics artifact
- define the fail-closed handoff to H2 through H5 without editing runtime authorities

### Out of scope

- editing `registry/ai_team.json`
- editing `registry/persona_registry_v2.yaml`
- editing `registry/persona_capability_map.yaml`
- editing `registry/agents.yaml`
- activating any promoted persona
- finalizing titles, managers, escalation owners, or active-state flips outside H2 through H5
- changing `Operations/NORTHSTAR.md` in this phase
- creating an eleventh department without a separate governed change

### File allowlist

- `plans/m365-authoritative-persona-census-and-department-model-decision/**`
- `docs/prompts/codex-m365-authoritative-persona-census-and-department-model-decision.md`
- `docs/prompts/codex-m365-authoritative-persona-census-and-department-model-decision-prompt.txt`
- `docs/commercialization/m365-authoritative-persona-census-and-department-model-decision.md`
- `artifacts/diagnostics/m365_authoritative_persona_census_and_department_model_decision.json`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `registry/ai_team.json`
- `registry/persona_registry_v2.yaml`
- `registry/persona_capability_map.yaml`
- `registry/agents.yaml`
- `src/**`
- `tests/**`
- `Operations/NORTHSTAR.md`

## Requirements

- **R1** — Restate the current authoritative baseline and department lock.
- **R2** — Evaluate all `20` planned personas against the existing `10` departments only.
- **R3** — Publish projected department counts for the rebased `59`-persona authoritative roster.
- **R4** — Emit an explicit decision artifact and diagnostics artifact proving either `GO` inside `10` departments or `NO-GO` with separate department-model escalation.
- **R5** — Define the fail-closed handoff from H1 into H2 through H5.
- **R6** — Update governance surfaces truthfully and stop without editing runtime authorities.

## Execution Sequence

| Task | Description |
| --- | --- |
| `T1` | Read the current authoritative authorities and lock the baseline counts (`59`, `39`, `34`, `10`). |
| `T2` | Build the full `20`-persona mapping matrix against the current department set. |
| `T3` | Compute the projected authoritative department distribution and determine whether the `10`-department model holds. |
| `T4` | Publish the H1 decision doc and diagnostics artifact with the `GO` or `NO-GO` result. |
| `T5` | Update `Operations/EXECUTION_PLAN.md`, `Operations/ACTION_LOG.md`, and `Operations/PROJECT_FILE_INDEX.md`, then stop. |

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-authoritative-persona-census-and-department-model-decision.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-authoritative-persona-census-and-department-model-decision-prompt.txt`

## Validation Strategy

- verify the decision doc and diagnostics artifact exist
- verify the projected department counts sum to `59`
- verify the projected department count remains `10`
- verify every one of the `20` extras is assigned to an existing department
- verify no registry or runtime authority files changed
- run `git diff --check`

## Current Authoritative Baseline

| Department | Current Authoritative Count |
| --- | --- |
| `operations` | `2` |
| `hr` | `1` |
| `communication` | `1` |
| `engineering` | `7` |
| `marketing` | `7` |
| `product` | `3` |
| `project-management` | `3` |
| `studio-operations` | `5` |
| `testing` | `5` |
| `design` | `5` |

## Proposed H1 Department Projection

| Department | Current Authoritative Count | Proposed Extra Count | Projected Authoritative Count |
| --- | --- | --- | --- |
| `operations` | `2` | `8` | `10` |
| `hr` | `1` | `1` | `2` |
| `communication` | `1` | `3` | `4` |
| `engineering` | `7` | `1` | `8` |
| `marketing` | `7` | `1` | `8` |
| `product` | `3` | `0` | `3` |
| `project-management` | `3` | `2` | `5` |
| `studio-operations` | `5` | `4` | `9` |
| `testing` | `5` | `0` | `5` |
| `design` | `5` | `0` | `5` |

Projected authoritative total if approved: `59` personas across the same `10` departments.

## Proposed Mapping Set

| Agent ID | Proposed Name | Recommended Department | Fit Rationale |
| --- | --- | --- | --- |
| `audit-operations` | `Naomi Brooks` | `operations` | Audit governance fits the existing operational control surface. |
| `calendar-management-agent` | `Mateo Alvarez` | `communication` | Calendar scheduling is part of the communications coordination surface. |
| `client-relationship-agent` | `Priya Mehta` | `studio-operations` | Client follow-through aligns with the customer and studio operating lane. |
| `compliance-monitoring-agent` | `Farah Alvi` | `operations` | Compliance monitoring belongs inside the existing governance-heavy operations lane. |
| `device-management` | `Connor Walsh` | `operations` | Device operations are operational administration rather than a new department. |
| `email-processing-agent` | `Hannah Kim` | `communication` | Email triage and routing fit the communications function. |
| `financial-operations-agent` | `Luis Carvalho` | `studio-operations` | Financial controls align with the existing finance/reporting studio-operations cluster. |
| `identity-security` | `Amara Okoye` | `operations` | Identity security is part of the operational admin and security-control plane. |
| `it-operations-manager` | `Peter Novak` | `operations` | IT operations management belongs inside the operational administration lane. |
| `knowledge-management-agent` | `Leah Goldstein` | `operations` | Knowledge-control and documentation stewardship fit the operating backbone. |
| `platform-manager` | `Andre Baptiste` | `engineering` | Platform stewardship is an engineering function, not a new department. |
| `project-coordination-agent` | `Sofia Petrova` | `project-management` | Cross-team coordination is a direct project-management responsibility. |
| `project-manager` | `Haruto Tanaka` | `project-management` | Program ownership is already represented inside project management. |
| `recruitment-assistance-agent` | `Camila Torres` | `hr` | Recruiting support fits HR without widening the department model. |
| `reports` | `Youssef Haddad` | `studio-operations` | KPI reporting stays with the existing finance/reporting studio-operations cluster. |
| `security-operations` | `Tunde Adeyemi` | `operations` | Security operations extends the current operations control plane. |
| `service-health` | `Chloe Martin` | `operations` | Service monitoring and escalation fit the operations reliability lane. |
| `teams-manager` | `Alicia Nguyen` | `communication` | Teams workspace orchestration sits closest to communications collaboration. |
| `ucp-administrator` | `Omar El-Masry` | `operations` | UCP control-plane administration belongs inside governed operations. |
| `website-operations-specialist` | `Lucia Fernandez` | `marketing` | Website release operations support the public-facing marketing surface. |

## Approval Packet Contract

Use this exact operator-facing structure before executing H1:

1. `Decision Summary`
2. `Options Considered`
3. `Evaluation Criteria`
4. `Why This Choice`
5. `Risks`
6. `Next Steps`

The recommended approval-packet decision is: preserve the current `10`-department model, accept the projected `59`-persona remap shown above, and stop immediately if any evidence during execution contradicts the mapping fit or forces a new department.

## Governance Closure

- [ ] `Operations/ACTION_LOG.md`
- [ ] `Operations/EXECUTION_PLAN.md`
- [ ] `Operations/PROJECT_FILE_INDEX.md`
- [ ] This child plan `status -> complete`

## Execution Outcome

- **Decision:** `pending`
- **Approved by:** `pending`
- **Completion timestamp:** `pending`

## Agent Constraints

- Do not edit `registry/ai_team.json`, `registry/persona_registry_v2.yaml`, or `registry/persona_capability_map.yaml` in H1.
- Do not add a new department silently; escalate instead.
- Do not auto-advance to H2 even if H1 emits GO.
- Stop if the projected count does not remain `59` across `10` departments.
