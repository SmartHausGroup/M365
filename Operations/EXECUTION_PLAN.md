# SmartHaus AI Workforce — Codex Execution Plan

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

## Initiative: M365 Enterprise Commercialization Readiness (Standalone Module)

**Initiative:** Convert the current M365 capability into a commercially honest, enterprise-ready standalone deterministic module with a narrow supported v1 surface, canonical production configuration, explicit governance posture, live acceptance evidence, and buyer-ready packaging.

**Plan:** `plans/m365-enterprise-commercialization-readiness/m365-enterprise-commercialization-readiness.md`

**Reference:** `plan:m365-enterprise-commercialization-readiness:R1`

**Status:** 🟡 `P0A`, `P0B`, `P1A`, `P1B`, `P2A`, and `P2B` complete (2026-03-17); `P3A` next — Standalone M365 v1 commercialization is fail-closed to the 9 router-implemented actions documented in `docs/commercialization/m365-v1-supported-surface.md`, the buyer/operator/deployment model is defined in `docs/commercialization/m365-v1-positioning-and-north-star-delta.md`, the canonical production config target is defined in `docs/commercialization/m365-canonical-config-contract.md`, the migration/auth posture is defined in `docs/commercialization/m365-config-migration-and-auth-policy.md`, the audit/governance evidence boundary is defined in `docs/commercialization/m365-audit-and-governance-evidence-model.md`, and the permission/approval/fail-closed boundary is now defined in `docs/commercialization/m365-permission-approval-fail-closed-hardening.md`. The repo now explicitly documents that permission tiers and ops-adapter approvals exist, but permissive tier fallbacks, OPA fail-open paths, and approval-less instruction-API mutations remain hardening gaps rather than enterprise-ready claims. Remaining execution units are `P3A` live-tenant validation matrix, `P3B` release gates/certification model, `P4A` packaging/install/bootstrap, `P4B` onboarding/runbooks/support boundary, `P5A` enterprise collateral pack, and `P5B` pilot acceptance/customer handoff.

**Prompt artifacts:** umbrella prompt pair plus per-subphase MATHS prompt pairs under `docs/prompts/`

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

**Status:** ✅ Complete (2026-03-17) — `R1` through `R5` are complete: the cleanup plan and prompt pair were created, the plaintext secret-bearing local docs were removed from the worktree, the formatter-only tracked fallout from the failed repo-wide pre-commit run was reverted, the remaining substantive payload was shipped under explicit user direction, the GitHub push-protection-blocked Azure secret in `create_teams_workspace.py` was replaced with env-driven secret loading, and the rewritten unpushed commit was successfully pushed to `origin/feature/m365-universe-batch2-identity-user-group`. The next active commercialization unit remains `P1B`.

**Prompt artifacts:** `docs/prompts/codex-m365-repo-worktree-cleanup-separation.md`, `docs/prompts/codex-m365-repo-worktree-cleanup-separation-prompt.txt`

---

## Notes
- All M365‑changing operations are gated by `ALLOW_M365_MUTATIONS` and require valid Graph credentials.
- We will not run tenant‑impacting steps without explicit readiness. Dry‑runs and status checks first.
