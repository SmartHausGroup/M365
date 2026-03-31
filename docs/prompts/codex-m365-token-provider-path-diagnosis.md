# MATHS Prompt: M365 Token Provider Path Diagnosis

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-token-provider-path-diagnosis:R1`
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

## Ownership Boundary (P2A)

This phase owns credential-source, auth-mode, and provider-path truth **only**. It must not repair runtime bootstrap, dependency, or health issues (P1A's scope). If evidence shows the remaining blocker belongs to P1A's domain, this phase must reopen P1A rather than drift scope.

## Execution Rules

- Run checks `M365-TOKEN-DIAGNOSIS-C0` -> `M365-TOKEN-DIAGNOSIS-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Final outputs:
  - `GATE:M365-TOKEN-DIAGNOSIS STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-TOKEN-DIAGNOSIS`
- Run ID: `m365-token-provider-path-diagnosis`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-token-provider-path-diagnosis:R1`
  - `plan:m365-token-provider-path-diagnosis:R2`
  - `plan:m365-token-provider-path-diagnosis:R3`
  - `plan:m365-token-provider-path-diagnosis:R4`
  - `plan:m365-token-provider-path-diagnosis:R5`

## Context

- Task name: `Diagnose the exact M365 token-provider path failure`
- Domain: `runtime`
- Dependencies:
  - `plans/m365-service-runtime-readiness-and-health/m365-service-runtime-readiness-and-health.md`
  - `src/ops_adapter/actions.py`
  - `src/smarthaus_graph/client.py`
  - `src/smarthaus_common/auth_model.py`
- Allowlist:
  - `plans/m365-token-provider-path-diagnosis/**`
  - `src/ops_adapter/actions.py`
  - `src/smarthaus_graph/client.py`
  - `src/smarthaus_common/auth_model.py`
  - `tests/test_ops_adapter.py`
  - `tests/test_auth_model_v2.py`
  - `docs/commercialization/m365-token-provider-path-diagnosis.md`
  - `artifacts/diagnostics/m365_token_provider_path_diagnosis.json`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
- Denylist:
  - `src/m365_server/__main__.py`
  - `../UCP/**`

## M - Model

- Problem: `The live path still needs exact evidence for which credential, auth-mode, or provider-path boundary is failing.`
- Goal: `Replace ambiguous credential stories with exact provider-path truth.`
- Success criteria:
  - `Credential source is explicit.`
  - `Auth mode and provider path are explicit.`
  - `Outcome classes are no longer ambiguous.`

## A - Annotate

- Artifact/schema evidence:
  - `diagnosis doc and diagnostics artifact`
- Runtime/test evidence:
  - `focused ops/auth tests`
- Governance evidence:
  - `plan/execution/action-log/file-index sync`
- Determinism evidence:
  - `repeat diagnosis lands on the same provider-path boundary`

## T - Tie

- Dependency ties:
  - `Diagnosis must close before repair starts.`
- Known failure modes:
  - `wrong credential source`
  - `wrong auth mode`
  - `provider/library failure hidden behind generic error text`
- GO criteria:
  - `exact repair boundary is explicit`
- NO-GO criteria:
  - `outcome class remains generic or ambiguous`

## H - Harness (ordered checks)

`M365-TOKEN-DIAGNOSIS-C0` Preflight
- Verify prerequisite readiness phase is green.

`M365-TOKEN-DIAGNOSIS-C1` Baseline inventory
- Capture current token-provider path behavior and outcome classes.

`M365-TOKEN-DIAGNOSIS-C2` Credential-source analysis
- Prove which credential source the live path actually uses.

`M365-TOKEN-DIAGNOSIS-C3` Auth-mode/provider analysis
- Prove which auth mode and provider code path the live path actually uses.

`M365-TOKEN-DIAGNOSIS-C4` Diagnostic surfacing
- Add bounded observability inside the allowlist.

`M365-TOKEN-DIAGNOSIS-C5` Outcome reclassification
- Replace generic credential stories with precise local or downstream classes.

`M365-TOKEN-DIAGNOSIS-C6` Execute targeted validations
- Run focused ops/auth validation for the diagnosis path.

`M365-TOKEN-DIAGNOSIS-C7` Strict artifact validation
- Fail if source, auth mode, provider path, or outcome class is missing.

`M365-TOKEN-DIAGNOSIS-C8` Deterministic replay
- Repeat the diagnosis and require the same boundary.

`M365-TOKEN-DIAGNOSIS-C9` Hard gates (strict order)
1. `targeted diagnosis tests`
2. `artifact readback`
3. `git diff --check`

`M365-TOKEN-DIAGNOSIS-C10` Governance synchronization and final decision
- Update required docs and emit GO/NO-GO lines.

## S - Stress-test

- Adversarial checks:
  - `If the phase jumps into repair without proving the boundary, fail.`
  - `If the phase keeps a fake credentials_missing label when more precise truth exists, fail.`
- Replay checks:
  - `Provider-path conclusion must match on reread.`

## Output Contract

- Deliverables:
  - `exact provider-path diagnosis`
  - `diagnostics artifact`
  - `explicit repair boundary`
- Final decision lines:
  - `GATE:M365-TOKEN-DIAGNOSIS STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Credential source remains ambiguous.
- Auth mode/provider path remains ambiguous.
- Diagnosis drifts into broad repair work.
