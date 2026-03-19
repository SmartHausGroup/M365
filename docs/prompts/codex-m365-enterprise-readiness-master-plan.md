# MATHS Prompt: M365 Enterprise Readiness Master Plan Overview

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:R1`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- This overview prompt is the active control-plane map for the standalone M365 readiness program.
- Every execution act must use its own act-specific MATHS prompt pair.
- Stop on first `FAIL` or `BLOCKED`.
- Do not use absorbed commercialization prompts as active execution authority.

## Prompt Run Metadata

- Prompt version: `2.0`
- Task ID: `M365-READY-MASTER`
- Run ID: `m365-enterprise-readiness-master-plan-overview`
- Commit SHA: `WORKTREE`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R1`
  - `plan:m365-enterprise-readiness-master-plan:R8`
- Invariant IDs in scope: `N/A`
- Lemma IDs in scope: `N/A`
- Owners: `product`, `engineering`, `operations`

## Context

- Task name: `M365 enterprise-readiness master control plane`
- Domain: `governance`
- Dependencies:
  - `Operations/NORTHSTAR.md`
  - `Operations/EXECUTION_PLAN.md`
  - `plans/m365-enterprise-readiness-master-plan/m365-enterprise-readiness-master-plan.md`
- Allowlist:
  - `plans/m365-enterprise-readiness-master-plan/*`
  - `Operations/NORTHSTAR.md`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
  - `docs/prompts/*`
  - `docs/governance/MATHS_PROMPT_TEMPLATE.md`
- Denylist:
  - `plans/m365-enterprise-commercialization-readiness/*` as active execution authority

## M - Model

- Problem: the repo needs one AGENTS-compliant active readiness program with explicit execution acts and prompt discipline.
- Goal: keep one accurate critical path from foundation through standards closure, live certification, and launch handoff.
- Success criteria:
  - the master plan names the correct next act
  - the prompt inventory covers every act in the plan
  - downstream work cannot outrun validation or certification blockers
- Out of scope:
  - direct runtime implementation
  - live tenant execution

## Act Order

1. `A1` Product Boundary and Positioning
2. `A2` Canonical Config Contract and Auth Posture
3. `A3` Governance Boundary and Certification Model
4. `A4` Packaging and Operator Model
5. `B1` Runtime Config Authority Remediation
6. `B2` Fail-Closed Governance and Approval Remediation
7. `B3` Admin Audit and Evidence-Surface Remediation
8. `B4A` Governance Baseline Alignment
9. `B4B` Prompt System Regeneration
10. `B4C` Validation Blockers and Syntax Recovery
11. `B4D` Ruff/Black/Mypy Remediation
12. `B4E` Full Repo Validation Closure
13. `B5A` Identity Architecture Lock
14. `B5B` Runtime Identity Enforcement
15. `B5C` Authorization and Audit Binding
16. `C1A` Certification Environment Readiness
17. `C1B` Live Read-Only Certification
18. `C1C` Live Mutation and Governance Certification
19. `C1D` Evidence Packet Completion and Matrix Closure
20. `C2` Release Certification Packet and Decision
21. `D1` Enterprise Collateral Pack
22. `D2` Pilot Acceptance and Customer Handoff

## Active-State Rules

- `B5A` is the next executable act.
- `C1A` is prepared but blocked until `B5C` is complete and the live environment prerequisites exist.
- `C1B` and `C1C` require explicit live-execution approval.
- `D1` and `D2` must not be used to imply readiness while `B4*`, `C1*`, or `C2` are incomplete.
