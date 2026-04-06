# Plan: M365 Direct Runtime Readiness Remediation

## Section 1: Plan Header

- **Plan ID:** `plan:m365-direct-runtime-readiness-remediation`
- **Parent Plan ID:** `none`
- **Title:** `Repair the repo-direct M365 runtime so representative functions can be tested truthfully`
- **Version:** `1.0`
- **Status:** `complete`
- **Owner:** `SMARTHAUS`
- **Date Created:** `2026-04-06`
- **Date Updated:** `2026-04-06`
- **North Star Ref:** `Operations/NORTHSTAR.md`
- **Execution Plan Ref:** `Operations/EXECUTION_PLAN.md § Initiative: M365 Direct Runtime Readiness Remediation`
- **Domain:** `infrastructure`
- **Math/Algorithm Scope:** `false`

## Section 2: North Star Alignment

- **Source:** `Operations/NORTHSTAR.md`
- **Principles served:**
  - `M365-only tooling with truthful native execution`
  - `Self-service posture with direct local validation before broader integration claims`
  - `Fail-closed security, actor identity, and permission enforcement on governed action paths`
- **Anti-alignment:**
  - `Does NOT widen scope into UCP runtime changes`
  - `Does NOT weaken actor identity or permission enforcement to force green`
  - `Does NOT relabel local import, routing, or harness defects as Microsoft tenant failures`

## Section 3: Intent Capture

- **User's stated requirements:**
  - `Make the repo-direct runtime actually testable end-to-end instead of stopping at partial smoke checks`
  - `Fix whatever needs to be fixed under the repo rules and governance`
  - `Reach a state where representative functions like email, Teams/calendar, SharePoint, and Power Automate can be tested directly`
- **Intent doc ref:** `captured in this plan`
- **Intent verification:** `R0 through R5 define the bounded direct-runtime readiness and repair path required before truthful direct function testing can be claimed.`

## Section 4: Objective

- **Objective:** Repair the repo-direct runtime so the top-level instruction API, the lower-level ops adapter, executor routing, and a truthful local direct-test harness are all usable for representative M365 function tests.
- **Current state:** The repo-direct runtime now starts cleanly, all allowed actions in `registry/agents.yaml` route deterministically through `registry/executor_routing_v2.yaml`, and representative direct function tests no longer fail because of local import or routing defects.
- **Target state:** The repo-direct runtime starts cleanly, representative governed actions no longer fail because of local import or routing defects, and direct function tests either succeed or fail only for truthful external reasons such as missing tenant credentials, actor tier, Microsoft permission boundaries, or missing local admin modules.

## Section 5: Scope

### In scope (conceptual)

- repair direct repo runtime import and entrypoint failures
- repair bounded executor-routing parity defects that block representative direct action execution
- add or update focused regression coverage for the direct runtime path
- create one truthful direct-test harness and diagnostics surface for repeated local function testing
- run representative direct tests across core M365 function families

### Out of scope (conceptual)

- UCP runtime or caller changes
- tenant-side Microsoft admin changes
- silent permission bypasses or actor identity weakening
- commercialization or release-promotion work

### File allowlist (agent MAY touch these)

- `plans/m365-direct-runtime-readiness-remediation/**`
- `docs/prompts/codex-m365-direct-runtime-readiness-remediation.md`
- `docs/prompts/codex-m365-direct-runtime-readiness-remediation-prompt.txt`
- `src/provisioning_api/main.py`
- `src/provisioning_api/routers/email_dashboard.py`
- `src/provisioning_api/routers/m365.py`
- `src/ops_adapter/main.py`
- `src/ops_adapter/app.py`
- `src/ops_adapter/actions.py`
- `src/smarthaus_common/executor_routing.py`
- `src/smarthaus_common/tenant_config.py`
- `registry/executor_routing_v2.yaml`
- `tests/test_endpoints.py`
- `tests/test_ops_adapter.py`
- `tests/test_executor_routing_v2.py`
- `tests/test_m365_module_entrypoint.py`
- `tests/test_env_loading.py`
- `docs/LOCAL_TEST_LICENSED_RUNTIME.md`
- `docs/commercialization/m365-direct-runtime-readiness-remediation.md`
- `artifacts/diagnostics/m365_direct_runtime_readiness_remediation.json`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist (agent MUST NOT touch these)

- `../UCP/**`
- `registry/persona_registry_v2.yaml`
- `registry/persona_certification_v1.yaml`
- `registry/department_certification_v1.yaml`
- `registry/activated_persona_surface_v1.yaml`
- `registry/workforce_packaging_v1.yaml`
- `Any path not listed in the allowlist`

### Scope fence rule

Agent must STOP and re-scope if truthful direct runtime readiness requires UCP-side changes, tenant-admin changes, or edits outside the allowlist.

