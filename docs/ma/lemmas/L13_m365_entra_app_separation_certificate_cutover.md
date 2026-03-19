# L13 — M365 Entra App Separation and Executor Certificate Cutover

## Claim

For standalone SMARTHAUS M365 enterprise certification, the auth architecture is admissible iff:

1. the operator-identity app registration and the backend executor app registration are explicitly distinct
2. the executor app is the only runtime source of app-only Graph execution
3. the operator-identity app is the only governed source of Entra-authenticated human operator identity
4. the executor contract explicitly targets certificate-based auth as the long-term production credential mode
5. `C1A` remains downstream of both the role-separation act and the executor certificate-cutover act

If any of those conditions fails, standalone M365 enterprise certification remains blocked.

## Existing Proof Sources

- `docs/commercialization/m365-entra-identity-and-app-execution-model.md`
- `docs/commercialization/m365-entra-app-registration-separation-and-certificate-cutover.md`
- `plans/m365-enterprise-readiness-master-plan/m365-enterprise-readiness-master-plan.md`
- `Operations/EXECUTION_PLAN.md`
- `docs/prompts/codex-m365-enterprise-readiness-master-plan-b5d-entra-app-registration-role-separation.md`
- `docs/prompts/codex-m365-enterprise-readiness-master-plan-b5e-executor-certificate-cutover-tenant-contract-finalization.md`
- `notebooks/m365/INV-M365-O-entra-app-separation-certificate-cutover.ipynb`
- `notebooks/lemma_proofs/L13_m365_entra_app_separation_certificate_cutover.ipynb`

## Acceptance Evidence

- the active master plan inserts `B5D` and `B5E` before `C1A`
- the executor app and operator-identity app are locked to distinct roles with stable app IDs
- the executor app is documented as certificate-based in the target production posture
- touched-file diff remains bounded to MA traceability, plan/prompt governance, and auth-architecture documentation

## Deterministic Surface

`AuthArchitecture(C1A) = Distinct(operator_identity_app, executor_app) ∧ GraphExecutor(executor_app, app_only) ∧ OperatorIdentity(operator_identity_app, Entra) ∧ ExecutorCredentialTarget(certificate) ∧ Prereq(C1A) ⊇ {B5D, B5E}`
