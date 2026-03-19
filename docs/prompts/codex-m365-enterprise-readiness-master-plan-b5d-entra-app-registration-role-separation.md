# MATHS Prompt: B5D Entra App Registration Role Separation

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B5D`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B5D-C0` -> `M365-READY-B5D-C7` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Final outputs exactly:
  - `GATE:M365-READY-B5D STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-B5D`
- Run ID: `b5d-entra-app-registration-role-separation`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R8`
  - `plan:m365-enterprise-readiness-master-plan:R9`
  - `plan:m365-enterprise-readiness-master-plan:B5D`

## Context

- Domain: `docs`
- Dependencies: `B5C`
- Goal: lock the Azure / Entra app-registration role split so the operator-identity plane and the executor plane are no longer ambiguous before certification resumes.
- Allowlist:
  - `plans/m365-enterprise-readiness-master-plan/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
  - `docs/commercialization/m365-entra-identity-and-app-execution-model.md`
  - `docs/commercialization/m365-entra-app-registration-separation-and-certificate-cutover.md`
  - `docs/prompts/*b5d*`
  - `docs/prompts/*b5e*`
- Denylist:
  - runtime code changes
  - live tenant execution

## M - Model

- Problem: the SMARTHAUS auth architecture is implemented conceptually in runtime, but the live Azure app-registration layer is still not formally role-separated.
- Success criteria:
  - the executor app and operator-identity app are locked to distinct roles
  - the active master plan and prompt inventory place `B5D` before `B5E` and `C1A`
  - the Azure cleanup specification is explicit and deterministic

## H - Harness

- `M365-READY-B5D-C0` verify `B5C` closure and current `C1A` blockage state.
- `M365-READY-B5D-C1` inventory the current app registrations and current tenant-contract executor selection.
- `M365-READY-B5D-C2` lock the executor-app role.
- `M365-READY-B5D-C3` lock the operator-identity-app role.
- `M365-READY-B5D-C4` sync the active plan and trackers so `B5D` is the next act and `C1A` is re-blocked.
- `M365-READY-B5D-C5` create or refresh the `B5D` and `B5E` prompt pairs.
- `M365-READY-B5D-C6` validate the governance rewrite.
- `M365-READY-B5D-C7` emit final gate and next-act state.

## Validation

1. `rg -n "720788ac-1485-4073-b0c8-1a6294819a87|e6fd71d3-4116-401e-a4f1-b2fda4318a8b|SMARTHAUS M365 Executor|SMARTHAUS M365 Operator Identity|B5D|B5E" docs plans Operations`
2. `git diff --check`

## No-Go Triggers

- the executor app and operator-identity app are still treated as overlapping roles
- `C1A` remains the active next act instead of being blocked behind `B5D` and `B5E`
- the cleanup spec does not explicitly target certificate-based executor auth
