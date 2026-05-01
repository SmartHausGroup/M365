# L108 - M365 Capability Pack B6 Auth-Mode Tiers v1

**Lemma id:** `L108_m365_cps_b6_auth_tiers_v1`
**Plan reference:** `plan:m365-cps-trkB-p6-auth-mode-tiers:T2`
**Predecessor:** `L107_m365_cps_b5_directory_teams_v1`

## Mission

Introduce the tier system: every `ActionSpec` declares a `min_tier` of
`read-only` / `standard` / `admin`. `admit()` rejects calls whose session
tier is below the spec's minimum. All Track B actions added so far are
`read-only` since they are all reads. The tier system is architectural
preparation for future write actions (out of master plan scope).

## Tier ordering

```
read-only < standard < admin
```

A session admitted at tier `T` can invoke any action with `min_tier <= T`.

## Predicate

```
AuthTiersEnforced =
    L_TIER_DEFAULT_READ_ONLY
  ∧ L_TIER_ORDERING_TRANSITIVE
  ∧ L_ADMIT_REJECTS_INSUFFICIENT
  ∧ L_NO_REGRESSION
```

## Lemmas

### L_TIER_DEFAULT_READ_ONLY

`ActionSpec.min_tier` defaults to `"read-only"` so existing entries do
not need to be edited. Session tier defaults to `"read-only"` so device-
code holders can call the same surface they had before.

### L_TIER_ORDERING_TRANSITIVE

`tier_at_or_above("admin", "read-only") == True`,
`tier_at_or_above("read-only", "admin") == False`,
`tier_at_or_above(t, t) == True` for every t.

### L_ADMIT_REJECTS_INSUFFICIENT

`admit(action_id, granted_scopes, current_auth_mode, current_tier="read-only")`
returns `("denied", "tier_insufficient")` if `spec.min_tier > "read-only"`.

### L_NO_REGRESSION

All pre-B6 tests still pass; default-tier read-only sessions still
admit every existing read action.
