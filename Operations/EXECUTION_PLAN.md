# SMARTHAUS AI Workforce — Codex Execution Plan

## Mission & Scope
- Mission: Deliver a production-ready AI Workforce on Microsoft 365 only (SharePoint, Teams, Power Automate, Power Apps, Power BI, Outlook, Azure AD), with 39 agents managed via interactive dashboards and automated cross‑department workflows.
- Scope: Infrastructure setup, agent configuration, interactive dashboards, workflow automation, analytics, testing, security, go‑live, and training — strictly within M365 tooling and this repo’s services.

## Documents Reviewed (order)
- AI_WORKFORCE_PROJECT_TEMPLATE.md
- AI_WORKFORCE_DETAILED_SPECIFICATIONS.md
- AI_WORKFORCE_INTERACTIVE_DASHBOARD_SPECS.md
- AI_WORKFORCE_COMPLETE_IMPLEMENTATION_GUIDE.md

## 5‑Phase Plan (Deliverables)
1) Infrastructure Setup (Weeks 1–2)
   - 10 SharePoint sites + libraries, 10 Teams workspaces + channels, shared mailboxes, Power Platform perms. Baseline dashboards online.
2) Agent Configuration (Weeks 3–6)
   - 39 agents mapped to SharePoint lists/libraries, Teams channels, Outlook rules, Power Automate flows per agent.
3) Interactive Dashboards (Weeks 7–8)
   - Agent overview + detail pages, status telemetry, task assignment, work review, approvals, basic real‑time updates.
4) Automation & Integration (Weeks 9–10)
   - Cross‑department workflows, escalation patterns, Power BI dashboards wired to SharePoint/Graph data.
5) Testing & Go‑Live (Weeks 11–12)
   - Full test suites (unit/integration/perf/security/UAT), production deployment, training, handoff.

## Repo Mapping (Where work lives)
- Provisioning API: `src/provisioning_api/*` (FastAPI, M365 orchestration, routers, status, auth)
- Agent Dashboards: `src/provisioning_api/routers/agent_dashboard.py` + `registry/ai_team.json`, `registry/agents.yaml`
- Graph/M365 Integration: `src/smarthaus_graph/client.py`, `src/provisioning_api/m365_provision.py`
- Ops Adapter (policy, approvals, audit): `src/ops_adapter/*`, `policies/*.rego`, `policies/agents/*.rego`
- Config & Bootstrap: `config/services.json`, `scripts/bootstrap_m365_services.py`, `scripts/ops/*`
- Frontend static build: `src/frontend/*`, `make build-dashboard` → `dist/`
- Auth: `MICROSOFT_OAUTH_SETUP.md`, `api/auth/*`, `src/provisioning_api/auth.py`
- Tests: `tests/*` (FastAPI endpoints, Graph client, OPA policies)

## Environment & Prereqs (M365 only)
- Azure AD App: Tenant, Client ID, Client Secret with Graph App permissions (per MICROSOFT_OAUTH_SETUP.md)
- Env vars:
  - Graph: `GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET`
  - SharePoint: `SP_HOSTNAME` (e.g., smarthausgroup.sharepoint.com)
  - Mutations gate: `ALLOW_M365_MUTATIONS=true` only when ready to provision
  - Optional: `CORS_ORIGINS`, `OPA_URL`, Teams webhook envs for approvals
- CLI/Tools: PowerShell modules (PnP.PowerShell, Microsoft.Graph), OPA CLI (for `policies` tests), Python (uvicorn, pytest), Node/Vercel for dashboard hosting.

## Implementation Checklist (Phase by Phase)
Phase 1 — Infrastructure (Weeks 1–2)
- SharePoint: Create 10 sites and libraries per specs (PnP.PowerShell or Graph)
- Teams: Create 10 workspaces + channels (Graph); confirm in `config/services.json`
- Outlook: Shared mailboxes + rules per roles
- Power Platform: Permissions, solutions scaffolding
- Repo tasks:
  - Verify Graph connectivity: `GET /status` → `m365_connectivity`
  - Dry‑run bootstrap (no mutations): `python scripts/bootstrap_m365_services.py`
  - Enable provisioning once ready: `ALLOW_M365_MUTATIONS=true`

