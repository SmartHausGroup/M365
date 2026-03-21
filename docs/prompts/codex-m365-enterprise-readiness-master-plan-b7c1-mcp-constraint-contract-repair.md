# MATHS Prompt: B7C1 MCP Constraint Contract Repair

## Governance Ack

- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B7C1`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B7C1-C0` -> `M365-READY-B7C1-C6` in order.
- Stop on first `FAIL` or `BLOCKED`.

## Prompt Run Metadata

- Task ID: `M365-READY-B7C1`
- Run ID: `b7c1-mcp-constraint-contract-repair`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R8`
  - `plan:m365-enterprise-readiness-master-plan:R11`
  - `plan:m365-enterprise-readiness-master-plan:B7C1`

## Context

- Domain: `governance`
- Goal: repair the inconsistent MCP metadata contract for bounded read-only validation and governance-closeout execution before `B7D` resumes.

## M - Model

- Problem: the governance gate accepted the write surfaces during `B7C` but rejected bounded read-only test-run and governance-closeout validation shapes on metadata semantics.
- Success criteria:
  - the ownership boundary between this repo and upstream UCP constraints is explicit
  - the accepted metadata contract for bounded validation is written down
  - `B7D` is blocked until the repaired contract is provably deterministic

## H - Harness

- `M365-READY-B7C1-C0` verify `B7C` completion and the current `B7D` block condition.
- `M365-READY-B7C1-C1` isolate the constraint-ownership boundary.
- `M365-READY-B7C1-C2` document the accepted metadata contract for bounded read-only validation.
- `M365-READY-B7C1-C3` document the accepted governance-closeout validation shape.
- `M365-READY-B7C1-C4` sync the plan, prompts, and trackers so `B7D` is blocked behind `B7C1`.
- `M365-READY-B7C1-C5` validate the repaired control-plane artifacts.
- `M365-READY-B7C1-C6` emit the resulting gate and next-act state.

## Validation

1. `rg -n "constraint contract|validate_action|B7C1|governance-closeout|test_run" docs/governance docs/prompts plans Operations`
2. `git diff --check`

## No-Go Triggers

- the ownership boundary remains ambiguous
- valid bounded read-only validation shapes are still undefined
- `B7D` is allowed to resume without a repaired contract
