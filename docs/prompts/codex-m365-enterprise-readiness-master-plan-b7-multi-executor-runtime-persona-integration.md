# MATHS Prompt: B7 Multi-Executor Runtime and Persona Integration

## Governance Ack

- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B7`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B7-C0` -> `M365-READY-B7-C7` in strict order.
- Stop on first `FAIL` or `BLOCKED`.

## Prompt Run Metadata

- Task ID: `M365-READY-B7`
- Run ID: `b7-multi-executor-runtime-persona-integration`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R8`
  - `plan:m365-enterprise-readiness-master-plan:R10`
  - `plan:m365-enterprise-readiness-master-plan:R11`
  - `plan:m365-enterprise-readiness-master-plan:B7`

## Context

- Domain: `code`
- Dependencies: `B6E`
- Goal: implement the rebased production target with bounded executor domains, persona-aware routing, deterministic governance-closeout semantics, and approval-path reachability.

## M - Model

- Problem: the B6 architecture is locked, but the runtime still reflects the old single-executor posture.
- Success criteria:
  - tenant contract supports bounded executor domains
  - runtime routes actions through the correct executor domain
  - personas bind to routing, approval, and audit semantics
  - governance validation for bounded read-only and closeout paths is deterministic
  - approval reachability is restored through the SharePoint executor path

## H - Harness

- `M365-READY-B7-C0` verify B6 closure and C1A rebase state.
- `M365-READY-B7-C1` extend the tenant contract and executor registry.
- `M365-READY-B7-C2` implement executor routing.
- `M365-READY-B7-C3` bind personas into runtime delegation.
- `M365-READY-B7-C4` repair the MCP constraint contract for bounded validation and governance closeout.
- `M365-READY-B7-C5` minimize executor permissions and clean Azure posture.
- `M365-READY-B7-C6` re-prove approval reachability.
- `M365-READY-B7-C7` refresh certification readiness.
- `M365-READY-B7-C8` emit final gate and next-act state.

## Validation

1. `rg -n "executor|persona|routing|approval backend|SharePoint executor|constraint contract|B7C1|validate_action" src docs plans`
2. `git diff --check`

## No-Go Triggers

- single-executor runtime behavior remains active
- personas are documented but not bound into routing or audit
- governance-closeout validation remains metadata-ambiguous
- approval reachability is still tied to the legacy executor path