## Section 6: Requirements

- **R0 — Create the governed direct-runtime remediation package**
  - Create the bounded plan triplet, prompt pair, and tracker updates before any code or config change.
- **R1 — Repair direct import and entrypoint failures**
  - The top-level repo-direct instruction path must import and start locally without FastAPI response-model errors.
- **R2 — Repair bounded executor-routing parity**
  - Representative governed actions for direct testing must no longer fail because of local `executor_route_unknown` drift.
- **R3 — Add truthful direct-runtime regression coverage**
  - Focused tests must cover the repaired import path, repaired routing path, and preserved fail-closed actor/permission behavior.
- **R4 — Build and execute a direct-test harness**
  - The repo must have one repeatable direct-test path for representative functions across email/calendar, Teams, SharePoint, Power Automate, and admin/governance.
- **R5 — Stop only when direct testing is genuinely usable**
  - The phase ends only when representative direct tests run cleanly enough that future function checks can be requested without tripping on known local runtime defects.

## Section 7: Execution Sequence

- `T1 -> T2 -> T3 -> T4 -> T5`
- Stop on first red.

## Section 8: Tasks

- **T1 — Package and baseline lock**
  - Create the governed package, freeze the current direct-runtime blockers, and mark this initiative active in the trackers.
- **T2 — Import/entrypoint repair**
  - Repair the top-level provisioning API import path and revalidate the endpoint collection boundary.
- **T3 — Routing parity repair**
  - Inventory and repair bounded executor-routing drift blocking representative governed direct actions.
- **T4 — Direct-test harness and representative runs**
  - Execute the direct test harness across representative function families and capture truthful outcomes.
- **T5 — Governance closeout**
  - Write diagnostics, sync trackers, and close the phase only if the direct runtime is genuinely usable.

## Section 9: Gates

- **CHECK:C0 — Package and baseline truth locked**
  - The plan, prompt pair, and tracker state must exist before runtime edits.
- **CHECK:C1 — Import path green**
  - `provisioning_api.main` must import and endpoint tests must collect cleanly.
- **CHECK:C2 — Routing drift repaired**
  - Representative actions must not fail due to `executor_route_unknown`.
- **CHECK:C3 — Fail-closed auth truth preserved**
  - Actor identity, permission tier, and mutation gating must remain explicit and truthful.
- **CHECK:C4 — Representative direct harness usable**
  - Representative direct function tests must either succeed or fail only for truthful external reasons.
- **CHECK:C5 — Validation suite green**
  - Focused pytest, direct runtime smoke, `pre-commit run --all-files`, and `git diff --check` must pass.

## Section 10: Determinism Requirements

- `N/A — this phase is bounded runtime-readiness and regression repair work, not numerical or matching logic. Determinism is enforced through repeatable focused tests and repeated direct smoke runs under fixed local configuration.`

## Section 11: Artifacts

- `plans/m365-direct-runtime-readiness-remediation/m365-direct-runtime-readiness-remediation.md`
- `plans/m365-direct-runtime-readiness-remediation/m365-direct-runtime-readiness-remediation.yaml`
- `plans/m365-direct-runtime-readiness-remediation/m365-direct-runtime-readiness-remediation.json`
- `docs/prompts/codex-m365-direct-runtime-readiness-remediation.md`
- `docs/prompts/codex-m365-direct-runtime-readiness-remediation-prompt.txt`
- `docs/commercialization/m365-direct-runtime-readiness-remediation.md`
- `artifacts/diagnostics/m365_direct_runtime_readiness_remediation.json`

## Section 12: Environment

- **Python version:** `repo .venv / local developer workstation`
- **Venv:** `.venv/bin/python`
- **Additional dependencies:**
  - `fastapi`
  - `uvicorn`
  - `httpx`
  - `pytest`
- **Hardware:** `local developer workstation`
- **External data:**
  - `local tenant contract via UCP_ROOT/UCP_TENANT when present`
  - `Microsoft 365 tenant and actor identity when representative live actions are executed`

## Section 13: Implementation Approach

- **Option A:** Repair the bounded direct-runtime defects in place and prove them with focused direct runtime tests.
  - **Pros:** directly addresses the user requirement; keeps the work inside the actual repo runtime; preserves truthful local-versus-external failure classification.
  - **Cons:** may surface more than one local runtime defect before the direct test surface is stable.
- **Option B:** Treat the current repo verification suite as sufficient and skip direct runtime repair.
  - **Pros:** less work.
  - **Cons:** false completion; contradicts the already-proven direct import and routing failures.
- **Chosen:** `Option A`
- **Rationale:** the repo has already proven it is partially healthy but not directly testable enough for real function checks, so the next valid work is to close that direct-runtime gap rather than relitigate higher-level governance or UCP packaging.

