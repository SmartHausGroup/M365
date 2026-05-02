# L109 - M365 Capability Pack C1 Coverage-Status Contract v1

**Lemma id:** `L109_m365_cps_c1_coverage_status_contract_v1`
**Plan reference:** `plan:m365-cps-trkC-p1-coverage-status-contract:T2`
**Predecessor:** `L108_m365_cps_b6_auth_tiers_v1`

## Mission

Define the four-value coverage status enum and the new
`not_yet_implemented` status class. This is the contract foundation
Track C builds on: agents.yaml entries (C2), MCP tool docstrings (C3),
and the operator capability map (C4) all reference these values.

## Coverage-status enum

```
COVERAGE_STATUS = {implemented, aliased, planned, deprecated}
```

- `implemented`: action_id is a key in READ_ONLY_REGISTRY directly.
- `aliased`: action_id is a key in LEGACY_ACTION_TO_RUNTIME_ACTION mapping
  to a key in READ_ONLY_REGISTRY.
- `planned`: action is declared in agents.yaml but neither implemented
  nor aliased. Calls return status_class=not_yet_implemented.
- `deprecated`: action was previously implemented or aliased and has
  been removed; calls return not_yet_implemented (or a deprecated marker
  if we add one later).

## Predicate

```
CoverageStatusContractValid =
    L_ENUM_COMPLETE
  ∧ L_NOT_YET_IMPLEMENTED_DISTINCT
  ∧ L_DENIAL_REASON_PLANNED
  ∧ L_NO_REGRESSION
```

## Lemmas

### L_ENUM_COMPLETE

`COVERAGE_STATUS_VALUES` exposes exactly these four values; nothing else.

### L_NOT_YET_IMPLEMENTED_DISTINCT

`not_yet_implemented` is distinct from `unknown_action`, `mutation_fence`,
`permission_missing`, `auth_required`, `policy_denied`, and
`tier_insufficient`. It signals "this action is declared in agents.yaml
but the runtime hasn't implemented it yet" — different from
`unknown_action` which means "I have no idea what this is".

### L_DENIAL_REASON_PLANNED

`_denial_to_status("planned_action")` returns `"not_yet_implemented"`.
This wires a new admit/denial reason through the existing status mapper.

### L_NO_REGRESSION

All Track A and Track B tests still pass; existing five status_class
values still resolve correctly.
