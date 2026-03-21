# MATHS Prompt: B4D4A Typing Environment and Module-Path Unblock

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B4D4A`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`

## Goal

Remove governed mypy environment blockers by adding the required third-party typing dependency and eliminating duplicate module discovery for `src/ops_adapter/actions.py`.

## Validation

1. `pre-commit run mypy --all-files`
2. `git diff --check`

## No-Go Triggers

- global weakening of type checking
- duplicate module discovery remains