Phase 2 — Agent Configuration (Weeks 3–6)
- Map 39 agents in `registry/ai_team.json` + `registry/agents.yaml`
- Create agent SharePoint lists, Teams channels; wire Outlook rules
- Author baseline Power Automate flows: onboarding, deployment, campaigns, approvals
- Generate/validate OPA policies from registry: `scripts/generate-policies.py`

Phase 3 — Interactive Dashboards (Weeks 7–8)
- Extend `agent_dashboard.py` with status endpoints, task/instruction posts, and work review UI
- Add real‑time updates (SSE/WebSocket) for status/progress where feasible
- Build “Agent Control Panel”, “Work Review”, and “Instruction” interfaces per specs

Phase 4 — Automation & Integration (Weeks 9–10)
- Wire cross‑department workflows via Power Automate + Graph + Ops Adapter approvals
- Implement escalation patterns and notifications (Teams webhooks)
- Publish Power BI reports tied to SharePoint/Graph datasets

Phase 5 — Testing & Go‑Live (Weeks 11–12)
- Run tests: unit (`tests/*`), integration (cross‑dept), perf, security (authZ/RBAC/DLP)
- UAT checklists per department; production deploy; runbooks; training

## Testing Strategy
- Unit: FastAPI endpoints (`tests/test_endpoints.py`), Graph client (`tests/test_graph_client.py`), API health
- Policy: OPA policy decisions (`tests/test_policies.py`, requires `opa`)
- Integration: Cross‑dept flows (onboarding, deployment, campaigns) via API + Flow validation
- Performance: API latency, workflow throughput (per implementation guide targets)
- Security: Auth/MFA, RBAC, DLP, logs, conditional access

## Security & Compliance
- Auth: Azure AD; MFA for admins; sessions per policy
- RBAC: Global Admin, Department Admin, Agent, Guest
- Data: Encryption in transit (TLS 1.3), at rest (M365); Key Vault for secrets
- DLP/Compliance: SharePoint/Teams/Email DLP policies; audit logging; retention policies

## Success Metrics
- Technical: 39 agents live; 99.9% uptime; <2s response; 100% security compliance; workflows automated
- Business: 90% task automation; 50% manual reduction; 95% user satisfaction; zero extra software cost; +25% efficiency

## Immediate Next Actions (Safe to start now)
1) Configure Graph auth (no mutations)
   - Set `GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET`
   - Hit `GET /status` → confirm `m365_connectivity: ok | not_configured_or_unreachable`
2) Validate dashboards locally
   - `make serve-api` → open `/api/agents/dashboard` and `/api/email/dashboard`
3) Validate tests (optional OPA)
   - Run `make test`; if OPA missing, run subset: `pytest -q tests/test_api_health.py tests/test_endpoints.py`
4) Prepare provisioning dry‑run
   - Review `config/services.json`; align with departments; dry‑run `scripts/bootstrap_m365_services.py`
5) Plan Phase 1 provisioning window
   - When ready, enable `ALLOW_M365_MUTATIONS=true` and execute bootstrap + PowerShell site creation

## Integration: Voice → M365 (TAI, MAIA, CAIO, VFE)

**Initiative:** Voice-driven M365 execution (speak to TAI → intent via MAIA → orchestration via CAIO → M365 execution → speak back).

**Master plan (overarching):** `plans/tai-maia-caio-vfe-m365-integration/master-plan.md`

**M365 repo detailed plan:** `plans/tai-maia-caio-vfe-m365-integration/m365-repo-plan.md`

**Reference:** `plan:tai-maia-caio-vfe-m365-integration:m365`

**Status (M365):** ✅ Instruction API implemented and documented (2026-02-06); re-validated against plan/prompt at 2026-02-06 14:07 EST — `plan:tai-maia-caio-vfe-m365-integration:m365`.

**Status (Cross-repo):** ✅ As of 2026-02-06, all five repos are complete for voice→M365 integration; CAIO now wires to VFE for inference-backed M365 draft generation before M365 instruction execution where needed — `plan:tai-maia-caio-vfe-m365-integration`.

Per-repo detailed plans and Codex prompts live in TAI, MAIA, CAIO, and VFE repositories (all plans and two-file prompts created 2026-02-06). Work in each repo follows that repo’s plan and the strictest governance (plan-first, MA process where applicable). No implementation without approved plan and explicit "go."

---

