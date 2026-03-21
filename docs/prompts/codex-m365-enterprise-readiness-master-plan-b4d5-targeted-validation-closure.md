# MATHS Prompt: B4D5 Targeted Validation Closure

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B4D5`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B4D5-C0` -> `M365-READY-B4D5-C7` in strict order.
- Stop on first `FAIL` or `BLOCKED`.

## Prompt Run Metadata

- Task ID: `M365-READY-B4D5`
- Run ID: `b4d5-targeted-validation-closure`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R5`
  - `plan:m365-enterprise-readiness-master-plan:B4D5`

## Context

- Domain: `governance`
- Dependencies: `B4D2`, `B4D3`, `B4D4`
- Goal: prove the `B4D` remediation surface is stable before `B4E`.

## Validation

1. `ruff check <approved touched set>`
2. `black --check <approved touched set>` or approved equivalent
3. `mypy <approved governed module set>`
4. `git diff --check`

## No-Go Triggers

- targeted validation is not green for the remediated surfaces
- `B4E` is advanced without a stable targeted validation handoff
