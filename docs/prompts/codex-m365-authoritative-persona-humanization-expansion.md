# Execution Prompt — Governed Authoritative Persona Humanization Expansion

Plan Reference: `plan:m365-authoritative-persona-humanization-expansion`
Parent Plan: `plan:m365-post-expansion-promotion-and-persona-activation`
North Star: `Operations/NORTHSTAR.md`
Execution Plan: `Operations/EXECUTION_PLAN.md`
Prompt Template: `docs/governance/MATHS_PROMPT_TEMPLATE.md`

**Mission:** execute the future governed implementation that promotes all `20` extra agents into named digital employees, rebases the authoritative census deliberately, and keeps the runtime fail-closed while the current `10`-department North Star remains the default model.

This prompt is created in the planning slice only. It does not authorize runtime expansion by itself.

## Phase Package Stack

Use the parent initiative only as the coordinator. Execute the child phases through their dedicated packages in this exact order:

1. `H1` — `plans/m365-authoritative-persona-census-and-department-model-decision/m365-authoritative-persona-census-and-department-model-decision.md`
2. `H2` — `plans/m365-authoritative-persona-humanized-employee-record-completion/m365-authoritative-persona-humanized-employee-record-completion.md`
3. `H3` — `plans/m365-authoritative-persona-registry-and-capability-map-rebase/m365-authoritative-persona-registry-and-capability-map-rebase.md`
4. `H4` — `plans/m365-authoritative-persona-certification-and-count-rebase/m365-authoritative-persona-certification-and-count-rebase.md`
5. `H5` — `plans/m365-authoritative-persona-activation-gate-closeout/m365-authoritative-persona-activation-gate-closeout.md`

Each child phase has its own detailed prompt and kickoff prompt. Do not execute broad parent-level runtime changes directly when a child-phase package exists.

## Governance Lock (Mandatory)

Before any write, test, or mutating command:

1. Read:
- `AGENTS.md`
- applicable `.cursor/rules/**/*.mdc`
- `Operations/NORTHSTAR.md`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`
- `plans/m365-authoritative-persona-humanization-expansion/m365-authoritative-persona-humanization-expansion.md`
- `plans/m365-authoritative-persona-humanization-expansion/m365-authoritative-persona-humanization-expansion.yaml`
- `registry/agents.yaml`
- `registry/ai_team.json`
- `registry/persona_registry_v2.yaml`
- `registry/persona_capability_map.yaml`

2. Verify current truth:
- runtime inventory remains `59` agents in `registry/agents.yaml`
- authoritative named roster remains `39` in `registry/ai_team.json`
- authoritative registry remains `39` total / `34` active in `registry/persona_registry_v2.yaml`
- no runtime expansion may be claimed before those authorities are deliberately rebased

3. Enforce approval protocol:
- present the approval packet first
- wait for explicit owner approval before any mutating phase
- call `validate_action` before every write, commit, push, or test run
- stop immediately on any red governance verdict
- if the mandatory pre-commit gate fails on the bounded remediation set in `tests/test_ucp_m365_pack_contracts.py` and `tests/test_ucp_m365_pack_client.py`, fix only those files before continuing the commit path

## Mission Constraints

- preserve the current `10`-department North Star by default
- if H1 proves a remap is impossible, stop and open a separate governed department-model change
- use only bounded metadata fields:
  - `working_style`
  - `communication_style`
  - `decision_style`
- do not invent freeform personality schema
- do not mark any promoted persona `active` until chain-of-command, capability-map, registry, and certification-count gates are green
- do not widen the remediation surface beyond `tests/test_ucp_m365_pack_contracts.py` and `tests/test_ucp_m365_pack_client.py` for commit-gate repair

## Sequential Execution Discipline

- execute only one child phase at a time
- `H2`, `H3`, `H4`, and `H5` are notebook-first / MA-first phases
- for `H2` through `H5`, enforce MA phases `0` through `7` explicitly:
  - phase `0` intent definition must be restated in the approval packet and approved before notebook work starts
  - phases `1` through `4` must establish the formula, calculus, lemmas, and invariants before extraction
  - phase `6` scorecard green is mandatory before any runtime, registry, verifier, or documentation extraction
  - phase `7` extraction must mirror notebook-proven logic exactly
- all iteration for those phases must occur in notebooks first before any extraction into code, registries, tests, verifiers, or docs
- after each child phase is green, commit and push that child phase before moving to the next one
- no child phase may start until its predecessor is green, committed, and pushed

## Candidate Persona Set

Use the following authoritative promotion targets:

- `audit-operations -> Naomi Brooks`
- `calendar-management-agent -> Mateo Alvarez`
- `client-relationship-agent -> Priya Mehta`
- `compliance-monitoring-agent -> Farah Alvi`
- `device-management -> Connor Walsh`
- `email-processing-agent -> Hannah Kim`
- `financial-operations-agent -> Luis Carvalho`
- `identity-security -> Amara Okoye`
- `it-operations-manager -> Peter Novak`
- `knowledge-management-agent -> Leah Goldstein`
- `platform-manager -> Andre Baptiste`
- `project-coordination-agent -> Sofia Petrova`
- `project-manager -> Haruto Tanaka`
- `recruitment-assistance-agent -> Camila Torres`
- `reports -> Youssef Haddad`
- `security-operations -> Tunde Adeyemi`
- `service-health -> Chloe Martin`
- `teams-manager -> Alicia Nguyen`
- `ucp-administrator -> Omar El-Masry`
- `website-operations-specialist -> Lucia Fernandez`

Use the bounded style metadata and recommended department placements recorded in the plan package unless a later approved H1 decision changes them.

## Execution Order (After Approval Only)

1. **H1 — Authoritative census and department-model decision**
   - confirm the exact census rebase from `39` to `59`
   - preserve the existing `10`-department model by default
   - stop and escalate if a new department is required
2. **H2 — Humanized employee record completion**
   - fill name, title, department, manager, escalation owner, working_style, communication_style, and decision_style for all `20`
3. **H3 — Authoritative registry and capability-map rebase**
   - update `registry/ai_team.json`
   - update `registry/persona_registry_v2.yaml`
   - update `registry/persona_capability_map.yaml`
4. **H4 — Certification and count rebase**
   - rebase all summary counts and commercialization truth surfaces that still assert `39`
5. **H5 — Activation gate closeout**
   - fail closed if any promoted persona lacks name, title, chain-of-command, capability-map coverage, authoritative registry entry, or certification-count alignment
   - land the final authoritative state only after H2 through H4 are green and pushed

## Required Output Format

Before approval, use this exact structure:

- `Decision Summary`
- `Options Considered`
- `Evaluation Criteria`
- `Why This Choice`
- `Risks`
- `Next Steps`

After approval, report:

- phase status by `H1` through `H5`
- evidence paths for every changed authority surface
- exact validation commands and results
- any stop condition or blocker

## Success Criteria

- the authoritative census rebase is explicit and truthful
- the current `10`-department model is preserved unless a separate governed change is approved
- all `20` promoted personas are named digital employees with bounded metadata
- no persona is marked active without the full fail-closed prerequisite set
- runtime truth, registry truth, and certification/count truth all agree

## Stop Conditions

- any attempt to silently widen the department model
- any attempt to add freeform personality schema
- any attempt to mark a promoted persona active without title, manager, escalation owner, capability-map coverage, and authoritative registry entry
- any mismatch between `registry/ai_team.json`, `registry/persona_registry_v2.yaml`, `registry/persona_capability_map.yaml`, and the rebased counts
