# MATHS Prompt: B6B Capability, API, License, and Auth Matrix

## Governance Ack

- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B6B`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B6B-C0` -> `M365-READY-B6B-C6` in order.
- Stop on first `FAIL` or `BLOCKED`.

## Prompt Run Metadata

- Task ID: `M365-READY-B6B`
- Run ID: `b6b-capability-api-license-auth-matrix`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R10`
  - `plan:m365-enterprise-readiness-master-plan:B6B`

## Context

- Domain: `docs`
- Goal: map what “anything in M365” means across licensed surface, exposed API surface, and auth posture.

## M - Model

- Problem: licensed scope, automation scope, and auth scope are being conflated.
- Success criteria:
  - Graph versus non-Graph surfaces are explicit
  - delegated versus app-only posture is explicit
  - workload boundaries are clear enough to drive executor domains

## H - Harness

- `M365-READY-B6B-C0` verify dependency state.
- `M365-READY-B6B-C1` classify workloads by API surface.
- `M365-READY-B6B-C2` classify workloads by auth mode.
- `M365-READY-B6B-C3` classify workloads by license dependency.
- `M365-READY-B6B-C4` mark v1 implementation relevance.
- `M365-READY-B6B-C5` sync plan and prompt state.
- `M365-READY-B6B-C6` validate and emit gate.

## Validation

1. `rg -n "Graph|delegated|app-only|license|Power Platform|Power BI" docs/commercialization/m365-capability-api-license-auth-matrix.md`
2. `git diff --check`

## No-Go Triggers

- licensed scope is presented as automatically automatable scope
- workload/auth/API boundaries remain ambiguous
