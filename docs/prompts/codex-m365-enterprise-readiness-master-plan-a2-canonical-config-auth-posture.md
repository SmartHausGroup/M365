# MATHS Prompt: A2 Canonical Config Contract and Auth Posture

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:A2`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-A2-C0` -> `M365-READY-A2-C4` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Use this act prompt only if `A2` is explicitly reopened for revision.
- Final outputs exactly:
  - `GATE:M365-READY-A2 STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-A2`
- Run ID: `a2-canonical-config-auth-posture`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R2`
  - `plan:m365-enterprise-readiness-master-plan:A2`

## Context

- Domain: `docs`
- Dependencies: `docs/commercialization/m365-canonical-config-contract.md`, `docs/commercialization/m365-config-migration-and-auth-policy.md`
- Allowlist:
  - `docs/commercialization/m365-canonical-config-contract.md`
  - `docs/commercialization/m365-config-migration-and-auth-policy.md`
  - `plans/m365-enterprise-readiness-master-plan/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
- Denylist:
  - runtime source files

## M - Model

- Problem: production config authority and auth posture must remain singular and explicit.
- Goal: preserve tenant YAML authority and the documented production auth posture.
- Success criteria:
  - one canonical production config contract
  - auth posture is explicit
  - secret policy and deprecation posture remain explicit

## H - Harness

- `M365-READY-A2-C0` verify plan refs and prerequisite status.
- `M365-READY-A2-C1` inventory current config-contract and auth-policy docs.
- `M365-READY-A2-C2` verify tenant authority and source-precedence language.
- `M365-READY-A2-C3` verify auth, secret, and deprecation posture.
- `M365-READY-A2-C4` sync plan and tracker artifacts if the act is reopened.

## Validation

1. `rg -n "tenant|UCP_TENANT|auth|certificate|client secret|delegated" docs/commercialization/m365-canonical-config-contract.md docs/commercialization/m365-config-migration-and-auth-policy.md`
2. `git diff --check`

## No-Go Triggers

- production authority becomes split between tenant config and dotenv
- auth posture becomes ambiguous
- secret policy permits checked-in secret material
