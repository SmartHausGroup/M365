# Execution Prompt — MATHS Workstream (Governance Locked)

Plan Reference: `plan:m365-token-provider-runtime-repair`
Parent Plan: `plan:m365-service-mode-token-acquisition-remediation`
North Star: `docs/NORTH_STAR.md` (M365 repo equivalent: `Operations/NORTHSTAR.md`)
Execution Plan: `docs/platform/EXECUTION_PLAN.md` (M365 repo equivalent: `Operations/EXECUTION_PLAN.md`)
MATHS Template: `docs/governance/MATHS_PROMPT_TEMPLATE.md`
North Star Reference: `docs/NORTH_STAR.md` and `Operations/NORTHSTAR.md`
Execution Plan Reference: `docs/platform/EXECUTION_PLAN.md` and `Operations/EXECUTION_PLAN.md`

**Mission:** Repair the bounded M365-side service-auth/runtime defect on governed `/actions/*` calls so the M365 service satisfies the current cross-repo auth contract without weakening JWT-backed actor identity or masking downstream Microsoft truth.

This prompt uses the **MATHS Prompt Template** as the formal execution scaffold and remains inside the active M365 repair path. This phase must not perform UCP-side caller alignment, live classification, or end-to-end acceptance.

## Model Configuration (for prompt runner)

- Set temperature to `0`.
- Set `top_p` to `1.0`.
- Use precise or deterministic settings when available.

## Governance Lock (Mandatory)

Before any write, test, or command:

