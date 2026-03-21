# MATHS Prompt: C1 Live-Tenant Certification Execution Overview

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:R6`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- This overview prompt is historical coordination only.
- Use `C1A`, `C1B`, `C1C`, and `C1D` act prompts for actual execution.
- Stop on first `FAIL` or `BLOCKED`.
- Do not execute any tenant-impacting step without explicit approval for live validation.

## Prompt Run Metadata

- Task ID: `M365-READY-C1`
- Run ID: `c1-live-tenant-certification-execution`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R6`
- Owners: `operations`, `security`, `engineering`

## Context

- Domain: `test`
- Dependencies: `B4E`, `C1A`, `C1B`, `C1C`, `C1D`
- Goal: coordinate the `C1A` → `C1D` act sequence without treating live certification as one opaque act.
- Allowlist:
  - `plans/m365-enterprise-readiness-master-plan/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `docs/commercialization/m365-live-tenant-validation-matrix.md`
  - `docs/commercialization/m365-release-gates-and-certification.md`
  - `artifacts/certification/*`
- Denylist:
  - `docs/prompts/**` other than the active `C1*` act prompts

## Act Sequence

1. `C1A` Certification Environment Readiness
2. `C1B` Live Read-Only Certification
3. `C1C` Live Mutation and Governance Certification
4. `C1D` Evidence Packet Completion and Matrix Closure

`C2` is downstream and is not part of this overview prompt.

## Validation

1. Evidence packet matches the rows in `docs/commercialization/m365-live-tenant-validation-matrix.md`
2. `rg -n "C1A|C1B|C1C|C1D|Live required|supported actions|approval|audit" plans/m365-enterprise-readiness-master-plan/m365-enterprise-readiness-master-plan.md docs/commercialization/m365-live-tenant-validation-matrix.md`
3. `git diff --check`

## No-Go Triggers

- live work is attempted without explicit approval
- evidence packet is incomplete for any required supported-surface row
- certification-critical checks fail or remain ambiguous
