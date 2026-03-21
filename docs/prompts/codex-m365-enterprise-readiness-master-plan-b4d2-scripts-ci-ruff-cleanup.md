# MATHS Prompt: B4D2 Scripts and CI Ruff Cleanup

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B4D2`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B4D2-C0` -> `M365-READY-B4D2-C7` in strict order.
- Stop on first `FAIL` or `BLOCKED`.

## Prompt Run Metadata

- Task ID: `M365-READY-B4D2`
- Run ID: `b4d2-scripts-ci-ruff-cleanup`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R5`
  - `plan:m365-enterprise-readiness-master-plan:B4D2`

## Context

- Domain: `code`
- Dependencies: `B4D1`
- Goal: close the remaining Ruff debt in scripts and CI-adjacent files without changing runtime behavior.

## Validation

1. `ruff check <touched scripts and CI files>`
2. `git diff --check`

## No-Go Triggers

- runtime behavior changes outside script or CI tooling
- remediation widens into black or mypy work not required for scripts/CI Ruff closure
