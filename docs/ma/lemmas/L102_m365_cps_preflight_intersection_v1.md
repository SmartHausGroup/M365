# L102 - M365 Capability Pack Preflight Intersection v1

**Lemma id:** `L102_m365_cps_preflight_intersection_v1`
**Plan reference:** `plan:m365-cps-trkA-p3-preflight-intersection:T2`
**Status:** Active
**Owner:** SMARTHAUS
**Module notebook:** `notebooks/m365/INV-M365-CPS-A3-preflight-intersection-v1.ipynb`
**Invariant YAML:** `invariants/lemmas/L102_m365_cps_preflight_intersection_v1.yaml`
**Scorecard:** `artifacts/scorecards/scorecard_l102.json`
**Generated verification:** `configs/generated/m365_cps_preflight_intersection_v1_verification.json`
**Predecessor:** `L101_m365_cps_capability_inventory_v1`

## Mission

Compute the token-vs-registry intersection: given the current session's `auth_mode` and `granted_scopes`, return which registered actions the session can actually invoke, and split the rest into `blocked_by_auth_mode` vs `blocked_by_scopes`. Closes `plan:m365-capability-pack-surface-remediation:R3`.

## Bundled predicate

```
PreflightIntersectionValid =
    L_INVOKABLE_INCLUSION
  ∧ L_BLOCKED_BY_AUTH_MODE_DISJOINT
  ∧ L_BLOCKED_BY_SCOPES_DISJOINT
  ∧ L_PARTITION_COMPLETE
  ∧ L_NO_MUTATION
```

## Lemmas

### L_INVOKABLE_INCLUSION

For action `a`: `a in invokable` iff `session.auth_mode in a.auth_modes` and `a.scopes <= session.granted_scopes`.

### L_BLOCKED_BY_AUTH_MODE_DISJOINT

`blocked_by_auth_mode = {a in REGISTRY : session.auth_mode not in a.auth_modes}`. This set is disjoint from `invokable`.

### L_BLOCKED_BY_SCOPES_DISJOINT

`blocked_by_scopes = {a in REGISTRY : session.auth_mode in a.auth_modes AND a.scopes not <= session.granted_scopes}`. Disjoint from `invokable` and from `blocked_by_auth_mode`.

### L_PARTITION_COMPLETE

`invokable | blocked_by_auth_mode | blocked_by_scopes == REGISTRY`. Every action lands in exactly one bucket.

### L_NO_MUTATION

The function is pure: takes auth_mode and granted_scopes, returns three lists. No I/O, no Graph call, no state change.

## Test bindings

- `tests/test_m365_runtime_preflight_intersection.py`
