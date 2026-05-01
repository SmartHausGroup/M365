# Codex Prompt: M365 Auth Persistence Reconnect Remediation

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-auth-persistence-reconnect-remediation:R0-R8`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Approval and Governance Gates

1. The operator approved plan creation and full execution with `GO` on 2026-05-01.
2. Call UCP `validate_action` before each mutating action and obey the verdict.
3. Stay inside the plan allowlist unless a separate scope-correction package is created and approved.
4. Stop on hard blocker. Repair metadata-shape issues in the UCP validation request without stopping if the substantive scope remains allowed.
5. Do not publish a GitHub Release or push without explicit separate approval.

## Context

The standalone `m365_runtime` stores access and refresh tokens through `TokenStore`, defaulting to macOS Keychain. The startup path in `build_app()` initializes auth state from empty memory and never reads stored tokens. `refresh_access_token()` already exists in `src/m365_runtime/auth/oauth.py`, but the launcher does not call it on startup or before readiness/action invocation.

The remediation target is a corrected local artifact line `com.smarthaus.m365@0.1.3`. The existing `0.1.2` GitHub Release remains historical and must not be silently rewritten.

## Plan Reference

Primary plan: `plans/m365-auth-persistence-reconnect-remediation/m365-auth-persistence-reconnect-remediation.md`

## Execution Instructions

### R1 - Root-cause lock

Confirm from code that:

- `_store_access_token()` persists `access_token` and `refresh_token`.
- `build_app()` initializes state from empty memory.
- no startup hydration path reads `TOKEN_ACCOUNT_ACCESS` or `TOKEN_ACCOUNT_REFRESH`.
- no readiness/action/status path calls `refresh_access_token()`.

### R2 - Startup hydration and refresh

Implement a bounded launcher helper that:

- reads stored access token, refresh token, and expiry metadata from `TokenStore`;
- treats stored access without expiry and refresh as unusable;
- uses stored refresh token to mint a fresh access token for delegated modes;
- preserves refresh token if Microsoft returns a new access token without a replacement refresh token;
- records only state flags and failure reason, never token values.

### R3 - Lazy refresh

Before `/v1/auth/status`, `/v1/health/readiness`, and `/v1/actions/{action_id}/invoke`, ensure the in-memory access token is current. Refresh when the token is expired or inside the refresh margin. If refresh fails, clear in-memory access and return `auth_required`.

### R4 - Fail-closed auth truth

Ensure:

- `signed_in` means an in-memory access token exists and is not known expired;
- refresh failure returns `auth_required` with a bounded reason;
- Graph is never invoked with a stale token after refresh failure.

### R5 - Regression proof

Add focused tests in existing runtime test files:

- startup refresh uses stored refresh token and invokes Graph with fresh access token;
- refresh failure reports `auth_required` and does not call Graph with stale token;
- missing expiry and no refresh token is not treated as signed in;
- token expiry metadata is stored after auth;
- refresh response without replacement refresh token preserves the existing refresh token.

### R6 - Corrected artifact line

Update active runtime/build constants and tests to `0.1.3` without rewriting published `0.1.2` release notes/handoff docs.

### R7 - Validation

Run the validation commands recorded in the plan. If a validation command fails because of the new implementation, fix the root cause and rerun. If it fails due to unrelated repo drift, record the blocker precisely.

### R8 - Governance closeout

Update the plan triplet, execution plan, project file index if needed, and action log with final results.

## Success Criteria

- Runtime restarts can reuse persisted refresh token without forcing device-code sign-in.
- Auth status/readiness/action paths are truthful and fail closed.
- Targeted tests and packaging validation are green or a hard blocker is documented.
- Local corrected artifact line is `0.1.3`.
- No tokens, secrets, auth codes, device codes, or passwords are committed or logged.
