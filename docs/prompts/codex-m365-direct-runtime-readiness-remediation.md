# Execution Prompt — Direct Runtime Readiness Remediation

Plan Reference: `plan:m365-direct-runtime-readiness-remediation`
North Star Reference: `Operations/NORTHSTAR.md`
Execution Plan Reference: `Operations/EXECUTION_PLAN.md`
MATHS Template: `docs/governance/MATHS_PROMPT_TEMPLATE.md`

**Mission:** Repair the repo-direct M365 runtime so representative functions can be tested truthfully through the local repo version without tripping on known local import, routing, or harness defects.

## Governance Lock (Mandatory)

Before any write, test, or command:

1. Read:
- `AGENTS.md`
- applicable `.cursor/rules/**/*.mdc`
- `Operations/NORTHSTAR.md`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`
- `plans/m365-direct-runtime-readiness-remediation/m365-direct-runtime-readiness-remediation.md`
- `docs/LOCAL_TEST_LICENSED_RUNTIME.md`
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

2. Verify alignment + plan linkage:
- cite `plan:m365-direct-runtime-readiness-remediation:R0` through `R5`
- cite `plan:m365-direct-runtime-readiness-remediation:T1` through `T5`
- stop immediately if the work escapes the allowlist or drifts into UCP-side work

3. Enforce approval protocol:
- this package is already approved for execution
- call `validate_action` before any mutating action
- stop on first red

## Required Output Format

Use this exact structure:

- `Decision Summary`
- `Options Considered`
- `Evaluation Criteria`
- `Why This Choice`
- `Risks`
- `Next Steps`

## Execution Order

1. Complete **M** (Model).
2. Complete **A** (Annotate).
3. Complete **T** (Tie).
4. Complete **H** (Harness).
5. Complete **S** (Stress-test).
6. Update `Operations/ACTION_LOG.md`, `Operations/EXECUTION_PLAN.md`, and `Operations/PROJECT_FILE_INDEX.md` only when the phase actually changes governance state.

## Context

- Task name: `Repair the repo-direct M365 runtime for truthful direct function testing`
- Domain: `infrastructure`
- Allowlist:
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
- Denylist:
  - `../UCP/**`
  - `registry/persona_registry_v2.yaml`
  - `registry/persona_certification_v1.yaml`
  - `registry/department_certification_v1.yaml`
  - `registry/activated_persona_surface_v1.yaml`
  - `registry/workforce_packaging_v1.yaml`
  - any path not in the allowlist

## M - Model

- Problem:
  - `The repo verification suite is greener than the actual direct runtime.`
  - `provisioning_api.main currently breaks on import.`
  - `Representative governed actions still fail locally with executor_route_unknown.`
- Goal:
  - `Make the direct repo runtime usable enough that representative function tests can be requested and run without known local import or routing defects.`
- Success criteria:
  - `Top-level provisioning API imports cleanly.`
  - `Representative governed actions no longer fail because of local routing drift.`
  - `Direct tests across email/calendar, Teams, SharePoint, Power Automate, and admin/governance produce truthful outcomes.`
- Out of scope:
  - `UCP runtime changes`
  - `tenant-side Microsoft admin changes`
  - `permission bypasses`

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `docs/commercialization/m365-direct-runtime-readiness-remediation.md`
  - `artifacts/diagnostics/m365_direct_runtime_readiness_remediation.json`
- Runtime/test evidence:
  - `PYTHONPATH=src .venv/bin/pytest -q tests/test_m365_module_entrypoint.py tests/test_endpoints.py tests/test_ops_adapter.py tests/test_executor_routing_v2.py`
- Direct smoke evidence:
  - `local /health`
  - `top-level instruction path`
  - `representative direct actions across email/calendar, Teams, SharePoint, Power Automate, admin/governance`
- Governance evidence:
  - `Operations/ACTION_LOG.md`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/PROJECT_FILE_INDEX.md`

## T - Tie

- Dependency ties:
  - `The top-level API import path must be repaired before endpoint collection and direct instruction tests are meaningful.`
  - `Executor routing must be truthful before direct function testing is meaningful.`
  - `Actor identity and permission enforcement must stay fail-closed during all direct testing.`
- Known failure modes:
  - `import-time FastAPI response-model errors`
  - `executor_route_unknown`
  - `truth drift between local runtime defects and external tenant/auth failures`
- GO criteria:
  - `known local direct-runtime blockers are repaired`
  - `focused regressions are green`
  - `representative direct tests are usable`
- NO-GO criteria:
  - `top-level runtime still import-fails`
  - `representative direct actions still fail because of local routing drift`
  - `green requires bypassing actor identity or permission enforcement`

## H - Harness (ordered checks)

`M365-DIRECT-RUNTIME-C0` Package and baseline lock
- Confirm the package artifacts and current blocker inventory are in place.

`M365-DIRECT-RUNTIME-C1` Import repair
- Repair and revalidate `provisioning_api.main` import and endpoint collection.

`M365-DIRECT-RUNTIME-C2` Routing parity inventory
- Inventory representative routed actions and repair bounded drift in `registry/executor_routing_v2.yaml`.

`M365-DIRECT-RUNTIME-C3` Regression coverage
- Add or update focused endpoint, ops-adapter, and executor-routing tests.

`M365-DIRECT-RUNTIME-C4` Direct harness
- Run local direct runtime harness checks against `/health`, the top-level instruction path, and representative function families.

`M365-DIRECT-RUNTIME-C5` Diagnostics artifact
- Write diagnostics capturing repaired local blockers and remaining truthful external dependencies.

`M365-DIRECT-RUNTIME-C6` Hard gates (strict order)
1. `python3 -m py_compile src/provisioning_api/main.py src/provisioning_api/routers/email_dashboard.py src/ops_adapter/main.py src/ops_adapter/app.py src/ops_adapter/actions.py src/smarthaus_common/executor_routing.py`
2. `PYTHONPATH=src .venv/bin/pytest -q tests/test_m365_module_entrypoint.py tests/test_endpoints.py tests/test_ops_adapter.py tests/test_executor_routing_v2.py`
3. `pre-commit run --all-files`
4. `git diff --check`

`M365-DIRECT-RUNTIME-C7` Governance synchronization and final decision
- Update required docs and trackers, then emit GO/NO-GO lines.

## S - Stress-test

- Adversarial checks:
  - `If the fix weakens actor identity or permission enforcement, fail.`
  - `If a direct test still fails because of a local import or routing defect, fail.`
  - `If a live test fails for missing credentials, actor tier, or Microsoft-side permission, classify it truthfully instead of masking it.`
- Replay checks:
  - `Repeat the focused runtime and direct smoke suite and require the same outcome for the repaired local state.`

## Output Contract

- Deliverables:
  - `repaired direct runtime import path`
  - `repaired bounded executor-routing parity`
  - `focused regression coverage`
  - `direct runtime diagnostics and harness truth`
