# SMARTHAUS M365 AI Workforce — Project File Index

**Status:** Baseline initialized on 2026-03-18 under `plan:m365-enterprise-readiness-master-plan:B4A`

This baseline indexes the governance-critical and active enterprise-readiness artifacts first. It satisfies the mandatory file-index baseline required by `B4A`. Broader repo coverage can be expanded in later governance work, but the active critical path now has the required index artifact in place.

## Governance Core

| Path | Purpose | North Star Clause | Execution Plan Reference |
| --- | --- | --- | --- |
| `AGENTS.md` | Repo operating contract for all AI assistants. | `Core Values & Ethos` | `plan:m365-enterprise-readiness-master-plan:R8` |
| `Operations/NORTHSTAR.md` | Repo North Star and commercialization-scope authority reference. | `Mission Statement`, `Commercialization Scope Clarification` | `plan:m365-enterprise-readiness-master-plan:R1` |
| `Operations/EXECUTION_PLAN.md` | Primary execution-plan source of truth. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:R1` |
| `Operations/ACTION_LOG.md` | Granular governed action history. | `Operational Model: Self-Service & Self-Sufficient` | `plan:m365-enterprise-readiness-master-plan:R8` |
| `Operations/PROJECT_FILE_INDEX.md` | File-index governance baseline for active readiness artifacts. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4A` |
| `docs/governance/MATHS_PROMPT_TEMPLATE.md` | Canonical MATHS prompt template for execution acts. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4A` |

## Active Master Plan Artifacts

| Path | Purpose | North Star Clause | Execution Plan Reference |
| --- | --- | --- | --- |
| `plans/m365-enterprise-readiness-master-plan/m365-enterprise-readiness-master-plan.md` | Human-readable active readiness master plan. | `Commercialization Scope Clarification`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:R1` |
| `plans/m365-enterprise-readiness-master-plan/m365-enterprise-readiness-master-plan.yaml` | Structured YAML form of the active readiness master plan. | `Commercialization Scope Clarification`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:R1` |
| `plans/m365-enterprise-readiness-master-plan/m365-enterprise-readiness-master-plan.json` | Structured JSON form of the active readiness master plan. | `Commercialization Scope Clarification`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:R1` |

## Active B5 Identity Architecture Artifacts

