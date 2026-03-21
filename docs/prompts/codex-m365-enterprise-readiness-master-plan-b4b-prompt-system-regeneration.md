# MATHS Prompt: B4B Prompt System Regeneration

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B4B`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B4B-C0` -> `M365-READY-B4B-C6` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Final outputs exactly:
  - `GATE:M365-READY-B4B STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-B4B`
- Run ID: `b4b-prompt-system-regeneration`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R4`
  - `plan:m365-enterprise-readiness-master-plan:R8`
  - `plan:m365-enterprise-readiness-master-plan:B4B`

## Context

- Domain: `governance`
- Dependencies: `docs/governance/MATHS_PROMPT_TEMPLATE.md`, `plans/m365-enterprise-readiness-master-plan/*`
- Allowlist:
  - `docs/prompts/*`
  - `docs/governance/MATHS_PROMPT_TEMPLATE.md`
  - `Operations/PROJECT_FILE_INDEX.md`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `plans/m365-enterprise-readiness-master-plan/*`
- Denylist:
  - runtime source files

## M - Model

- Problem: the active plan needs one formal MATHS prompt pair per act.
- Goal: regenerate the prompt inventory so no act is unprompted or ambiguously prompted.
- Success criteria:
  - prompt pair exists for every act in the active plan
  - master overview prompt names the correct act order
  - historical commercialization prompts are not treated as active authority

## H - Harness

- `M365-READY-B4B-C0` verify plan refs and current act inventory.
- `M365-READY-B4B-C1` inventory existing prompt coverage and gaps.
- `M365-READY-B4B-C2` regenerate or create missing act prompt pairs.
- `M365-READY-B4B-C3` update master overview prompt and any phase-overview prompts.
- `M365-READY-B4B-C4` update file index and trackers for the regenerated prompt set.
- `M365-READY-B4B-C5` verify prompt files exist and follow the template discipline.
- `M365-READY-B4B-C6` emit final gate and next-act state.

## Validation

1. `find docs/prompts -maxdepth 1 -type f | sort`
2. `rg -n "PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan" docs/prompts`
3. `git diff --check`

## No-Go Triggers

- any active act lacks a prompt pair
- master overview prompt and plan act order diverge
- historical prompts are left as ambiguous active sources
