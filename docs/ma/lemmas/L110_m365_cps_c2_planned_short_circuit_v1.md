# L110 - M365 Capability Pack C2 Planned-Action Short-Circuit v1

**Lemma id:** `L110_m365_cps_c2_planned_short_circuit_v1`
**Plan reference:** `plan:m365-cps-trkC-p2-agents-yaml-schema:T2`
**Predecessor:** `L109_m365_cps_c1_coverage_status_contract_v1`

## Mission

Add a `compute_coverage_status(action_id)` helper that classifies any
action_id against the live runtime registry and alias table, plus a
short-circuit in `execute_m365_action` that returns
`status_class=not_yet_implemented` for `planned` actions without
contacting the runtime. This is the user-visible behavior change of
Track C: operators calling planned actions get an honest status instead
of an HTTP round-trip that would resolve to `unknown_action`.

## Predicate

```
PlannedShortCircuitValid =
    L_COVERAGE_STATUS_CORRECT
  ∧ L_PLANNED_RETURNS_NOT_YET_IMPLEMENTED
  ∧ L_IMPLEMENTED_PASSES_THROUGH
  ∧ L_NO_REGRESSION
```

## Lemmas

### L_COVERAGE_STATUS_CORRECT

`compute_coverage_status(action_id)` returns:
- `"implemented"` if `action_id` (or its `graph.`-prefixed form) is in `READ_ONLY_REGISTRY`.
- `"aliased"` if `action_id` is a key in `LEGACY_ACTION_TO_RUNTIME_ACTION` whose value is in `READ_ONLY_REGISTRY`.
- `"planned"` otherwise.

### L_PLANNED_RETURNS_NOT_YET_IMPLEMENTED

`execute_m365_action(agent, planned_action)` returns
`{"status_class": "not_yet_implemented", "coverage_status": "planned",
"action": ..., "agent": ..., "correlation_id": ...}` without any HTTP
call to the runtime.

### L_IMPLEMENTED_PASSES_THROUGH

`execute_m365_action` for an implemented or aliased action falls
through to the existing runtime/service/stub path unchanged.

### L_NO_REGRESSION

All Track A and Track B tests still pass. `validate_agent_action`
keeps its `(bool, str)` return signature; coverage status is exposed
via the new helper, not by changing existing function shapes.