| Path | Purpose | North Star Clause | Execution Plan Reference |
| --- | --- | --- | --- |
| `docs/commercialization/m365-entra-identity-and-app-execution-model.md` | Canonical enterprise identity architecture lock for Entra-authenticated SmartHaus users plus app-only Graph execution. | `Policy & Security`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B5A` |

## Active B5B Runtime Identity Enforcement Surface

| Path | Purpose | North Star Clause | Execution Plan Reference |
| --- | --- | --- | --- |
| `src/ops_adapter/main.py` | Governed ops-adapter execution boundary now enforcing JWT-backed actor identity and deterministic fail-closed auth responses on `/actions/*`. | `Policy & Security`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B5B` |
| `src/ops_adapter/app.py` | Legacy app-factory execution path aligned to deny raw header-only actor access unless the explicit non-enterprise override is enabled. | `Policy & Security`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B5B` |
| `tests/test_ops_adapter.py` | Bounded actor-identity enforcement coverage for bearer-token propagation, missing-token denial, and missing-actor-claim denial. | `Core Success Metrics`, `Policy & Security` | `plan:m365-enterprise-readiness-master-plan:B5B` |

## Active B5C Authorization and Audit Binding Surface

| Path | Purpose | North Star Clause | Execution Plan Reference |
| --- | --- | --- | --- |
| `src/smarthaus_common/tenant_config.py` | Tenant-contract tier resolution surface now supporting both direct user mappings and Entra group-to-tier bindings. | `Policy & Security`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B5C` |
| `src/smarthaus_common/permission_enforcer.py` | Shared governed permission surface binding authenticated actors and actor groups to effective tiers and confirmation overrides. | `Policy & Security`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B5C` |
| `src/ops_adapter/approvals.py` | Approval-store surface preserving actor tier, actor groups, tenant, and executor identity metadata in approval records. | `Policy & Security`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B5C` |
| `src/ops_adapter/audit.py` | Audit-entry surface preserving actor, actor tier, actor groups, executor, and tenant metadata on governed runtime and admin events. | `Policy & Security`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B5C` |
| `src/ops_adapter/actions.py` | Admin-action runtime surface now emitting actor-versus-executor admin events with tier and tenant context. | `Policy & Security`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B5C` |

## Active MA / Validation Recovery Artifacts

| Path | Purpose | North Star Clause | Execution Plan Reference |
| --- | --- | --- | --- |
| `docs/ma/phase1_formula.md` | Governing formula for the active MA bridge, now including validation-blocker and scripts/CI tooling-gate constraints. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D2` |
| `docs/ma/phase2_calculus.md` | Calculus and lemma mapping for the active MA bridge, now including `L7` and `L8`. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D2` |
| `docs/ma/lemmas/L7_m365_validation_blocker_recovery.md` | Lemma definition for the blocker-recovery syntax gate. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4C` |
| `docs/ma/lemmas/L8_m365_scripts_ci_ruff_cleanup.md` | Lemma definition for the scripts and CI Ruff-cleanup gate. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D2` |
| `invariants/lemmas/L7_m365_validation_blocker_recovery.yaml` | Machine-enforced invariant metadata for `L7`. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4C` |
| `invariants/lemmas/L8_m365_scripts_ci_ruff_cleanup.yaml` | Machine-enforced invariant metadata for `L8`. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D2` |
| `invariants/lemmas/L9_m365_runtime_cli_notebook_validation_cleanup.yaml` | Machine-enforced invariant metadata for `L9`. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D3` |
| `invariants/lemmas/L10_m365_mypy_stub_module_path_remediation.yaml` | Machine-enforced invariant metadata for `L10`. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4A` |
| `notebooks/m365/INV-M365-I-validation-blocker-recovery.ipynb` | Primary source notebook for the blocker-recovery proof surface. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4C` |
| `notebooks/m365/INV-M365-J-scripts-ci-ruff-cleanup.ipynb` | Primary source notebook for the scripts and CI Ruff-cleanup proof surface. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D2` |
| `notebooks/m365/INV-M365-K-runtime-cli-notebook-cleanup.ipynb` | Primary source notebook for the runtime, CLI, and notebook validation cleanup proof surface. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D3` |
| `notebooks/m365/INV-M365-L-mypy-stub-module-path-remediation.ipynb` | Primary source notebook for the mypy stub and module-path remediation proof surface. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4A` |
| `notebooks/lemma_proofs/L7_m365_validation_blocker_recovery.ipynb` | Projected lemma-proof notebook for `L7`. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4C` |
| `notebooks/lemma_proofs/L8_m365_scripts_ci_ruff_cleanup.ipynb` | Projected lemma-proof notebook for `L8`. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D2` |
| `notebooks/lemma_proofs/L9_m365_runtime_cli_notebook_validation_cleanup.ipynb` | Projected lemma-proof notebook for `L9`. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D3` |
| `notebooks/lemma_proofs/L10_m365_mypy_stub_module_path_remediation.ipynb` | Projected lemma-proof notebook for `L10`. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4A` |
| `artifacts/scorecards/scorecard_l7.json` | Per-lemma scorecard for validation-blocker recovery. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4C` |
| `artifacts/scorecards/scorecard_l8.json` | Per-lemma scorecard for scripts and CI Ruff cleanup. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D2` |
| `artifacts/scorecards/scorecard_l9.json` | Per-lemma scorecard for runtime, CLI, and notebook validation cleanup. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D3` |
| `artifacts/scorecards/scorecard_l10.json` | Per-lemma scorecard for mypy stub and module-path remediation. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4A` |
| `artifacts/scorecards/scorecard_l11.json` | Per-lemma scorecard for certification-environment readiness. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:C1A` |
| `artifacts/scorecards/scorecard_l13.json` | Per-lemma scorecard for SMARTHAUS Entra app separation and executor certificate-cutover linkage. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B5D` |
| `scorecard.json` | Aggregate MA scorecard including `L7` through `L13` linkage. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B5D` |
| `artifacts/b4d1_failure_inventory.json` | Pinned clean-baseline validation inventory for `B4D2` through `B4D4`. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D1` |
| `artifacts/b4d3_failure_inventory.json` | Pinned post-runtime-cleanup failure inventory showing the remaining handoff into `B4D4`. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D3` |
| `artifacts/b4d4_failure_inventory.json` | Pinned actionable mypy inventory after the environment and duplicate-module blockers were removed. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4A` |
| `artifacts/b4d4d_failure_inventory.json` | Stable repo-wide mypy handoff inventory after repeated governed `B4D4D` runs. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4D` |
| `artifacts/b4d5_validation_handoff.json` | Bounded `B4D5` validation closeout and explicit `B4E` blocker inventory after targeted closure. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D5` |
| `artifacts/b4e_full_repo_validation_closure.json` | Authoritative green repo-validation closure for `B4E` after full Ruff, format, Mypy, and pre-commit success. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4E` |
| `docs/ma/lemmas/L9_m365_runtime_cli_notebook_validation_cleanup.md` | Formal lemma narrative for the bounded runtime, CLI, and notebook validation cleanup proof surface. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D3` |
| `docs/ma/lemmas/L10_m365_mypy_stub_module_path_remediation.md` | Formal lemma narrative for the bounded mypy stub and module-path remediation proof surface. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D4A` |
| `docs/ma/lemmas/L11_m365_certification_environment_readiness.md` | Formal lemma narrative for the `C1A` certification-environment readiness gate. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:C1A` |
| `docs/ma/lemmas/L12_m365_approval_contract_alignment.md` | Formal lemma narrative for tenant-backed approval contract alignment and exact-shell approval reachability. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:C1A` |
| `docs/ma/lemmas/L13_m365_entra_app_separation_certificate_cutover.md` | Formal lemma narrative for SMARTHAUS operator-versus-executor app separation and executor certificate-cutover gating. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B5E` |

## Active B5D/B5E App Registration Hardening Artifacts

| Path | Purpose | North Star Clause | Execution Plan Reference |
| --- | --- | --- | --- |
| `docs/commercialization/m365-entra-app-registration-separation-and-certificate-cutover.md` | Canonical SMARTHAUS Azure / Entra cleanup spec for separating the operator-identity app from the executor app and moving the executor to certificate auth. | `Policy & Security`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B5E` |
| `invariants/lemmas/L13_m365_entra_app_separation_certificate_cutover.yaml` | Machine-enforced invariant metadata for `L13`. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B5E` |
| `notebooks/m365/INV-M365-O-entra-app-separation-certificate-cutover.ipynb` | Primary source notebook for the SMARTHAUS app-registration separation and executor certificate-cutover proof surface. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B5E` |
| `notebooks/lemma_proofs/L13_m365_entra_app_separation_certificate_cutover.ipynb` | Projected lemma-proof notebook for `L13`. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B5E` |

## Active C1A Certification Readiness Artifacts

| Path | Purpose | North Star Clause | Execution Plan Reference |
| --- | --- | --- | --- |
| `artifacts/certification/m365-v1-candidate-52ca494/README.md` | Certification packet status for candidate `52ca494`, now carrying the explicit `C1A` `NO-GO` gate and exact standalone shell contract. | `Core Success Metrics`, `Policy & Security` | `plan:m365-enterprise-readiness-master-plan:C1A` |
| `artifacts/certification/m365-v1-candidate-52ca494/prerequisites_report.json` | Deterministic `C1A` readiness report separating tenant/app-contract readiness from the remaining SMARTHAUS Operations site-discovery blocker. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:C1A` |
| `artifacts/certification/m365-v1-candidate-52ca494/operator_checklist.md` | Operator checklist for the approved certification window, exact shell contract, and stop conditions. | `Operational Model: Self-Service & Self-Sufficient`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:C1A` |
| `invariants/lemmas/L11_m365_certification_environment_readiness.yaml` | Machine-enforced invariant metadata for `L11`. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:C1A` |
| `invariants/lemmas/L12_m365_approval_contract_alignment.yaml` | Machine-enforced invariant metadata for `L12`. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:C1A` |
| `notebooks/m365/INV-M365-M-certification-environment-readiness.ipynb` | Primary source notebook for the `C1A` readiness proof surface. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:C1A` |
| `notebooks/m365/INV-M365-N-approval-contract-alignment.ipynb` | Primary source notebook for tenant-backed approval contract alignment and exact-shell reachability checks. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:C1A` |
| `notebooks/lemma_proofs/L11_m365_certification_environment_readiness.ipynb` | Projected lemma-proof notebook for `L11`. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:C1A` |
| `notebooks/lemma_proofs/L12_m365_approval_contract_alignment.ipynb` | Projected lemma-proof notebook for `L12`. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:C1A` |
| `artifacts/scorecards/scorecard_l12.json` | Per-lemma scorecard for approval-contract alignment and exact-shell reachability. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:C1A` |
| `tests/test_approvals.py` | Focused approval-store contract tests proving tenant-backed backend selection and Graph token-provider binding. | `Policy & Security`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:C1A` |

## Active B4D4B Runtime Surface

| Path | Purpose | North Star Clause | Execution Plan Reference |
| --- | --- | --- | --- |
| `src/ops_adapter/actions.py` | Core governed action dispatcher and Graph-backed runtime mutation surface. | `Policy & Security`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D4B` |
| `src/ops_adapter/main.py` | Active ops-adapter HTTP execution boundary for policy, approval, and audit enforcement. | `Policy & Security`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D4B` |
| `src/ops_adapter/audit.py` | Append-only audit envelope and admin-event evidence surface. | `Core Success Metrics`, `Policy & Security` | `plan:m365-enterprise-readiness-master-plan:B4D4B` |
| `src/ops_adapter/approvals.py` | Approval-backend abstraction used by the governed mutation path. | `Policy & Security`, `Operational Model: Self-Service & Self-Sufficient` | `plan:m365-enterprise-readiness-master-plan:B4D4B` |
| `src/ops_adapter/rate_limit.py` | Deterministic rate-limit primitive for the governed execution path. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D4B` |
| `src/smarthaus_common/config.py` | Shared config authority helpers for tenant-selected runtime state. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4B` |
| `src/smarthaus_common/tenant_config.py` | Tenant-scoped configuration loader used by the governed runtime path. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4B` |
| `src/smarthaus_common/permission_enforcer.py` | Fail-closed user-tier enforcement boundary. | `Policy & Security`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4B` |
| `src/smarthaus_graph/client.py` | Typed Graph client bridge for the governed M365 execution path, now carrying valid PEM certificate-auth support for the executor cutover. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B5E` |
| `tests/test_graph_client.py` | Bounded graph-client validation for organization reads and PEM certificate-credential parsing. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B5E` |
| `src/smarthaus_cli/repo_analyzer.py` | Typed repository analyzer used by the bounded CLI analyzer surface in `B4D4B`. | `Operational Model: Self-Service & Self-Sufficient`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4B` |
| `src/smarthaus_cli/__main__.py` | CLI entrypoint carrying the duplicated analyzer surface remediated in `B4D4B`. | `Operational Model: Self-Service & Self-Sufficient`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4B` |

## Active B4D4C Dashboard, Script, and Test Surface

| Path | Purpose | North Star Clause | Execution Plan Reference |
| --- | --- | --- | --- |
| `src/provisioning_api/simple_dashboard.py` | Legacy standalone dashboard surface remediated for bounded typing closure. | `Operational Model: Self-Service & Self-Sufficient`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4C` |
| `src/provisioning_api/routers/agent_dashboard.py` | Agent dashboard router surface remediated for bounded typing closure. | `Operational Model: Self-Service & Self-Sufficient`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4C` |
| `src/provisioning_api/business_operations.py` | Business operations dashboard surface remediated for bounded typing closure. | `Operational Model: Self-Service & Self-Sufficient`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4C` |
| `src/provisioning_api/agent_workstation.py` | Agent workstation UI surface remediated for bounded typing closure. | `Operational Model: Self-Service & Self-Sufficient`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4C` |
| `src/provisioning_api/agent_command_center.py` | Agent command center UI surface remediated for bounded typing closure. | `Operational Model: Self-Service & Self-Sufficient`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4C` |
| `src/provisioning_api/automation/lattice_repo_documentation_automation.py` | Documentation automation surface remediated for bounded typing closure. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4C` |
| `src/provisioning_api/routers/email_dashboard.py` | Email dashboard router surface remediated for bounded typing closure. | `Operational Model: Self-Service & Self-Sufficient`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4C` |
| `src/provisioning_api/unified_dashboard.py` | Unified dashboard surface remediated for bounded typing closure. | `Operational Model: Self-Service & Self-Sufficient`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4C` |
| `src/provisioning_api/enterprise_dashboard.py` | Enterprise dashboard surface remediated for bounded typing closure. | `Operational Model: Self-Service & Self-Sufficient`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4C` |
| `scripts/check_env_credentials.py` | Credential-check helper remediated for bounded typing closure. | `Operational Model: Self-Service & Self-Sufficient`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4C` |
| `scripts/get_group_ids.py` | Group-ID discovery helper remediated for bounded typing closure. | `Operational Model: Self-Service & Self-Sufficient`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4C` |
| `scripts/teams_finalize.py` | Teams finalization helper remediated for bounded typing closure. | `Operational Model: Self-Service & Self-Sufficient`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4C` |
| `scripts/upload_docx_to_team_site.py` | Docx upload helper remediated for bounded typing closure. | `Operational Model: Self-Service & Self-Sufficient`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4C` |
| `scripts/provision_mcp_registration.py` | SharePoint provisioning helper remediated for bounded typing closure. | `Operational Model: Self-Service & Self-Sufficient`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4C` |
| `tests/test_policies.py` | Policy test surface remediated for bounded typing closure. | `Policy & Security`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4D4C` |

## Active Overview Prompt Artifacts

| Path | Purpose | North Star Clause | Execution Plan Reference |
| --- | --- | --- | --- |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan.md` | Active control-plane overview prompt for the readiness program. | `Commercialization Scope Clarification`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:R8` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-prompt.txt` | Kick-off pointer for the active master-plan overview prompt. | `Commercialization Scope Clarification`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:R8` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-c1-live-tenant-certification-execution.md` | Historical coordination overview for `C1`, retained to point execution to `C1A` through `C1D`. | `Commercialization Scope Clarification`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:R8` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-c1-live-tenant-certification-execution-prompt.txt` | Kick-off pointer for the historical `C1` coordination overview prompt. | `Commercialization Scope Clarification`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:R8` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4d-ruff-black-mypy-remediation.md` | Coordination overview for grouped phase `B4D`, retained to point execution to `B4D1` through `B4D5`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:R8` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4d-ruff-black-mypy-remediation-prompt.txt` | Kick-off pointer for the `B4D` coordination overview prompt. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:R8` |

## Active Act Prompt Artifacts

| Path | Purpose | North Star Clause | Execution Plan Reference |
| --- | --- | --- | --- |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-a1-product-boundary-positioning.md` | MATHS prompt for act `A1`. | `Commercialization Scope Clarification` | `plan:m365-enterprise-readiness-master-plan:A1` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-a1-product-boundary-positioning-prompt.txt` | Kick-off pointer for act `A1`. | `Commercialization Scope Clarification` | `plan:m365-enterprise-readiness-master-plan:A1` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-a2-canonical-config-auth-posture.md` | MATHS prompt for act `A2`. | `Commercialization Scope Clarification` | `plan:m365-enterprise-readiness-master-plan:A2` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-a2-canonical-config-auth-posture-prompt.txt` | Kick-off pointer for act `A2`. | `Commercialization Scope Clarification` | `plan:m365-enterprise-readiness-master-plan:A2` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-a3-governance-boundary-certification-model.md` | MATHS prompt for act `A3`. | `Commercialization Scope Clarification`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:A3` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-a3-governance-boundary-certification-model-prompt.txt` | Kick-off pointer for act `A3`. | `Commercialization Scope Clarification`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:A3` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-a4-packaging-operator-model.md` | MATHS prompt for act `A4`. | `Operational Model: Self-Service & Self-Sufficient` | `plan:m365-enterprise-readiness-master-plan:A4` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-a4-packaging-operator-model-prompt.txt` | Kick-off pointer for act `A4`. | `Operational Model: Self-Service & Self-Sufficient` | `plan:m365-enterprise-readiness-master-plan:A4` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b1-runtime-config-authority-remediation.md` | Active MATHS prompt for act `B1`. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B1` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b1-runtime-config-authority-remediation-prompt.txt` | Kick-off pointer for act `B1`. | `Technical Architecture`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B1` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b2-fail-closed-governance-approval-remediation.md` | Active MATHS prompt for act `B2`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B2` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b2-fail-closed-governance-approval-remediation-prompt.txt` | Kick-off pointer for act `B2`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B2` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b3-admin-audit-evidence-remediation.md` | Active MATHS prompt for act `B3`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B3` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b3-admin-audit-evidence-remediation-prompt.txt` | Kick-off pointer for act `B3`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B3` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4a-governance-baseline-alignment.md` | Active MATHS prompt for act `B4A`. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4A` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4a-governance-baseline-alignment-prompt.txt` | Kick-off pointer for act `B4A`. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4A` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4b-prompt-system-regeneration.md` | Active MATHS prompt for act `B4B`. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4B` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4b-prompt-system-regeneration-prompt.txt` | Kick-off pointer for act `B4B`. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4B` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4c-validation-blockers-syntax-recovery.md` | Active MATHS prompt for act `B4C`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4C` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4c-validation-blockers-syntax-recovery-prompt.txt` | Kick-off pointer for act `B4C`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4C` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4d1-spillover-reset-failure-inventory.md` | Active MATHS prompt for act `B4D1`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D1` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4d1-spillover-reset-failure-inventory-prompt.txt` | Kick-off pointer for act `B4D1`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D1` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4d2-scripts-ci-ruff-cleanup.md` | Active MATHS prompt for act `B4D2`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D2` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4d2-scripts-ci-ruff-cleanup-prompt.txt` | Kick-off pointer for act `B4D2`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D2` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4d3-runtime-cli-ruff-black-cleanup.md` | Active MATHS prompt for act `B4D3`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D3` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4d3-runtime-cli-ruff-black-cleanup-prompt.txt` | Kick-off pointer for act `B4D3`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D3` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4d4-mypy-stub-module-path-remediation.md` | Active MATHS prompt for act `B4D4`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D4` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4d4-mypy-stub-module-path-remediation-prompt.txt` | Kick-off pointer for act `B4D4`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D4` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4d4a-typing-env-module-path-unblock.md` | Active MATHS prompt for act `B4D4A`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D4A` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4d4a-typing-env-module-path-unblock-prompt.txt` | Kick-off pointer for act `B4D4A`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D4A` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4d4b-core-runtime-governance-mypy-remediation.md` | Active MATHS prompt for act `B4D4B`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D4B` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4d4b-core-runtime-governance-mypy-remediation-prompt.txt` | Kick-off pointer for act `B4D4B`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D4B` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4d4c-dashboard-script-test-mypy-remediation.md` | Active MATHS prompt for act `B4D4C`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D4C` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4d4c-dashboard-script-test-mypy-remediation-prompt.txt` | Kick-off pointer for act `B4D4C`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D4C` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4d4d-targeted-mypy-closure.md` | Active MATHS prompt for act `B4D4D`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D4D` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4d4d-targeted-mypy-closure-prompt.txt` | Kick-off pointer for act `B4D4D`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D4D` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4d5-targeted-validation-closure.md` | Active MATHS prompt for act `B4D5`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D5` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4d5-targeted-validation-closure-prompt.txt` | Kick-off pointer for act `B4D5`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B4D5` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4e-full-repo-validation-closure.md` | Active MATHS prompt for act `B4E`. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4E` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4e-full-repo-validation-closure-prompt.txt` | Kick-off pointer for act `B4E`. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B4E` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b5a-identity-architecture-lock.md` | Active MATHS prompt for act `B5A`. | `Technical Architecture`, `Policy & Security` | `plan:m365-enterprise-readiness-master-plan:B5A` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b5a-identity-architecture-lock-prompt.txt` | Kick-off pointer for act `B5A`. | `Technical Architecture`, `Policy & Security` | `plan:m365-enterprise-readiness-master-plan:B5A` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b5b-runtime-identity-enforcement.md` | Active MATHS prompt for act `B5B`. | `Technical Architecture`, `Policy & Security` | `plan:m365-enterprise-readiness-master-plan:B5B` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b5b-runtime-identity-enforcement-prompt.txt` | Kick-off pointer for act `B5B`. | `Technical Architecture`, `Policy & Security` | `plan:m365-enterprise-readiness-master-plan:B5B` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b5c-authorization-audit-binding.md` | Active MATHS prompt for act `B5C`. | `Policy & Security`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B5C` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b5c-authorization-audit-binding-prompt.txt` | Kick-off pointer for act `B5C`. | `Policy & Security`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:B5C` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b5d-entra-app-registration-role-separation.md` | Active MATHS prompt for act `B5D`. | `Policy & Security`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B5D` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b5d-entra-app-registration-role-separation-prompt.txt` | Kick-off pointer for act `B5D`. | `Policy & Security`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B5D` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b5e-executor-certificate-cutover-tenant-contract-finalization.md` | Active MATHS prompt for act `B5E`. | `Policy & Security`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B5E` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-b5e-executor-certificate-cutover-tenant-contract-finalization-prompt.txt` | Kick-off pointer for act `B5E`. | `Policy & Security`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:B5E` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-c1a-certification-environment-readiness.md` | Active MATHS prompt for act `C1A`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:C1A` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-c1a-certification-environment-readiness-prompt.txt` | Kick-off pointer for act `C1A`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:C1A` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-c1b-live-read-only-certification.md` | Active MATHS prompt for act `C1B`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:C1B` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-c1b-live-read-only-certification-prompt.txt` | Kick-off pointer for act `C1B`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:C1B` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-c1c-live-mutation-governance-certification.md` | Active MATHS prompt for act `C1C`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:C1C` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-c1c-live-mutation-governance-certification-prompt.txt` | Kick-off pointer for act `C1C`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:C1C` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-c1d-evidence-packet-matrix-closure.md` | Active MATHS prompt for act `C1D`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:C1D` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-c1d-evidence-packet-matrix-closure-prompt.txt` | Kick-off pointer for act `C1D`. | `Core Success Metrics`, `Technical Architecture` | `plan:m365-enterprise-readiness-master-plan:C1D` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-c2-release-certification-packet-decision.md` | Active MATHS prompt for act `C2`. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:C2` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-c2-release-certification-packet-decision-prompt.txt` | Kick-off pointer for act `C2`. | `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:C2` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-d1-enterprise-collateral-pack.md` | Active MATHS prompt for act `D1`. | `Commercialization Scope Clarification`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:D1` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-d1-enterprise-collateral-pack-prompt.txt` | Kick-off pointer for act `D1`. | `Commercialization Scope Clarification`, `Core Success Metrics` | `plan:m365-enterprise-readiness-master-plan:D1` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-d2-pilot-acceptance-customer-handoff.md` | Active MATHS prompt for act `D2`. | `Operational Model: Self-Service & Self-Sufficient` | `plan:m365-enterprise-readiness-master-plan:D2` |
| `docs/prompts/codex-m365-enterprise-readiness-master-plan-d2-pilot-acceptance-customer-handoff-prompt.txt` | Kick-off pointer for act `D2`. | `Operational Model: Self-Service & Self-Sufficient` | `plan:m365-enterprise-readiness-master-plan:D2` |
