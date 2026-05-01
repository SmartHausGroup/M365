# L100 - M365 Capability Pack Surface Status Code Semantics v1

**Lemma id:** `L100_m365_cps_status_code_semantics_v1`
**Plan reference:** `plan:m365-cps-trkA-p1-status-code-semantics:T2`
**Status:** Active
**Owner:** SMARTHAUS
**Module notebook:** `notebooks/m365/INV-M365-CPS-A1-T2-status-code-semantics-v1.ipynb`
**Invariant YAML:** `invariants/lemmas/L100_m365_cps_status_code_semantics_v1.yaml`
**Scorecard:** `artifacts/scorecards/scorecard_l100.json`
**Generated verification:** `configs/generated/m365_cps_status_code_semantics_v1_verification.json`
**Predecessor:** `L99_m365_standalone_graph_runtime_pack_0_1_2_readiness_fix_v1`

## Mission

Make `_denial_to_status` in `src/m365_runtime/graph/actions.py` semantically honest. Prior implementation collapsed `unknown_action` into `mutation_fence`, which lied about the denial reason and led downstream consumers (UCP `m365_tools.py`, the testing operator, the audit envelope reader) to misdiagnose unknown actions as policy-fenced writes.

This lemma binds the one-line fix at `actions.py:135` to a notebook-backed invariant. The fix preserves all four other branches exactly and changes only the `unknown_action` branch from returning `"mutation_fence"` to returning `"unknown_action"`.

## Bundled predicate

```
StatusDenialHonest =
    L_PRESERVE_PERMISSION_MISSING
  ∧ L_PRESERVE_AUTH_REQUIRED
  ∧ L_FIX_UNKNOWN_ACTION
  ∧ L_PRESERVE_MUTATION_FENCE
  ∧ L_PRESERVE_DEFAULT
```

Any single false clause means `NO_GO`.

## Lemmas

### L_PRESERVE_PERMISSION_MISSING

`_denial_to_status("permission_missing")` returns `"permission_missing"`. Unchanged.

**Failure boundary:** function returns any other string for input `"permission_missing"`.

### L_PRESERVE_AUTH_REQUIRED

`_denial_to_status("auth_mode_mismatch")` returns `"auth_required"`. Unchanged.

**Failure boundary:** function returns any other string for input `"auth_mode_mismatch"`.

### L_FIX_UNKNOWN_ACTION

`_denial_to_status("unknown_action")` returns `"unknown_action"`. **This is the change.** Prior behavior returned `"mutation_fence"`; this lemma asserts the post-fix behavior.

**Failure boundary:** function returns `"mutation_fence"` (or anything other than `"unknown_action"`) for input `"unknown_action"`.

### L_PRESERVE_MUTATION_FENCE

`_denial_to_status("mutation_fence")` returns `"mutation_fence"`. Unchanged. Genuine mutation fences (a write action that admit() rejected for `rw != "read"`) still surface as `mutation_fence`.

**Failure boundary:** function returns any other string for input `"mutation_fence"`.

### L_PRESERVE_DEFAULT

`_denial_to_status(<anything else>)` returns `"policy_denied"`. Unchanged default branch.

**Failure boundary:** function returns any other string for an unknown reason value.

## Why the fix is safe

Three downstream consumers of `status_class`:

1. **`ActionInvocation.status_class`** (returned to caller). Caller code in UCP `m365_tools.py` does not pattern-match on `mutation_fence` differently from `unknown_action` for unknown action IDs (verified by inspection of the active `_m365_execute` path). Adding a new distinct status `unknown_action` adds information; it does not change behavior for callers that only check for success vs. denial.

2. **Audit envelope `status_class`** (in the audit log). The audit format is open string; no downstream auditor was relying on `unknown_action` denials being labeled `mutation_fence`.

3. **UCP MCP tool response** (surfaced to the operator/agent). Operators previously could not distinguish "this is a write we fenced" from "we don't know what that action is at all." Restoring the distinction is the whole point of `plan:m365-capability-pack-surface-remediation:R1`.

Therefore the fix is purely additive in information content. No callers break.

## Test bindings

- `tests/test_m365_pack_client.py` — adds `test_unknown_action_returns_unknown_action_status` (T5).
- `tests/test_m365_pack_contracts.py` — verifies ActionInvocation.status_class is plumbed faithfully (T3).
- UCP-side `tests/test_m365_integration.py` — adds `test_m365_unknown_action_routing` (T6).

## Determinism

```
seed_locked: true
seed: 0
mode: deterministic-static
```

The notebook performs no random sampling and no live network. The five assertions are pure function-call equality checks against `_denial_to_status`.