1. Read:
- `AGENTS.md`
- applicable `.cursor/rules/**/*.mdc`
- `Operations/NORTHSTAR.md`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`
- `plans/m365-service-mode-token-acquisition-remediation/m365-service-mode-token-acquisition-remediation.md`
- `plans/m365-token-provider-runtime-repair/m365-token-provider-runtime-repair.md`
- `plans/m365-token-provider-path-diagnosis/m365-token-provider-path-diagnosis.md`
- `docs/governance/MATHS_PROMPT_TEMPLATE.md`
- `../UCP/docs/platform/M365_SERVICE_AUTH_CONTRACT_AND_EXECUTION_ORDER.md`
- `src/ops_adapter/main.py`
- `src/ops_adapter/app.py`
- `src/ops_adapter/actions.py`
- `src/provisioning_api/auth.py`
- `tests/test_ops_adapter.py`
- `tests/test_graph_client.py`
- `tests/test_env_loading.py`

2. Verify alignment + plan linkage:
- cite `plan:m365-token-provider-runtime-repair:R1` through `R5`
- cite `plan:m365-token-provider-runtime-repair:T1` through `T5`
- stop immediately if the work escapes the allowlist or drifts into UCP-side caller alignment

3. Enforce approval protocol:
- present the formal approval packet first
- wait for explicit `go`
- call `validate_action` before any mutating action and obey the verdict
- stop on first red

## Required Output Format (Before Approval)

Use this exact structure:

- `Decision Summary`
- `Options Considered`
- `Evaluation Criteria`
- `Why This Choice`
- `Risks`
- `Next Steps`

## Execution Order (After Approval Only)

1. Complete **M** (Model).
2. Complete **A** (Annotate).
3. Complete **T** (Tie).
4. Complete **H** (Harness).
5. Complete **S** (Stress-test).
6. Update `Operations/ACTION_LOG.md`, `Operations/EXECUTION_PLAN.md`, and `Operations/PROJECT_FILE_INDEX.md` only if the bounded phase actually executes and changes governance state.

## Validator Compatibility Anchors

M:
A:
T:
H:
S:

## Context

- Task name: `Repair the M365 service-auth/runtime boundary in the active repair path`
- Domain: `infrastructure`
- Dependencies:
  - `plans/m365-token-provider-path-diagnosis/m365-token-provider-path-diagnosis.md`
  - `../UCP/docs/platform/M365_SERVICE_AUTH_CONTRACT_AND_EXECUTION_ORDER.md`
  - `src/ops_adapter/main.py`
  - `src/ops_adapter/app.py`
  - `src/ops_adapter/actions.py`
- Allowlist:
  - `plans/m365-token-provider-runtime-repair/**`
  - `docs/prompts/codex-m365-token-provider-runtime-repair.md`
  - `docs/prompts/codex-m365-token-provider-runtime-repair-prompt.txt`
  - `src/ops_adapter/main.py`
  - `src/ops_adapter/app.py`
  - `src/ops_adapter/actions.py`
  - `src/smarthaus_common/auth_model.py`
  - `src/provisioning_api/auth.py`
  - `tests/test_ops_adapter.py`
  - `tests/test_graph_client.py`
  - `tests/test_env_loading.py`
  - `docs/commercialization/m365-token-provider-runtime-repair.md`
  - `artifacts/diagnostics/m365_token_provider_runtime_repair.json`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
- Denylist:
  - `../UCP/src/**`
  - `../UCP/tests/**`
  - `registry/**`
  - any path not in the allowlist

## M - Model

- Problem: `UCP now reaches the M365 service, but the M365 service still fail-closes locally on governed /actions/* calls with 401 missing_bearer_token before Graph token acquisition.`
- Goal: `Repair the bounded M365-side service-auth/runtime defect while preserving JWT-backed actor identity and truthful downstream Microsoft behavior.`
- Success criteria:
  - `The M365 service no longer fails locally at the missing-bearer boundary for the intended governed caller shape.`
  - `Fail-closed JWT actor-identity enforcement remains intact.`
  - `The next dependency boundary becomes live classification, not more speculative repair.`
- Out of scope:
  - `UCP-side caller alignment`
  - `Microsoft tenant permission changes`
  - `final live classification`
  - `end-to-end acceptance`

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `docs/commercialization/m365-token-provider-runtime-repair.md`
  - `artifacts/diagnostics/m365_token_provider_runtime_repair.json`
- Runtime/test evidence:
  - `PYTHONPATH=src .venv/bin/pytest -q tests/test_ops_adapter.py tests/test_graph_client.py tests/test_env_loading.py`
- Governance evidence:
  - `Operations/ACTION_LOG.md`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/PROJECT_FILE_INDEX.md`
- Determinism evidence:
  - `repeat the bounded regression suite and require the same pass/fail result for fixed code and config`

## T - Tie

- Dependency ties:
  - `The M365 service auth contract must be satisfied before UCP can rerun consumer-side token validation truthfully.`
  - `The phase owns only the local M365 service-auth/runtime repair, not the UCP caller change.`
- Known failure modes:
  - `scope drift into UCP-side caller alignment`
  - `weakening JWT enforcement to force green`
  - `masking Microsoft-side failures behind local success`
- GO criteria:
  - `local service-auth/runtime defect repaired`
  - `focused regressions green`
  - `next dependency boundary is live classification`
- NO-GO criteria:
  - `repair still fails locally`
  - `JWT actor-identity enforcement weakens`
  - `downstream Microsoft truth is obscured`

## H - Harness (ordered checks)

`M365-TOKEN-REPAIR-C0` Governance preflight
- Confirm prerequisite reads, plan refs, allowlist, and the current cross-repo contract note.

`M365-TOKEN-REPAIR-C1` Root-cause lock
- Restate the exact service-auth/runtime failure boundary and keep the phase bounded to it.

`M365-TOKEN-REPAIR-C2` Bounded repair
- Implement the minimal M365-side service-auth/runtime repair.

`M365-TOKEN-REPAIR-C3` Focused regression coverage
- Add or update targeted regressions for missing-bearer, valid-bearer, and actor-identity-required behavior.

`M365-TOKEN-REPAIR-C4` Diagnostics artifact
- Write the repair diagnostics artifact and capture whether the next boundary is live classification.

`M365-TOKEN-REPAIR-C5` Failure-truth validation
- Confirm local service-auth failures remain distinct from downstream Microsoft failures.

`M365-TOKEN-REPAIR-C6` Execute targeted validations
- Run the bounded ops/graph/env regression suite.

`M365-TOKEN-REPAIR-C7` Strict artifact validation
- Fail if the diagnostics artifact or required governance updates are missing.

`M365-TOKEN-REPAIR-C8` Deterministic replay
- Repeat the bounded regression suite and require the same outcome.

`M365-TOKEN-REPAIR-C9` Hard gates (strict order)
1. `python3 -m py_compile src/ops_adapter/main.py src/ops_adapter/app.py src/ops_adapter/actions.py`
2. `PYTHONPATH=src .venv/bin/pytest -q tests/test_ops_adapter.py tests/test_graph_client.py tests/test_env_loading.py`
3. `git diff --check`

`M365-TOKEN-REPAIR-C10` Governance synchronization and final decision
- Update the required governance files if the phase executed, then emit GO/NO-GO lines.

## S - Stress-test

- Adversarial checks:
  - `If the repair weakens JWT-backed actor identity, fail.`
  - `If the repair claims Microsoft-side success without crossing the local auth boundary, fail.`
- Replay checks:
  - `The bounded regression suite must produce the same outcome on repeated runs.`

## Stop Conditions

- the phase requires UCP-side caller alignment
- the repair requires Microsoft tenant permission changes
- the next correct act becomes live classification rather than more M365-local repair

## Output Contract

- Deliverables:
  - `bounded M365-side service-auth/runtime repair`
  - `repair diagnostics artifact`
  - `focused regression evidence`
- Validation results:
  - `M365-TOKEN-REPAIR-C0` through `M365-TOKEN-REPAIR-C10`
- Final decision lines:
  - `GATE:M365-TOKEN-REPAIR STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`
