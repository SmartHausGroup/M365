# MATHS Prompt: B4A Governance Baseline Alignment

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B4A`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B4A-C0` -> `M365-READY-B4A-C7` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Final outputs exactly:
  - `GATE:M365-READY-B4A STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-B4A`
- Run ID: `b4a-governance-baseline-alignment`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R4`
  - `plan:m365-enterprise-readiness-master-plan:R8`
  - `plan:m365-enterprise-readiness-master-plan:B4A`

## Context

- Domain: `governance`
- Dependencies: `AGENTS.md`, `.cursor/rules/*.mdc`, `Operations/NORTHSTAR.md`, `Operations/EXECUTION_PLAN.md`
- Allowlist:
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
  - `plans/m365-enterprise-readiness-master-plan/*`
  - `docs/governance/MATHS_PROMPT_TEMPLATE.md`
  - `docs/prompts/*`
- Denylist:
  - runtime source files not needed for governance alignment

## M - Model

- Problem: the active plan and governance artifacts drifted from `AGENTS.md`.
- Goal: restore one AGENTS-compliant governance baseline before more implementation proceeds.
- Success criteria:
  - next act is explicit and correct
  - project file index exists
  - MATHS prompt template references real repo artifacts

## H - Harness

- `M365-READY-B4A-C0` verify plan refs, prerequisites, and current blocker state.
- `M365-READY-B4A-C1` inventory governance drift across plan, trackers, and prompts.
- `M365-READY-B4A-C2` align master-plan sequencing and execution-plan status.
- `M365-READY-B4A-C3` create or expand the project file index baseline.
- `M365-READY-B4A-C4` correct the MATHS prompt template and control-plane prompts.
- `M365-READY-B4A-C5` normalize action-log and tracker state for the active act.
- `M365-READY-B4A-C6` validate the corrected governance artifacts.
- `M365-READY-B4A-C7` emit final gate and next-act state.

## Validation

1. `rg -n "B4A|B4E|C1A|PROJECT_FILE_INDEX|Prompt discipline" plans/m365-enterprise-readiness-master-plan/m365-enterprise-readiness-master-plan.md Operations/EXECUTION_PLAN.md docs/governance/MATHS_PROMPT_TEMPLATE.md`
2. `git diff --check`

## No-Go Triggers

- active plan and execution plan disagree on the next act
- project file index is still missing
- prompt template still points to nonexistent repo paths