## Integration: TAI Licensed Modular Runtime (Embedded Modules + Entitlements)

**Initiative:** Move from separately managed services toward a one-runtime TAI module model (install/import module + apply license + enable toggle).

**Master plan:** `plans/tai-licensed-modular-runtime/master-plan.md`

**M365 repo detailed plan:** `plans/tai-licensed-modular-runtime/m365-repo-plan.md`

**Reference:** `plan:tai-licensed-modular-runtime:m365`

**Status:** ✅ Complete (2026-02-06) — M365 connector module execution completed for this repo (`m365.module.entrypoint:M365ConnectorModule`) with canonical `m365.instruction.execute` contract, preserved auth/mutation/idempotency/audit behavior via shared instruction executor, targeted module tests, and module contract documentation updates. Plain-language commercial and local test guides were added in `docs/TAI_LICENSED_MODULE_MODEL.md` and `docs/LOCAL_TEST_LICENSED_RUNTIME.md`.

---

## Integration: ChatGPT Custom GPT — M365 Agent Control

**Initiative:** Allow employees to control M365 agents via a ChatGPT Custom GPT (natural language → GPT calls ops adapter API).

**Plan:** `plans/gpt-actions-m365-integration/gpt-actions-m365-integration.md`

**Reference:** `plan:gpt-actions-m365-integration:1`

**Status:** ✅ Complete (2026-02-06) — Plan created; OpenAPI schema and setup README added in `docs/gpt-actions/`. No changes to ops adapter code or registry.

**Deliverables:** `docs/gpt-actions/openapi.yaml`, `docs/gpt-actions/README.md`. See plan for validation and success criteria.

---

## Initiative: M365 AI Workforce Expansion Master Plan

**Initiative:** Expand the bounded standalone SMARTHAUS M365 v1 slice into the full agentic workforce program: all departments, all 39 personas, the full explicitly-inventoried governable M365 capability universe, bounded executors, and Claude -> UCP -> M365 delegation.

**Plan:** `plans/m365-ai-workforce-expansion-master-plan/m365-ai-workforce-expansion-master-plan.md`

**Reference:** `plan:m365-ai-workforce-expansion-master-plan:R1`

**Status:** 🟢 Active — the new expansion master plan triplet and the full MATHS prompt inventory are now in place. `E0A` through `E2D` are complete, `E2E` is the active next act, and `E3` through `E9E` remain planned and blocked by predecessor work.
**Current next act:** `E2E` — expand Word, Excel, and PowerPoint workflows on top of the completed v2 control plane plus the directory, messaging, SharePoint / files, and collaboration / Planner slices.

**Status update (2026-03-20 16:11 EDT):** Created `plans/m365-ai-workforce-expansion-master-plan/` as the new active program with a full phase/child-phase stack `E0` through `E9`, explicit department and workload universe targets, and a complete MATHS prompt pair inventory under `docs/prompts/` for the overview, each grouped phase, and each child act. This new plan follows the now-closed enterprise-readiness master plan and becomes the active critical path for the broader SMARTHAUS AI workforce vision.

**Status update (2026-03-20 16:11 EDT):** `E0A` is complete. The authoritative census is now locked at `39` personas across `10` departments by removing the stray non-authoritative `bonus` department from `registry/ai_team.json`, cross-checking every remaining roster agent ID against `registry/agents.yaml`, and recording the result in `docs/commercialization/m365-department-persona-census.md`. `E0B` is now the active next act.

**Status update (2026-03-20 16:11 EDT):** `E0B` is complete. The workload universe is now locked at the family level in `docs/commercialization/m365-workload-universe-inventory.md`, grounded in official Microsoft workload references plus the repo's current `184`-action registry surface. `E0C` is now the active next act.

**Status update (2026-03-20 16:11 EDT):** `E0C` is complete. The canonical capability taxonomy now exists at `docs/commercialization/m365-capability-taxonomy-and-feasibility-map.md`, explicitly separating implementation status, feasibility class, auth class, and licensing class across the locked workload families. `E0D` is now the active next act.

**Status update (2026-03-20 16:53 EDT):** `E0D` is complete. The workforce now has an explicit structured persona-to-capability map at `registry/persona_capability_map.yaml`, a human-readable risk and approval artifact at `docs/commercialization/m365-persona-capability-and-risk-map.md`, and notebook-backed MA evidence under `L21` proving that the authoritative `39`-persona roster is mapped without silently promoting the extra `20` non-authoritative registry agents. `E0E` is now the active next act.

