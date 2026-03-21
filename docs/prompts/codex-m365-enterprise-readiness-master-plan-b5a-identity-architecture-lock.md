# MATHS Prompt: B5A Identity Architecture Lock

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B5A`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B5A-C0` -> `M365-READY-B5A-C7` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Final outputs:
  - `GATE:M365-READY-B5A STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-B5A`
- Run ID: `b5a-identity-architecture-lock`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R3`
  - `plan:m365-enterprise-readiness-master-plan:R9`
  - `plan:m365-enterprise-readiness-master-plan:B5A`
- Owners: `product`, `engineering`, `security`

## Context

- Domain: `governance`
- Dependencies: `B4E`, `A2`, `A3`, `A4`
- Goal: lock the production identity architecture as Entra user authentication plus app-only Graph execution.
- Allowlist:
  - `plans/m365-enterprise-readiness-master-plan/*`
  - `Operations/NORTHSTAR.md`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
  - `docs/commercialization/m365-canonical-config-contract.md`
  - `docs/commercialization/m365-config-migration-and-auth-policy.md`
  - `docs/commercialization/m365-permission-approval-fail-closed-hardening.md`
  - `docs/commercialization/m365-audit-and-governance-evidence-model.md`
  - `docs/commercialization/m365-live-tenant-validation-matrix.md`
  - `src/smarthaus_common/tenant_config.py`
  - `src/ops_adapter/main.py`
  - `src/ops_adapter/app.py`
- Denylist:
  - live tenant execution

## M - Model

- Problem: the repo has app-only execution posture and partial user-identity handling, but not a formally locked enterprise identity model.
- Success criteria:
  - SmartHaus user authentication is explicitly tied to Microsoft Entra ID
  - Graph execution identity remains the SmartHaus app registration
  - actor-versus-executor semantics are explicit across policy, approvals, and audit

## H - Harness

- `M365-READY-B5A-C0` verify `B4E` completion and current identity posture.
- `M365-READY-B5A-C1` inventory current user-auth, app-auth, approval, and audit surfaces.
- `M365-READY-B5A-C2` define the canonical production identity model.
- `M365-READY-B5A-C3` define required tenant-contract and documentation updates.
- `M365-READY-B5A-C4` sync master-plan critical-path ordering.
- `M365-READY-B5A-C5` create or update act-level prompt inventory.
- `M365-READY-B5A-C6` run governance validation.
- `M365-READY-B5A-C7` emit final gate and next-act state.

## Validation

1. `rg -n "Entra|Azure AD|app_only|delegated|hybrid|permission_tiers|audit" docs src plans`
2. `git diff --check`

## No-Go Triggers

- actor identity and service executor identity remain conflated
- certification is still scheduled before identity architecture closure
- active prompts or trackers disagree on the next act
