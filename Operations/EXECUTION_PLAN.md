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

## Initiative: M365 Enterprise Readiness Master Plan (Standalone Module)

**Initiative:** Run the full standalone M365 v1 enterprise-readiness critical path as one governed program: product-boundary lock, runtime hardening, live-tenant certification, and launch readiness.

**Plan:** `plans/m365-enterprise-readiness-master-plan/m365-enterprise-readiness-master-plan.md`

**Reference:** `plan:m365-enterprise-readiness-master-plan:R1`

**Status:** 🟡 Imported foundation `A1` through `A4` and runtime hardening `B1`, `B2`, and `B3` complete (2026-03-17); governance baseline alignment `B4A`, prompt regeneration `B4B`, validation-blocker recovery `B4C`, spillover reset plus failure-inventory pin `B4D1`, scripts plus CI Ruff cleanup `B4D2`, runtime plus CLI plus notebook Ruff/Black cleanup `B4D3`, typing env plus module-path unblock `B4D4A`, core runtime plus governance mypy remediation `B4D4B`, dashboard plus script plus test mypy remediation `B4D4C`, targeted mypy closure `B4D4D`, targeted validation closure `B4D5`, full repo validation closure `B4E`, identity architecture lock `B5A`, runtime identity enforcement `B5B`, and authorization plus audit binding `B5C` complete (2026-03-18); Entra app-registration role separation `B5D`, executor certificate cutover `B5E`, digital-employee architecture `B6A` through `B6E`, tenant-contract executor-registry extension `B7A`, runtime executor routing `B7B`, persona-registry integration `B7C`, MCP constraint-contract repair `B7C1`, executor permission minimization plus Azure cleanup `B7D`, and approval-backend reproof plus certification re-readiness `B7E` complete (2026-03-20); `C1A` is now the active next act because the bounded SharePoint-executor approval re-proof is green under the exact standalone shell contract, and the live certification path may resume on the rebased multi-executor runtime — The repo has already locked the narrow 9-action supported surface, buyer/operator boundary, canonical config contract, governance/evidence model, release-gate model, packaging path, post-install operator model, digital-employee operating model, capability matrix, executor-domain routing model, persona-registry contract, and certification rebase docs in `docs/commercialization/`. `B1` turned the config contract into real runtime behavior by establishing local MA phase resolution for governed edits, making `UCP_TENANT`-selected tenant YAML the shared config authority, extending tenant discovery to the sibling `UCP/tenants` directory, and demoting dotenv loading to bootstrap-only across the standalone server and legacy dashboards. `B2` then hardened the active ops-adapter and shared permission-enforcement path so missing identity, missing tenant selection, missing tenant config, missing permission tiers, denied OPA decisions, and missing approval-owner configuration fail closed by default, and expanded explicit approval coverage for high-risk `m365-administrator` mutations. `B3` replaced `admin.audit_log` snapshot-mode behavior with append-only admin/configuration events for the active ops-adapter request path and aligned the admin dispatcher with the registry contract. `B4A` corrected the active master plan, execution trackers, MATHS prompt template, and created the required `Operations/PROJECT_FILE_INDEX.md` baseline so the repo is back on an AGENTS-compliant governance footing. `B4B` regenerated the active MATHS prompt inventory so the overview plus every act `A1` through `D2` now has one formal prompt pair under `docs/prompts/`. `B4C` added `L7` notebook-backed evidence for blocker recovery, fixed the Python parse bug in `scripts/generate-policies.py`, corrected the malformed governance invariants in `governance/invariants/m365/`, and closed the hard blocker surface with targeted `py_compile`, YAML-load, `black`, and `check-yaml` validation. `B4D1` restored the worktree to the approved post-`B4C` baseline after the repo-wide pre-commit inventory run, pinned the remaining failure set in `artifacts/b4d1_failure_inventory.json`, and made explicit that notebook formatting and one notebook syntax failure are still part of the repo-wide validation surface. `B4D2` then added notebook-backed `L8` traceability for the scripts and CI tooling surface, eliminated the pinned Ruff debt under `scripts/` and `scripts/ci/`, and validated the bounded cleanup with `ruff check`, `python3 -m py_compile`, and `git diff --check`. `B4D3` added notebook-backed `L9` traceability for the runtime, CLI, and notebook validation surface, eliminated the remaining targeted Ruff debt under `src/ops_adapter/`, `src/provisioning_api/`, `src/smarthaus_cli/`, and `tests/test_policies.py`, fixed the notebook formatter parse blocker in `notebooks/ma_m365_batch1_groups.ipynb`, stabilized targeted formatting across the governed runtime and notebook surface, and validated the bounded cleanup with targeted `ruff check`, `ruff format --check`, and `git diff --check`. `B4D4A` then added `types-PyYAML` to the governed mypy hook and repo dev dependency set, removed duplicate module discovery for `src/ops_adapter/actions.py`, and exposed the real mypy inventory at `283` errors across `47` files; `B4D4B` reduced the bounded core mypy surface from `90` errors across `11` files to green by tightening the governed runtime, config, graph-client, and CLI-analyzer typing surfaces with targeted `pre-commit run mypy --files ...`, `python3 -m py_compile`, and `git diff --check`; `B4D4C` reduced the remaining dashboard, script, and test typing surface from `126` errors across `15` files to green by tightening the legacy `src/provisioning_api/` dashboards, the bounded standalone scripts under `scripts/`, and the policy test surface with one full bounded `pre-commit run mypy --files ...` pass and `git diff --check`; `B4D4D` then proved the repo-wide mypy remainder is deterministic for handoff by running `pre-commit run mypy --all-files` twice under approved `test_run` validation and confirming the same `67` errors across `21` files both times, now pinned in `artifacts/b4d4d_failure_inventory.json`; `B4D5` closed the bounded `B4D` validation surface with green targeted Ruff, formatter, Mypy, and diff checks while capturing the current `B4E` handoff inventory in `artifacts/b4d5_validation_handoff.json`, which showed repo-wide format green, repo-wide Ruff down to `26` issues, and repo-wide mypy down to `5` errors across `5` files; and `B4E` then cleared the full repo-wide gate with passing `ruff check .`, `ruff format --check .`, `PYTHONPATH=src pre-commit run mypy --all-files`, `pre-commit run --all-files`, and `git diff --check`, recorded in `artifacts/b4e_full_repo_validation_closure.json`. `B5A` then locked the SMARTHAUS enterprise identity model in `docs/commercialization/m365-entra-identity-and-app-execution-model.md` by separating Entra-authenticated human actors from the tenant-selected app-only Graph executor and syncing the related commercialization and certification docs to that architecture. `B5B` then enforced JWT-backed actor identity on the governed ops-adapter path in `src/ops_adapter/main.py`, aligned the legacy `src/ops_adapter/app.py` path to deny raw header-only actor access unless the explicit non-enterprise override is enabled, propagated the validated actor identity through the action request boundary, corrected the middleware fail-closed response path so auth errors return deterministic JSON responses instead of leaking ASGI exceptions, and validated the bounded enforcement surface with `python3 -m py_compile`, `PYTHONPATH=src pytest -q tests/test_ops_adapter.py tests/test_policies.py`, and `git diff --check`. `B5C` then bound the authenticated SMARTHAUS actor into tier resolution, approvals, and actor-versus-executor audit semantics by adding group-aware tier resolution in `src/smarthaus_common/tenant_config.py` and `src/smarthaus_common/permission_enforcer.py`, preserving actor tier, actor groups, tenant, and executor identity metadata in `src/ops_adapter/main.py`, `src/ops_adapter/app.py`, `src/ops_adapter/approvals.py`, `src/ops_adapter/audit.py`, and `src/ops_adapter/actions.py`, and validating the bounded binding surface with `python3 -m py_compile`, `PYTHONPATH=src pytest -q tests/test_ops_adapter.py tests/test_policies.py`, and `git diff --check`. `B5D` then completed the live Azure / Entra role split by renaming app `720788ac-1485-4073-b0c8-1a6294819a87` to `SMARTHAUS M365 Executor`, renaming app `e6fd71d3-4116-401e-a4f1-b2fda4318a8b` to `SMARTHAUS M365 Operator Identity`, pruning Graph delegated scopes from the executor app, pruning Graph application roles from the operator-identity app, and setting `Application ID URI = api://e6fd71d3-4116-401e-a4f1-b2fda4318a8b` on the operator-identity app. `B5E` then fixed the runtime certificate path handling in `src/smarthaus_graph/client.py`, generated the SMARTHAUS executor PEM under `/Users/smarthaus/.ucp/certs/`, appended the public certificate to the executor app, updated the tenant contract to certificate-first auth with an empty client secret, validated non-mutating Graph execution after cutover, and retired the executor password credentials. `B6A` through `B6E` then formalized the operator-facing digital-employee model, the full capability/API/license/auth matrix, the bounded executor-domain and minimum-permission model, the persona-registry and humanized delegation contract, and the certification rebase away from the legacy single-executor posture. `B7A` then extended `src/smarthaus_common/tenant_config.py` so the tenant contract can represent explicit bounded executors and executor-routing metadata while deterministically projecting one default executor back into the legacy root auth fields; preserved the shared config authority path through `AppConfig().graph`; and added bounded contract tests in `tests/test_env_loading.py` and `tests/test_approvals.py` to prove legacy single-executor synthesis, explicit default-executor projection, and fail-closed multi-executor default resolution. `B7B` then implemented deterministic action-to-executor routing in `src/ops_adapter/actions.py`, `src/ops_adapter/main.py`, `src/ops_adapter/app.py`, and `src/ops_adapter/approvals.py`, routing approvals through the SharePoint executor path while preserving actor-based approval and audit semantics, and validated that bounded surface with `python3 -m py_compile`, `PYTHONPATH=src pytest -q tests/test_approvals.py tests/test_ops_adapter.py`, and `git diff --check`. `B7C` then integrated a deterministic persona registry derived from `registry/ai_team.json` and `registry/agents.yaml` into `src/ops_adapter/personas.py`, `src/ops_adapter/main.py`, `src/ops_adapter/app.py`, and `src/ops_adapter/approvals.py`, allowing named digital employees to resolve to one canonical runtime agent while preserving persona context through policy, approval, and audit payloads and failing closed on inactive persona targets or bounded-domain mismatches; the bounded surface validated with `python3 -m py_compile`, `PYTHONPATH=src pytest -q tests/test_ops_adapter.py tests/test_approvals.py`, and `git diff --check`. `B7C1` then closed the governance metadata blocker by documenting the accepted live `validate_action` contract for bounded `test_run`, `command_exec`, and `governance_edit` shapes and proving that contract against the live UCP gate. `B7D` then created bounded SharePoint, collaboration, and directory executor apps with certificate-backed credentials, repaired the missing Graph app-role assignments for the SharePoint and directory service principals, demoted the old monolithic executor to `SMARTHAUS Legacy M365 Executor`, cut the active tenant contract over to the bounded SharePoint default, updated the supported v1 provisioning and router surfaces to project bounded executors deterministically, and re-proved live app-only SharePoint, collaboration, and directory access with exact bounded role sets and `200` responses. `B7E` then re-proved the approval backend through the bounded SharePoint executor under the exact standalone shell contract, returning `200` on both the pinned approvals list metadata route and the pinned approvals list items route without URL-based site discovery, refreshed the `C1A` readiness packet to `GO`, and reopened the live certification path on the rebased multi-executor runtime. CAIO is out of scope for this standalone M365 certification path.

**Status update (2026-03-19 19:39 EDT):** `B7C1` is complete. The live UCP gate now admits the documented bounded `test_run` and `governance_edit` shapes, `B7D` is the active next act, `B7E` remains blocked by predecessor work, and `C1A` remains blocked only by executor permission minimization and bounded SharePoint-executor approval re-proof.

**Status update (2026-03-19 20:51 EDT):** `B7D` is complete. The live SMARTHAUS tenant now runs with bounded SharePoint, collaboration, and directory executors, the old monolithic executor is demoted to legacy-only status, `B7E` is the active next act, and `C1A` remains blocked only by bounded SharePoint-executor approval re-proof.

**Status update (2026-03-20 06:51 EDT):** `B7E` is complete. The bounded SharePoint executor now returns `200` on both the pinned approvals list metadata and approvals list items routes under the exact standalone shell contract, the `C1A` readiness packet is refreshed to `GO`, and `C1A` is the active next act.

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