**Status update (2026-03-20 17:03 EDT):** `E0E` is complete. The program now has a machine-readable release-wave authority at `registry/workforce_release_wave_map.yaml`, a human-readable completion map at `docs/commercialization/m365-workforce-release-wave-and-completion-map.md`, and notebook-backed MA evidence under `L22` proving the workforce can only be claimed complete when all bounded waves `W0` through `W10` are green. `E1A` is now the active next act.

**Status update (2026-03-20 17:12 EDT):** `E1A` is complete. The program now has a machine-readable universal action authority at `registry/universal_action_contract_v2.yaml`, a human-readable canonical contract at `docs/commercialization/m365-universal-action-contract-v2.md`, and notebook-backed `L23` evidence proving the repo's three current action dialects can be projected deterministically into one v2 identity/semantics/execution/governance/evidence envelope. `E1B` is now the active next act.

**Status update (2026-03-20 17:21 EDT):** `E1B` is complete. The program now has a machine-readable routing authority at `registry/executor_routing_v2.yaml`, a shared resolver at `src/smarthaus_common/executor_routing.py`, and notebook-backed `L24` evidence proving canonical v2 keys, legacy exact aliases, and legacy dotted aliases all project deterministically to one bounded executor domain across ops-adapter routing, persona-domain derivation, and instruction-router executor projection. `E1C` is now the active next act.

**Status update (2026-03-20 17:42 EDT):** `E1C` is complete. The program now has a machine-readable auth authority at `registry/auth_model_v2.yaml`, a shared auth resolver at `src/smarthaus_common/auth_model.py`, notebook-backed `L25` evidence, and runtime extraction in `src/ops_adapter/actions.py` so delegated, app-only, and hybrid execution preferences now project deterministically through the shared v2 routing surface for user-context action families. Validation passed with `python3 -m py_compile src/smarthaus_common/auth_model.py src/ops_adapter/actions.py tests/test_auth_model_v2.py`, `PYTHONPATH=src /Users/smarthaus/Projects/GitHub/M365/.venv/bin/pytest -q tests/test_auth_model_v2.py tests/test_executor_routing_v2.py tests/test_env_loading.py` (`23 passed` across the bounded E1C suite and deterministic replay), and `git diff --check`. `E1D` is now the active next act.

**Status update (2026-03-20 17:58 EDT):** `E1D` is complete. The program now has a machine-readable approval and risk authority at `registry/approval_risk_matrix_v2.yaml`, a shared resolver at `src/smarthaus_common/approval_risk.py`, notebook-backed `L26` evidence, and runtime extraction in `src/ops_adapter/main.py` plus `src/ops_adapter/approvals.py` so deterministic `risk_class`, `approval_profile`, approvers, and matrix-enforced fail-closed approval behavior now project through the governed runtime even when legacy OPA approval coverage is incomplete. Validation passed with `python3 -m py_compile src/smarthaus_common/approval_risk.py src/ops_adapter/main.py src/ops_adapter/approvals.py tests/test_approval_risk_v2.py tests/test_ops_adapter.py`, `PYTHONPATH=src pytest -q tests/test_approval_risk_v2.py tests/test_ops_adapter.py -k 'e1d_matrix_forces_pending_approval_when_opa_surface_is_incomplete or actions_returns_pending_approval_for_high_risk_admin_action or group_mapped_actor_binding_is_preserved_in_pending_approval or b7b_preserves_routed_executor_identity_in_pending_approval or sites_provision_is_high_impact_and_requires_approval or groups_list_is_low_risk_without_approval or email_send_bulk_only_requires_approval_above_threshold or security_domain_default_is_critical_and_approval_bearing or persona_profile_fallback_uses_authoritative_persona_map'` (`9 passed`), and `git diff --check`. `E1E` is now the active next act.

