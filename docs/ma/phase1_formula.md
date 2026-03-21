# Phase 1 Formula — M365 Contract System

Plan refs: `plan:m365-ma-scorecard-alignment:R2`, `plan:m365-ma-scorecard-alignment:R5`

## Governing Formula

Let:

- `A` be the declared M365 instruction action set
- `P` be request parameters
- `S` be tenant and runtime state
- `G` be the active governance gates
- `K` be the runtime configuration authority source
- `R` be the instruction response
- `Q` be the audit trace side effect

Define the governing instruction evaluation function:

`Eval : A x P x S x G -> (R, Q)`

Subject to the existing contract constraints:

1. `a ∈ A_impl` implies the action is supported by the runtime contract.
2. `auth_invalid => status(R) = 401`
3. `mutating(a) and mutations_disabled(G) => ok(R) = false and error(R) = "m365_mutations_disabled"`
4. `same(idempotency_key, a, P) and first_success => R_replay = R_first`
5. `execution_completed => exactly_one_audit_record(Q)`
6. `same(a, P, S, G) => same(R, Q)` for the current deterministic contract boundary
7. `tenant_selected(K) => authority(K) = tenant_yaml + injected_secret_env`, and bootstrap dotenv inputs do not override tenant-selected production credentials or org mappings
8. `validation_blockers_cleared => parse(scripts/generate-policies.py) = ok ∧ yaml(governance/invariants/m365/*.yaml) = ok` before broader repo validation may be trusted
9. `scripts_ci_validation_stable => ruff(scripts ∪ scripts/ci) = ok ∧ delta ⊆ (scripts ∪ scripts/ci ∪ MA_traceability_artifacts)` before runtime/tooling validation closure may advance
10. `runtime_cli_notebook_validation_stable => ruff(runtime ∪ cli ∪ governed_tests) = ok ∧ format(runtime ∪ cli ∪ notebooks) = ok ∧ delta ⊆ (runtime ∪ cli ∪ notebooks ∪ governed_tests ∪ MA_traceability_artifacts)` before repo-wide validation may advance to Mypy and final closure
11. `mypy_blockers_remediated => stub_env(yaml) = ok ∧ unique_module(actions_py) = ok ∧ actionable_mypy(governed_path)` before targeted validation closure may advance
12. `approval_contract_aligned => approval_target(selected_tenant) = tenant_contract ∨ env_compat_fallback ∧ approval_auth = tenant_selected_app_only_executor ∧ shell_inputs(C1A) ⊆ {UCP_TENANT, ALLOW_M365_MUTATIONS, ENABLE_AUDIT_LOGGING}` before standalone approval-path readiness may return `GO`
13. `entra_app_roles_finalized => executor_app ≠ operator_identity_app ∧ graph_executor = app_only_executor_app ∧ operator_auth = entra_operator_identity_app ∧ executor_credential_mode ∈ {certificate, certificate_cutover_blocked} ∧ C1A_prereq ⊇ {B5D, B5E}` before standalone enterprise certification may rely on the final SMARTHAUS auth architecture

## Source Mapping

- Intent source: `docs/contracts/caio-m365/INTENT.md`
- Mathematics source: `docs/contracts/caio-m365/MATHEMATICS.md`
- Master calculus source: `docs/contracts/caio-m365/M365_MASTER_CALCULUS.md`
- Capability universe source: `docs/contracts/M365_MASTER_CALCULUS_ACTIONS.md`

## Current Verified Action Surface

The currently implemented and verified runtime action surface is the 9-action set already locked by commercialization `P0A`:

- `list_users`
- `get_user`
- `reset_user_password`
- `list_teams`
- `list_sites`
- `create_site`
- `create_team`
- `add_channel`
- `provision_service`

The broader capability universe remains a contract-universe or roadmap surface, not the current runtime-commercial launch surface.
