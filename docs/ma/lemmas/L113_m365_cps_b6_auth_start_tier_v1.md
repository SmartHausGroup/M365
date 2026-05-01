# L113 - M365 Capability Pack B6 Auth-Start Tier Integration v1

**Lemma id:** `L113_m365_cps_b6_auth_start_tier_v1`
**Plan reference:** `plan:m365-cps-trkB-p6-auth-mode-tiers:T2,T3`
**Predecessor:** `L108_m365_cps_b6_auth_tiers_v1`

## Mission

Wire the tier system from L108 up to the user-visible auth flow.
`m365_auth_start` accepts an optional `tier` parameter; the value is
validated, stored in session state, and persisted via the token store
so it survives runtime restart. `invoke()` is extended to pass
`current_tier` through to `admit()` so calls are gated.

## Predicate

```
AuthStartTierIntegrated =
    L_AUTH_START_ACCEPTS_TIER
  ∧ L_TIER_VALIDATED
  ∧ L_TOKEN_STORE_PERSISTS_TIER
  ∧ L_INVOKE_FORWARDS_TIER
  ∧ L_DEFAULT_PRESERVED
```

## Lemmas

### L_AUTH_START_ACCEPTS_TIER

`POST /v1/auth/start` accepts an optional `tier` body field. The auth
flow (PKCE or device-code) proceeds with `state["session_tier"]` set
to the validated value.

### L_TIER_VALIDATED

Invalid tier strings are rejected with `state="config_invalid"` and
`reason="invalid_tier"`. Only members of `ALLOWED_TIERS`
(`{read-only, standard, admin}`) are accepted.

### L_TOKEN_STORE_PERSISTS_TIER

The token store records the session tier under account name
`session_tier`. On runtime restart, `state["session_tier"]` is
re-initialized from the token store; if absent, defaults to
`"read-only"`.

### L_INVOKE_FORWARDS_TIER

`actions.invoke()` accepts `current_tier` keyword (default
`"read-only"`) and forwards it to `admit()`. The HTTP
`/v1/actions/{id}/invoke` endpoint passes `state["session_tier"]`
through to `invoke()`.

### L_DEFAULT_PRESERVED

When no `tier` is provided in the auth_start body, the session
defaults to `"read-only"`. Existing operators who never opt into
higher tiers see no behavioral change.
