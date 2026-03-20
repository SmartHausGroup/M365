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
16. `B5D` Entra App Registration Role Separation
17. `B5E` Executor Certificate Cutover and Tenant Contract Finalization
18. `B6` Digital Employee and Executor-Domain Architecture
19. `B6A` Digital Employee Operating Model
20. `B6B` Capability, API, License, and Auth Matrix
21. `B6C` Executor-Domain Partitioning and Minimum-Permission Model
22. `B6D` Persona Registry and Humanized Delegation Routing
23. `B6E` Certification Rebase to the Digital-Employee Multi-Executor Target
24. `B7` Multi-Executor Runtime and Persona Integration
25. `B7A` Tenant Contract and Executor Registry Extension
26. `B7B` Runtime Executor Routing and Domain Selection
27. `B7C` Persona Registry and Humanized Delegation Integration
28. `B7C1` MCP Constraint Contract Repair
29. `B7D` Executor Permission Minimization and Azure Cleanup
30. `B7E` Approval Backend Reproof and Certification Re-Readiness
31. `C1A` Certification Environment Readiness
32. `C1B` Live Read-Only Certification
33. `C1C` Live Mutation and Governance Certification
34. `C1D` Evidence Packet Completion and Matrix Closure
35. `C2` Release Certification Packet and Decision
36. `D1` Enterprise Collateral Pack
37. `D2` Pilot Acceptance and Customer Handoff

## Active-State Rules

- `B7C1` is complete.
- `B7D` is complete.
- `B7E` is complete.
- `C1A` is the next executable act, and its readiness gate is now `GO` under the exact standalone shell contract on the rebased multi-executor runtime.
- `C1B` and `C1C` require explicit live-execution approval.
- `D1` and `D2` must not be used to imply readiness while `B4*`, `C1*`, or `C2` are incomplete.