**Status update (2026-03-20 18:00 EDT):** `E1E` is complete. The program now has a machine-readable audit authority at `registry/unified_audit_schema_v2.yaml`, a shared runtime builder at `src/smarthaus_common/audit_schema.py`, notebook-backed `L27` evidence, runtime extraction in `src/ops_adapter/audit.py` and `src/provisioning_api/audit.py`, and a refreshed bounded instruction-audit verifier in `scripts/ci/verify_m365_audit.py` with regenerated proof at `configs/generated/m365_audit_verification.json`. Validation passed with `python3 -m py_compile src/smarthaus_common/audit_schema.py src/ops_adapter/audit.py src/provisioning_api/audit.py scripts/ci/verify_m365_audit.py tests/test_audit_schema_v2.py tests/test_ops_adapter.py`, `PYTHONPATH=src pytest -q tests/test_audit_schema_v2.py tests/test_ops_adapter.py -k 'test_build_audit_record_v2_projects_canonical_contexts or test_provisioning_api_log_event_writes_unified_schema or test_admin_audit_log_captures_actor_executor_and_before_after or test_admin_audit_log_can_return_snapshot_context or test_success_audit_log_captures_actor_and_executor_identity'` (`4 passed`), `PYTHONPATH=src python3 scripts/ci/verify_m365_audit.py` (`Audit verification PASSED`), and `git diff --check`. `E2A` is now the active next act.

**Status update (2026-03-20 18:33 EDT):** `E2A` is complete. The workforce-expansion program now has a machine-readable Entra/directory authority at `registry/entra_directory_expansion_v2.yaml`, a human-readable contract at `docs/commercialization/m365-entra-directory-expansion-v2.md`, notebook-backed `L28` evidence, expanded Graph runtime support in `src/smarthaus_graph/client.py`, expanded instruction-router coverage in `src/provisioning_api/routers/m365.py`, aligned CAIO and capability-universe contracts, a bounded verifier at `scripts/ci/verify_entra_directory_expansion.py`, and generated proof at `configs/generated/entra_directory_expansion_verification.json`. Validation passed with `python3 -m py_compile src/smarthaus_graph/client.py src/provisioning_api/routers/m365.py scripts/ci/verify_caio_m365_contract.py scripts/ci/verify_capability_registry.py scripts/ci/verify_entra_directory_expansion.py tests/test_entra_directory_expansion_v2.py`, `PYTHONPATH=src .venv/bin/pytest -q tests/test_entra_directory_expansion_v2.py tests/test_executor_routing_v2.py tests/test_auth_model_v2.py tests/test_approval_risk_v2.py` (`22 passed`), `PYTHONPATH=src python3 scripts/ci/verify_caio_m365_contract.py`, `PYTHONPATH=src python3 scripts/ci/verify_capability_registry.py`, `PYTHONPATH=src python3 scripts/ci/verify_entra_directory_expansion.py` (`PASSED (18 actions)`), and `git diff --check`. `E2B` is now the active next act.

**Status update (2026-03-20 19:21 EDT):** `E2B` is complete. The workforce-expansion program now has a machine-readable Outlook / Exchange authority at `registry/outlook_exchange_expansion_v2.yaml`, a human-readable contract at `docs/commercialization/m365-outlook-exchange-expansion-v2.md`, notebook-backed `L29` evidence, expanded shared Graph runtime support in `src/smarthaus_graph/client.py`, expanded instruction-router coverage in `src/provisioning_api/routers/m365.py`, aligned CAIO and capability-universe contracts for mail, calendar, mailbox, shared-mailbox, and contact actions, a bounded verifier at `scripts/ci/verify_outlook_exchange_expansion.py`, and generated proof at `configs/generated/outlook_exchange_expansion_verification.json`. Validation passed with `python3 -m py_compile src/smarthaus_graph/client.py src/provisioning_api/routers/m365.py scripts/ci/verify_caio_m365_contract.py scripts/ci/verify_capability_registry.py scripts/ci/verify_outlook_exchange_expansion.py tests/test_outlook_exchange_expansion_v2.py`, `PYTHONPATH=src .venv/bin/pytest -q tests/test_outlook_exchange_expansion_v2.py tests/test_executor_routing_v2.py tests/test_auth_model_v2.py tests/test_approval_risk_v2.py` (`21 passed`), `PYTHONPATH=src python3 scripts/ci/verify_caio_m365_contract.py`, `PYTHONPATH=src python3 scripts/ci/verify_capability_registry.py`, `PYTHONPATH=src python3 scripts/ci/verify_outlook_exchange_expansion.py` (`PASSED (20 actions)`), and `git diff --check`. `E2C` is now the active next act.

