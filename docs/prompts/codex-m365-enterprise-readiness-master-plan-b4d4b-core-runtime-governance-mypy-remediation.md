# MATHS Prompt: B4D4B Core Runtime and Governance Mypy Remediation

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B4D4B`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`

## Goal

Reduce the actionable mypy debt in the governed runtime and governance core, prioritizing `src/ops_adapter/`, `src/smarthaus_common/`, `src/smarthaus_graph/`, and the core CLI analyzers that feed the enterprise-readiness path.

## Validation

1. `pre-commit run mypy --files <touched core files>`
2. `git diff --check`

## No-Go Triggers

- type checking is silenced instead of corrected
- fixes widen into unrelated dashboard or script surfaces
