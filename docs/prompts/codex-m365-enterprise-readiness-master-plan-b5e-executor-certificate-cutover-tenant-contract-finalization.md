# MATHS Prompt: B5E Executor Certificate Cutover and Tenant Contract Finalization

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B5E`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B5E-C0` -> `M365-READY-B5E-C8` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Final outputs exactly:
  - `GATE:M365-READY-B5E STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-B5E`
- Run ID: `b5e-executor-certificate-cutover-tenant-contract-finalization`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R9`
  - `plan:m365-enterprise-readiness-master-plan:B5E`

## Context

- Domain: `config`
- Dependencies: `B5D`
- Goal: cut the SMARTHAUS executor app to a certificate-based production posture and finalize the tenant contract before `C1A` resumes.
- Allowlist:
  - `/Users/smarthaus/Projects/GitHub/UCP/tenants/smarthaus.yaml`
  - `plans/m365-enterprise-readiness-master-plan/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
  - `docs/commercialization/m365-entra-app-registration-separation-and-certificate-cutover.md`
  - `artifacts/certification/m365-v1-candidate-52ca494/*`
  - `docs/prompts/*b5e*`
- Denylist:
  - live tenant mutation execution before `C1A`

## M - Model

- Problem: the executor app is still secret-based, which is transitional and not the intended long-term enterprise posture.
- Success criteria:
  - the tenant contract selects the executor app through certificate auth
  - executor secrets are no longer required after successful cutover validation
  - `C1A` prerequisites reference the finalized executor contract

## H - Harness

- `M365-READY-B5E-C0` verify `B5D` role separation closure.
- `M365-READY-B5E-C1` inventory the current SMARTHAUS tenant contract and executor credential state.
- `M365-READY-B5E-C2` define the executor certificate material requirements and runtime path contract.
- `M365-READY-B5E-C3` update the tenant contract to prefer the certificate path.
- `M365-READY-B5E-C4` validate non-mutating executor Graph auth through the certificate path.
- `M365-READY-B5E-C5` retire executor secrets only after certificate validation succeeds.
- `M365-READY-B5E-C6` sync `C1A` prerequisites and trackers.
- `M365-READY-B5E-C7` run bounded validation.
- `M365-READY-B5E-C8` emit final gate and next-act state.

## Validation

1. `rg -n "client_certificate_path|client_secret|720788ac-1485-4073-b0c8-1a6294819a87|B5E|C1A" /Users/smarthaus/Projects/GitHub/UCP/tenants/smarthaus.yaml docs plans Operations artifacts/certification/m365-v1-candidate-52ca494`
2. `git diff --check`

## No-Go Triggers

- the executor tenant contract still depends on an uncleared secret as the final production posture
- the operator-identity app is used as the Graph executor
- `C1A` proceeds without a finalized executor certificate contract