**Status update (2026-03-20 19:40 EDT):** `E2C` is complete. The workforce-expansion program now has a machine-readable SharePoint / OneDrive / files authority at `registry/sharepoint_onedrive_files_expansion_v2.yaml`, a human-readable contract at `docs/commercialization/m365-sharepoint-onedrive-files-expansion-v2.md`, notebook-backed `L30` evidence, expanded shared Graph runtime support in `src/smarthaus_graph/client.py`, expanded instruction-router coverage in `src/provisioning_api/routers/m365.py`, aligned CAIO and capability-universe contracts for site, list, drive, and drive-item actions, a bounded verifier at `scripts/ci/verify_sharepoint_onedrive_files_expansion.py`, and generated proof at `configs/generated/sharepoint_onedrive_files_expansion_verification.json`. Validation passed with `python3 -m py_compile src/smarthaus_graph/client.py src/provisioning_api/routers/m365.py scripts/ci/verify_sharepoint_onedrive_files_expansion.py tests/test_sharepoint_onedrive_files_expansion_v2.py`, `PYTHONPATH=src .venv/bin/pytest -q tests/test_executor_routing_v2.py tests/test_auth_model_v2.py tests/test_approval_risk_v2.py tests/test_sharepoint_onedrive_files_expansion_v2.py` (`22 passed`), `PYTHONPATH=src python3 scripts/ci/verify_sharepoint_onedrive_files_expansion.py` (`PASSED (11 actions)`), `python3 scripts/ci/verify_capability_registry.py`, `python3 scripts/ci/verify_caio_m365_contract.py`, and `git diff --check`. `E2D` is now the active next act.

**Status update (2026-03-20 20:00 EDT):** `E2D` is complete. The workforce-expansion program now has a machine-readable Teams / Groups / Planner authority at `registry/teams_groups_planner_expansion_v2.yaml`, a human-readable contract at `docs/commercialization/m365-teams-groups-planner-expansion-v2.md`, notebook-backed `L31` evidence, expanded shared Graph runtime support in `src/smarthaus_graph/client.py`, expanded instruction-router coverage in `src/provisioning_api/routers/m365.py`, aligned CAIO and capability-universe contracts for `get_team`, `list_channels`, `create_channel`, `list_plans`, `create_plan`, `list_plan_buckets`, `create_plan_bucket`, and `create_plan_task`, a bounded verifier at `scripts/ci/verify_teams_groups_planner_expansion.py`, and generated proof at `configs/generated/teams_groups_planner_expansion_verification.json`. Validation passed with `python3 -m py_compile src/smarthaus_graph/client.py src/provisioning_api/routers/m365.py scripts/ci/verify_teams_groups_planner_expansion.py tests/test_teams_groups_planner_expansion_v2.py`, `PYTHONPATH=src .venv/bin/pytest -q tests/test_teams_groups_planner_expansion_v2.py tests/test_executor_routing_v2.py tests/test_auth_model_v2.py tests/test_approval_risk_v2.py` (`22 passed`), `PYTHONPATH=src python3 scripts/ci/verify_teams_groups_planner_expansion.py` (`PASSED (8 actions)`), `PYTHONPATH=src python3 scripts/ci/verify_capability_registry.py`, `PYTHONPATH=src python3 scripts/ci/verify_caio_m365_contract.py`, and `git diff --check`. `E2E` is now the active next act.

**Prompt artifacts:** master prompt pair plus grouped-phase and child-act MATHS prompt pairs under `docs/prompts/`

---

## Internal Ops: SmartHaus UCP Setup-Token Delivery Flow

**Reference:** `plan:EXECUTION_PLAN:UCP-TD1`

**Status:** 🟢 Active — bounded internal-only support for UCP Phase 4 cross-repo build and assembly.

**Scope:** Provide the sibling-M365 flow blueprint and runbook that the local
SmartHaus-admin UCP runtime needs for Teams-based setup-token delivery. This is
not public/customer-facing M365 pack work.

**Deliverables:**
- `flows/internal-ops/ucp-setup-token-delivery-flow.json`
- `flows/internal-ops/UCP_SETUP_TOKEN_DELIVERY_FLOW_RUNBOOK.md`
- `flows/README.md` internal-ops flow entry
- `Operations/PROJECT_FILE_INDEX.md` and `Operations/ACTION_LOG.md` support

