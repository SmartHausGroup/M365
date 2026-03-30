# MATHS Prompt: M365 Token Provider Runtime Repair

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-token-provider-runtime-repair:R1`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Approval and Governance Gates

1. **Present the approval packet first** — before executing any check, present the plan ref, scope, predecessor status, and intended actions to the operator.
2. **Wait for explicit "go"** — do not begin execution until the operator confirms with "go" in the chat interface.
3. **Call MCP `validate_action` before any mutating action** — before writing, editing, or creating any file, call `validate_action` and obey the verdict. If the verdict is not `allowed`, stop immediately.
4. **Stop on first red** — if any check emits `FAIL` or `BLOCKED`, stop the entire phase. Do not continue to subsequent checks.
5. **Do not auto-advance to the next phase** — even if this phase emits GO, the next phase requires its own approval packet and "go" confirmation.

## Draft vs Active Semantics

This phase starts in **Draft** status. It transitions to **Active** only after the operator presents the approval packet and receives "go". The parent initiative can be Active while this phase is still Draft.

## Execution Rules

- Run checks `M365-TOKEN-REPAIR-C0` -> `M365-TOKEN-REPAIR-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Final outputs:
  - `GATE:M365-TOKEN-REPAIR STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-TOKEN-REPAIR`
- Run ID: `m365-token-provider-runtime-repair`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-token-provider-runtime-repair:R1`
  - `plan:m365-token-provider-runtime-repair:R2`
  - `plan:m365-token-provider-runtime-repair:R3`
  - `plan:m365-token-provider-runtime-repair:R4`
  - `plan:m365-token-provider-runtime-repair:R5`

## Context

- Task name: `Repair the diagnosed M365 token-provider/runtime defect`
- Domain: `runtime`
- Dependencies:
  - `plans/m365-token-provider-path-diagnosis/m365-token-provider-path-diagnosis.md`
  - `src/ops_adapter/actions.py`
  - `src/smarthaus_graph/client.py`
- Allowlist:
  - `plans/m365-token-provider-runtime-repair/**`
  - `pyproject.toml`
  - `src/ops_adapter/actions.py`
  - `src/smarthaus_graph/client.py`
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
  - `../UCP/**`
  - `registry/**`

## M - Model

- Problem: `The diagnosis phase identified a bounded M365-side runtime/token defect that still blocks live token acquisition.`
- Goal: `Repair that exact defect without hiding downstream Microsoft-side truth.`
- Success criteria:
  - `The diagnosed defect is fixed in the M365 repo.`
  - `Focused regression tests are green.`
  - `The next dependency boundary is live classification, not more speculative repair.`

## A - Annotate

- Artifact/schema evidence:
  - `repair doc and diagnostics artifact`
- Runtime/test evidence:
  - `targeted ops/graph/env regression tests`
- Governance evidence:
  - `plan/execution/action-log/file-index sync`
- Determinism evidence:
  - `repeat bounded regression on fixed state yields the same pass/fail result`

## T - Tie

- Dependency ties:
  - `Repair must consume the exact diagnosis output.`
  - `Repair is complete only when live classification is the next boundary.`
- Known failure modes:
  - `over-broad repair`
  - `masking downstream Microsoft errors`
  - `changing unrelated registry or UCP surfaces`
- GO criteria:
  - `diagnosed defect fixed, focused regressions green, live classification unblocked`
- NO-GO criteria:
  - `repair drifts, focused regressions fail, or diagnosis is contradicted`

## H - Harness (ordered checks)

`M365-TOKEN-REPAIR-C0` Preflight
- Verify prerequisite diagnosis phase is green.

`M365-TOKEN-REPAIR-C1` Root-cause lock
- Restate the exact diagnosed defect and bound the repair.

`M365-TOKEN-REPAIR-C2` Runtime/auth repair
- Implement the minimal M365-side fix.

`M365-TOKEN-REPAIR-C3` Regression coverage
- Add or update focused regression tests.

`M365-TOKEN-REPAIR-C4` Diagnostics artifact
- Write repair diagnostics and repaired-path evidence.

`M365-TOKEN-REPAIR-C5` Failure-truth validation
- Ensure downstream Microsoft-side failures remain explicit.

`M365-TOKEN-REPAIR-C6` Execute targeted validations
- Run targeted ops/graph/env regression commands.

`M365-TOKEN-REPAIR-C7` Strict artifact validation
- Fail if the repaired boundary, tests, or diagnostics are missing.

`M365-TOKEN-REPAIR-C8` Deterministic replay
- Repeat bounded regression and require the same outcome.

`M365-TOKEN-REPAIR-C9` Hard gates (strict order)
1. `targeted regression suite`
2. `artifact readback`
3. `git diff --check`

`M365-TOKEN-REPAIR-C10` Governance synchronization and final decision
- Update required docs and emit GO/NO-GO lines.

## S - Stress-test

- Adversarial checks:
  - `If the repair changes unrelated surfaces, fail.`
  - `If a Microsoft-side permission failure is relabeled as local success, fail.`
- Replay checks:
  - `Focused regression outcome must match between runs.`

## Output Contract

- Deliverables:
  - `bounded M365-side repair`
  - `repair diagnostics artifact`
  - `focused regression evidence`
- Final decision lines:
  - `GATE:M365-TOKEN-REPAIR STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Repair boundary expands beyond diagnosis.
- Focused regressions are not green.
- Downstream Microsoft truth is obscured.
