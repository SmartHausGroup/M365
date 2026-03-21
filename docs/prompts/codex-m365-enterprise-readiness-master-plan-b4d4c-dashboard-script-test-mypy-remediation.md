# MATHS Prompt: B4D4C Dashboard, Script, and Test Mypy Remediation

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B4D4C`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`

## Goal

Reduce the remaining actionable mypy debt across dashboards, scripts, and tests after the core governed runtime surface is corrected.

## Validation

1. `pre-commit run mypy --files <touched dashboard, script, and test files>`
2. `git diff --check`

## No-Go Triggers

- fixes widen into unrelated certification or launch collateral
- checker settings are weakened globally