**Exit boundary:** The artifact and runbook surface exists and UCP docs can
point to it truthfully; live tenant deployment and operator acceptance remain
outside this repo slice.

---

## Initiative: M365 Enterprise Readiness Master Plan (Standalone Module)

**Initiative:** Run the full standalone M365 v1 enterprise-readiness critical path as one governed program: product-boundary lock, runtime hardening, live-tenant certification, and launch readiness.

**Plan:** `plans/m365-enterprise-readiness-master-plan/m365-enterprise-readiness-master-plan.md`

**Reference:** `plan:m365-enterprise-readiness-master-plan:R1`

**Status:** ✅ Complete — foundation `A1` through `A4`, runtime hardening `B1` through `B7E`, live certification `C1A` through `C1D`, release decision `C2`, enterprise collateral `D1`, and pilot acceptance plus customer handoff `D2` are all complete for the current bounded standalone SMARTHAUS M365 v1 repository state. The certified launch scope remains the standalone `9`-action product boundary, and the enterprise-readiness critical path is closed.
**Current next act:** None — the enterprise-readiness master plan is complete for the current repository state.

**Status update (2026-03-19 19:39 EDT):** `B7C1` is complete. The live UCP gate now admits the documented bounded `test_run` and `governance_edit` shapes, `B7D` is the active next act, `B7E` remains blocked by predecessor work, and `C1A` remains blocked only by executor permission minimization and bounded SharePoint-executor approval re-proof.

**Status update (2026-03-19 20:51 EDT):** `B7D` is complete. The live SMARTHAUS tenant now runs with bounded SharePoint, collaboration, and directory executors, the old monolithic executor is demoted to legacy-only status, `B7E` is the active next act, and `C1A` remains blocked only by bounded SharePoint-executor approval re-proof.

**Status update (2026-03-20 06:51 EDT):** `B7E` is complete. The bounded SharePoint executor now returns `200` on both the pinned approvals list metadata and approvals list items routes under the exact standalone shell contract, the `C1A` readiness packet is refreshed to `GO`, and `C1A` is the active next act.

**Status update (2026-03-20 07:09 EDT):** `C1A` is complete. The readiness packet remains `GO`, the exact standalone shell contract and pinned approval backend are now formally accepted as the certification-ready environment, and `C1B` is the active next act pending explicit live-execution approval.

**Status update (2026-03-20 08:05 EDT):** `C1B` is complete and green with retained live transcripts for `list_users`, `get_user`, `list_teams`, and `list_sites`. `C1C` was then executed in the approved live window and is `NO-GO`: `create_site`, `create_team`, and `add_channel` passed, but `provision_service`, `reset_user_password`, the real actor-authenticated JWT path, and approval-record creation failed, so `C1C` is now the active blocker and `C1D` remains blocked.

**Status update (2026-03-20 10:35 EDT):** `provision_service` is re-proved green after notebook-backed service-site detection remediation. The live HR service surface now resolves through the group root site at `/sites/hr2`, so the active remaining `C1C` blockers are `reset_user_password`, the real actor-authenticated JWT path, and the approval-record creation evidence sync.

**Status update (2026-03-20 12:02 EDT):** `C1C` is complete. A dedicated unlicensed validation user (`m365-validation@smarthausgroup.com`) now anchors the password-reset proof, the bounded directory executor now holds the minimum additional privilege and directory role needed for that row, the operator-identity app now exposes `access_as_user` for governed JWT parity, and the live reproofs for `reset_user_password`, real actor-authenticated governed execution, approval create/readback, and approval-linked audit evidence are all green. `C1D` is now the active next act.

**Status update (2026-03-20 14:23 EDT):** `C1D` is complete. The retained `C1A` through `C1C` packet is now mapped into `artifacts/certification/m365-v1-candidate-52ca494/validation_matrix_status.json`, `docs/commercialization/m365-live-tenant-validation-matrix.md` is synchronized to the bounded standalone packet state, and `docs/commercialization/m365-release-gates-and-certification.md` now reflects that the runtime evidence gate is closed. `C2` is now the active next act.