## Section 14: Risks and Mitigations

- **Risk:** more direct runtime drift exists beyond the first import and routing defects.
  - **Impact:** `high`
  - **Mitigation:** keep the allowlist broad enough for the local runtime boundary and iterate inside the same package until representative direct tests are usable.
  - **Status:** `open`
- **Risk:** representative live actions may still fail because the local shell lacks tenant credentials or sufficient actor identity.
  - **Impact:** `medium`
  - **Mitigation:** preserve truthful classification; local runtime defects must be fixed, but external tenant/auth failures remain acceptable end states for direct testing.
  - **Status:** `open`
- **Risk:** a proposed fix could weaken actor identity or permission enforcement.
  - **Impact:** `high`
  - **Mitigation:** require focused auth/permission regressions and fail closed if green requires bypass.
  - **Status:** `open`
- **Hard blockers:** `none local to this repo; remaining failures are external prerequisites`

## Section 15: Rollback

- **Procedure:**
  - revert only the bounded allowlist files changed by this phase
  - restore the prior direct-runtime state if validation cannot stay truthful
  - update governance trackers to reflect the rollback truthfully
- **Files to revert:**
  - `plans/m365-direct-runtime-readiness-remediation/m365-direct-runtime-readiness-remediation.md`
  - `plans/m365-direct-runtime-readiness-remediation/m365-direct-runtime-readiness-remediation.yaml`
  - `plans/m365-direct-runtime-readiness-remediation/m365-direct-runtime-readiness-remediation.json`
  - `docs/prompts/codex-m365-direct-runtime-readiness-remediation.md`
  - `docs/prompts/codex-m365-direct-runtime-readiness-remediation-prompt.txt`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`

## Section 16: Prompt References

- **MATHS template:** `docs/governance/MATHS_PROMPT_TEMPLATE.md`
- **Prompt doc:** `docs/prompts/codex-m365-direct-runtime-readiness-remediation.md`
- **Prompt kickoff:** `docs/prompts/codex-m365-direct-runtime-readiness-remediation-prompt.txt`

## Section 17: Traceability

- `plan:m365-direct-runtime-readiness-remediation:R0` -> governed package and tracker creation
- `plan:m365-direct-runtime-readiness-remediation:R1` -> top-level direct runtime import/entrypoint repair
- `plan:m365-direct-runtime-readiness-remediation:R2` -> bounded executor-routing parity repair
- `plan:m365-direct-runtime-readiness-remediation:R3` -> focused direct-runtime regression coverage
- `plan:m365-direct-runtime-readiness-remediation:R4` -> repeatable direct-test harness and representative runs
- `plan:m365-direct-runtime-readiness-remediation:R5` -> usable direct-test surface closeout

## Section 18: Governance Closure

- [x] `Operations/ACTION_LOG.md` updated
- [x] `Operations/EXECUTION_PLAN.md` updated
- [x] `Operations/PROJECT_FILE_INDEX.md` updated
- [x] Plan artifacts synchronized (`.md/.yaml/.json`)
- [x] Diagnostics and direct-test truth recorded

## Section 19: Execution Outcome

- **Task checklist:**
  - `T1 complete`
  - `T2 complete`
  - `T3 complete`
  - `T4 complete`
  - `T5 complete`
- **Gate checklist:**
  - `CHECK:C0 complete`
  - `CHECK:C1 complete`
  - `CHECK:C2 complete`
  - `CHECK:C3 complete`
  - `CHECK:C4 complete`
  - `CHECK:C5 complete`
- **Outcome summary:**
  - `R1 complete` — repaired the provisioning API direct import boundary in `src/provisioning_api/routers/email_dashboard.py` and `src/provisioning_api/main.py`.
  - `R2 complete` — repaired logical-vs-physical executor resolution in `src/smarthaus_common/tenant_config.py`, `src/ops_adapter/actions.py`, `src/ops_adapter/main.py`, `src/ops_adapter/app.py`, and rebased `registry/executor_routing_v2.yaml` from `99` missing allowed-action routes to `0`.
  - `R3 complete` — focused regression coverage now proves import health, routing completeness, and logical-domain preservation across bounded multi-executor local tenants.
  - `R4 complete` — representative direct tests now classify truthfully:
    - instruction surface successes: SharePoint `list_sites`, Teams `list_teams`
    - governed action surface successes: `ucp-administrator/admin.get_tenant_config`, `teams-manager/teams.list`, `m365-administrator/sites.get`
    - external prerequisite failures: mail/calendar Graph `ErrorAccessDenied`, service-health Graph `UnknownError`, Power Apps / Power Automate admin module missing locally
  - `R5 complete` — future direct checks no longer trip on known local import or routing defects; remaining failures are external environment or tenant prerequisites rather than repo-runtime bugs.
