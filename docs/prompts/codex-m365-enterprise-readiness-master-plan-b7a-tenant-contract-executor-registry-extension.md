# MATHS Prompt: B7A Tenant Contract and Executor Registry Extension

## Governance Ack

- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B7A`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B7A-C0` -> `M365-READY-B7A-C6` in order.
- Stop on first `FAIL` or `BLOCKED`.

## Prompt Run Metadata

- Task ID: `M365-READY-B7A`
- Run ID: `b7a-tenant-contract-executor-registry-extension`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R11`
  - `plan:m365-enterprise-readiness-master-plan:B7A`

## Context

- Domain: `code`
- Goal: extend the tenant contract and config authority to represent bounded executor domains instead of one giant executor.

## M - Model

- Success criteria:
  - tenant schema supports multiple executors
  - executor registry metadata is explicit
  - single-executor migration path is defined

## H - Harness

- `M365-READY-B7A-C0` verify dependency state.
- `M365-READY-B7A-C1` extend tenant schema.
- `M365-READY-B7A-C2` extend config loaders.
- `M365-READY-B7A-C3` define executor registry metadata.
- `M365-READY-B7A-C4` add bounded tests.
- `M365-READY-B7A-C5` sync docs and trackers.
- `M365-READY-B7A-C6` validate and emit gate.

## Validation

1. `rg -n "executors:|executor_registry|SharePoint executor|collaboration executor" src docs`
2. `git diff --check`

## No-Go Triggers

- tenant contract still assumes one executor only