**Status update (2026-03-20 14:45 EDT):** `C2` is complete with an explicit `NO-GO`. The bounded standalone runtime evidence remains green, but `artifacts/certification/m365-v1-candidate-52ca494/sign_off_record.json` is still incomplete for engineering, security, and release-owner sign-off, so `D1` and `D2` remain blocked until a superseding release decision is recorded.

**Status update (2026-03-20 15:00 EDT):** `C2` is superseded to `GO`. Human engineering, security, and release-owner sign-off is now recorded in `artifacts/certification/m365-v1-candidate-52ca494/sign_off_record.json`, the bounded standalone release decision is now green in `release_decision.json`, and `D1` is the active next act while `D2` remains blocked by `D1`.

**Status update (2026-03-20 15:18 EDT):** `D1` is complete. The bounded buyer-facing and delivery-facing collateral pack now exists at `docs/commercialization/m365-enterprise-collateral-pack.md`, keeps product, security, supported-action, and operating-model language inside the certified standalone `9`-action boundary and the existing `C2 GO` release decision, and advances the critical path so `D2` is now the active next act.

**Status update (2026-03-20 15:27 EDT):** `D2` is complete. The bounded pilot acceptance and customer handoff pack now exists at `docs/commercialization/m365-pilot-acceptance-and-customer-handoff.md`, keeps pilot success criteria, acceptance, responsibility, handoff, and sign-off language inside the certified standalone `9`-action boundary and the current operator/support model, and closes the master-plan critical path for this repository state.

**Historical lineage:** `plans/m365-enterprise-commercialization-readiness/m365-enterprise-commercialization-readiness.md` remains for traceability but is now absorbed and no longer the active execution plan.

**Prompt artifacts:** master prompt pair plus full act-level MATHS prompt inventory under `docs/prompts/`

---

## Initiative: M365 MA Scorecard Alignment (Push Unblock)

**Initiative:** Align the repo's existing M365 Mathematical Autopsy evidence to the structural artifact layout required by UCP governance, emit a legitimate aggregate `scorecard.json`, and unblock governed `push` without runtime code changes.

**Plan:** `plans/m365-ma-scorecard-alignment/m365-ma-scorecard-alignment.md`

**Reference:** `plan:m365-ma-scorecard-alignment:R1`

**Status:** ✅ Complete (2026-03-17) — MA bridge documents, projected lemma/invariant/notebook paths, per-lemma scorecards, module scorecard, and aggregate `scorecard.json` have been added in the UCP-required layout. Validation is green: `phase_status` reports phase `9`, `validate_scorecard` reports `green=true`, and `validate_action(push)` now returns `allowed=true`.

**Prompt artifacts:** `docs/prompts/codex-m365-ma-scorecard-alignment.md`, `docs/prompts/codex-m365-ma-scorecard-alignment-prompt.txt`

---

## Initiative: M365 Repo Worktree Cleanup and Separation

**Initiative:** Reduce the current mixed dirty worktree into a safe, reviewable state by removing plaintext secret-bearing artifacts, reverting formatter-only fallout from the failed repo-wide pre-commit run, and separating the remaining substantive payload into explicit keep, split, and delete buckets.

**Plan:** `plans/m365-repo-worktree-cleanup-separation/m365-repo-worktree-cleanup-separation.md`

**Reference:** `plan:m365-repo-worktree-cleanup-separation:R1`

**Status:** ✅ Complete (2026-03-17) — `R1` through `R5` are complete: the cleanup plan and prompt pair were created, the plaintext secret-bearing local docs were removed from the worktree, the formatter-only tracked fallout from the failed repo-wide pre-commit run was reverted, the remaining substantive payload was shipped under explicit user direction, the GitHub push-protection-blocked Azure secret in `create_teams_workspace.py` was replaced with env-driven secret loading, and the rewritten unpushed commit was successfully pushed to `origin/feature/m365-universe-batch2-identity-user-group`. Active execution focus now returns to the integrated master plan at `B1`.

**Prompt artifacts:** `docs/prompts/codex-m365-repo-worktree-cleanup-separation.md`, `docs/prompts/codex-m365-repo-worktree-cleanup-separation-prompt.txt`

---

## Notes
- All M365‑changing operations are gated by `ALLOW_M365_MUTATIONS` and require valid Graph credentials.
- We will not run tenant‑impacting steps without explicit readiness. Dry‑runs and status checks first.
