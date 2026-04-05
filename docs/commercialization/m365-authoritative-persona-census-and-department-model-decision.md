# M365 Authoritative Persona Census and Department-Model Decision

- **Plan ID:** `plan:m365-authoritative-persona-census-and-department-model-decision`
- **Decision Date:** `2026-04-05`
- **Decision Timestamp:** `2026-04-05 07:46:12 EDT`
- **Decision:** `GO`
- **Approved By:** `operator explicit go`
- **Next Governed Act:** `H2`

## Summary

H1 confirms that the current authoritative workforce can be rebased from `39` named personas to a future `59` named personas without widening the current `10`-department North Star model. All `20` currently extra runtime agents can be mapped into the existing department set. No registry, runtime, certification, or activation files were changed in H1.

## Baseline Truth

- Runtime agent definitions in `registry/agents.yaml`: `59`
- Authoritative named personas in `registry/ai_team.json`: `39`
- Authoritative registry total in `registry/persona_registry_v2.yaml`: `39`
- Active authoritative personas in `registry/persona_registry_v2.yaml`: `34`
- Current authoritative departments in `registry/ai_team.json`: `10`
- Extras to evaluate: `20`

## Department Lock

The locked authoritative department set for H1 is:

- `operations`
- `hr`
- `communication`
- `engineering`
- `marketing`
- `product`
- `project-management`
- `studio-operations`
- `testing`
- `design`

H1 does not permit an eleventh department. Any evidence requiring a new department would have forced `NO-GO`.

## Mapping Matrix

| Agent ID | Proposed Name | Approved Department | Rationale |
| --- | --- | --- | --- |
| `audit-operations` | `Naomi Brooks` | `operations` | Audit governance fits the operational control surface. |
| `calendar-management-agent` | `Mateo Alvarez` | `communication` | Calendar coordination fits the communications coordination surface. |
| `client-relationship-agent` | `Priya Mehta` | `studio-operations` | Client follow-through aligns with the customer and studio operating lane. |
| `compliance-monitoring-agent` | `Farah Alvi` | `operations` | Compliance monitoring belongs in the governance-heavy operations lane. |
| `device-management` | `Connor Walsh` | `operations` | Device administration is an operational control-plane function. |
| `email-processing-agent` | `Hannah Kim` | `communication` | Email triage and routing fit the communications function. |
| `financial-operations-agent` | `Luis Carvalho` | `studio-operations` | Financial controls align with the existing finance/reporting cluster. |
| `identity-security` | `Amara Okoye` | `operations` | Identity security extends the operational security-control plane. |
| `it-operations-manager` | `Peter Novak` | `operations` | IT operations management belongs in operations. |
| `knowledge-management-agent` | `Leah Goldstein` | `studio-operations` | Knowledge stewardship aligns with enablement, reporting, and support operations already grouped in studio operations. |
| `platform-manager` | `Andre Baptiste` | `engineering` | Platform stewardship is an engineering function. |
| `project-coordination-agent` | `Sofia Petrova` | `project-management` | Cross-team coordination is a direct project-management responsibility. |
| `project-manager` | `Haruto Tanaka` | `project-management` | Program ownership is already represented in project management. |
| `recruitment-assistance-agent` | `Camila Torres` | `hr` | Recruiting support fits HR without widening the model. |
| `reports` | `Youssef Haddad` | `studio-operations` | KPI reporting stays with the finance/reporting cluster. |
| `security-operations` | `Tunde Adeyemi` | `operations` | Security operations extends the existing operational control plane. |
| `service-health` | `Chloe Martin` | `operations` | Service monitoring and escalation fit the reliability lane. |
| `teams-manager` | `Alicia Nguyen` | `communication` | Teams workspace orchestration fits communications collaboration. |
| `ucp-administrator` | `Omar El-Masry` | `operations` | UCP control-plane administration belongs in governed operations. |
| `website-operations-specialist` | `Lucia Fernandez` | `marketing` | Website release operations support the public-facing marketing surface. |

## Projected Department Counts

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

- Projected authoritative total: `59`
- Projected distinct departments: `10`

## Decision Logic

- `BaselineReady`: pass
- `RemapValid`: pass
- `ProjectedTruthConsistent`: pass
- `H1_GO`: pass

## Stop Conditions Checked

- No new department was required.
- No projected count divergence from `59` across `10` departments was found.
- No registry, runtime, certification, or activation edits were performed.

## Handoff

H1 emits `GO`. The next governed act is `H2` under `plan:m365-authoritative-persona-humanized-employee-record-completion:R1`. H2 remains blocked until its own approval packet is presented and receives explicit `go`.
