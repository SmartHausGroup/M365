# M365 Standalone Graph Runtime Integration Pack - P10 Operations, Rollback, Maintenance

**Plan:** `plan:m365-standalone-graph-runtime-integration-pack:R10`
**Phase:** `P10` Operations, Rollback, And Maintenance
**Date:** 2026-04-26
**Owner:** SMARTHAUS

This runbook is for the operator who runs the installed standalone Microsoft 365 Graph runtime pack. Everything in this runbook applies to the installed artifact at `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/<version>/` (or wherever UCP installs the pack), not to the M365 source repository.

## P10A - Operator Runbook

### 1. Setup (operator-supplied via UCP)

Required fields (declared in the packaged `setup_schema.json`):

- `M365_TENANT_ID` - Microsoft Entra tenant ID.
- `M365_CLIENT_ID` - Microsoft Entra application (client) ID with the read-only Graph permissions enumerated in `registry/action_registry.yaml`.
- `M365_AUTH_MODE` - one of `auth_code_pkce`, `device_code`, `app_only_secret`, `app_only_certificate`. **Username/password is rejected by the runtime; do not even try.**
- `M365_SERVICE_ACTOR_UPN` - operator or service principal UPN.

Additional fields (per auth mode):

- `auth_code_pkce`: `M365_REDIRECT_URI` (e.g. `http://localhost:9301/callback`).
- `device_code`: optional `M365_DEVICE_CODE_FALLBACK=true`.
- `app_only_secret`: `M365_APP_ONLY_CLIENT_SECRET_REF` - keychain item name or store reference, **never the raw secret**.
- `app_only_certificate`: `M365_APP_ONLY_CERTIFICATE_REF` - reference to a private key in keychain or HSM, **never the private key bytes**.

Recommended:

- `M365_TOKEN_STORE=keychain` (default).
- `M365_KEYCHAIN_SERVICE=ai.smarthaus.m365` (default).
- `M365_GRANTED_SCOPES` - comma-separated list of consented scopes.

### 2. Sign in

#### Authorization Code + PKCE

1. UCP starts the runtime via `python -m m365_runtime`.
2. UCP calls the runtime's auth-start flow (or the operator pastes the authorize URL into a browser).
3. Operator completes Microsoft sign-in.
4. The runtime stores the access token + refresh token in the configured token store (`keychain` by default).
5. Operator verifies via `GET /v1/auth/status`.

#### Device code

1. UCP requests a device code from the runtime.
2. Runtime returns `user_code`, `verification_uri`, and the polling interval.
3. Operator visits the URL on a separate browser, enters the user code, and approves.
4. Runtime polls until success and stores tokens.

#### App-only

1. The Entra application has been granted the read-only application permissions and admin consent has been recorded.
2. The client secret or certificate reference is set in the configured store.
3. Runtime acquires a token with `client_credentials`. No browser interaction.

### 3. Health and readiness

```
GET /v1/health/readiness
```

Returns a vector of nine boolean clauses + a `state` of `ready | not_ready` + a `label` for the first failing clause. Trust `Ready=true` only when `label=success`.

### 4. Action invocation

```
POST /v1/actions/{action_id}/invoke
{
  "actor": "ops@example.com",
  "params": { ... }
}
```

Read-only actions only. Non-registry IDs return `mutation_fence` immediately.

### 5. Logs

The runtime writes audit envelopes via `m365_runtime.audit.build_envelope`. Each envelope is `≤ 8 KB` and applies the redaction regex from P1E (`(?i)token|secret|password|assertion|certificate.*key|private.*key|authorization`) to every value before emit. If anything that matches the regex shows up unredacted in a log or evidence file, that is a **defect**, not a feature - report it immediately.

### 6. Restart

Stop and restart the runtime with the same launch command. The token store survives restarts (Keychain persists across processes; encrypted_pack_local survives across reboots).

### 7. Support boundaries

- The runtime does not modify Microsoft data outside read-only Graph endpoints. Mutations are fenced.
- The runtime does not call non-Graph services.
- The runtime does not contact UCP directly; UCP calls the runtime over the declared local socket.
- The runtime does not load configuration from `M365_REPO_ROOT`, `UCP_ROOT`, or any sibling repo path.

## P10B - Token Recovery

Routine sign-out (clear local token):

```
POST /v1/auth/clear
```

Removes the access token from the runtime's in-memory state.

Wipe stored tokens (Keychain backend):

```bash
security delete-generic-password -a <M365_SERVICE_ACTOR_UPN> -s <M365_KEYCHAIN_SERVICE>
```

Wipe stored tokens (encrypted_pack_local backend):

```bash
rm /Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/<version>/var/tokens.enc
```

Rotate app-only secret/certificate:

1. Rotate in Microsoft Entra (revoke old credential, create new credential).
2. Update the Keychain entry referenced by `M365_APP_ONLY_CLIENT_SECRET_REF` (or `M365_APP_ONLY_CERTIFICATE_REF`).
3. Restart the runtime. Health probes will go red briefly until the new token is acquired.

Reset local state entirely:

1. Stop the runtime.
2. Wipe stored tokens (above).
3. Remove any cached evidence under `<install_root>/var/`.
4. Restart and sign in fresh.

## P10C - Rollback

To roll the pack back to a previous version:

1. UCP disables the current pack version.
2. UCP stops the runtime process.
3. UCP installs the previous version from `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/<previous-version>/`.
4. UCP enables and launches the previous version.
5. UCP polls `GET /v1/health/readiness`. The previous version's readiness must come back `false` until its setup is restored, then `true` once auth/Graph health pass.

Failure mode safeguards:

- If the previous version cannot launch, UCP keeps the new version disabled; readiness across both is `false`. The operator chooses to either fix the new version or restore an older known-good version manifest.
- The plan does not authorize destructive teardown of installed pack directories without operator approval.

## P10D - Version Migration

Setup config migration policy:

- The setup schema is additive across `1.x` versions. New fields are optional unless they replace an explicit required field.
- If a future version retires a setup field, the runtime continues to accept the field for one minor release, with a documented deprecation note in the manifest.

Token state migration policy:

- Keychain entries persist across versions.
- The encrypted_pack_local store version-tags its payload prefix; an older version's store is not readable by a newer version unless an explicit migration step is run.
- Refresh tokens may be invalidated by Microsoft Entra at any time. The runtime must treat `auth_required` as a normal recoverable state.

## P10E - Support Evidence Policy

When opening a support ticket, attach:

- The pack version (`manifest.json -> version`).
- The most recent readiness vector (`GET /v1/health/readiness`).
- The auth status (`GET /v1/auth/status`).
- The last several audit envelopes (already redacted).
- The output of the verifier `python scripts/ci/verify_standalone_graph_runtime_pack.py` (from a development checkout - this is debug only).

Never include:

- Access tokens, refresh tokens, authorization codes, ID tokens.
- Client secrets, certificate private keys, PEM bytes.
- Microsoft Entra session bearer tokens.
- Operator passwords (which are not used by this runtime in any case).

If any of the above appears in a support artifact, treat it as a redaction defect. Stop, redact, and refile.

## P10F - Roadmap Gate

The following are explicitly out of scope for `1.x` and require new governed plans before implementation:

- Microsoft Graph **write** actions (any rw=write entry in any registry). Requires a separate mutation-governance plan.
- Webhook receivers / Microsoft Graph change notifications. Requires a webhook-receiver governance plan.
- Subscriptions / long-running connections. Requires a subscription governance plan.
- Multi-tenant SaaS hosting. Requires a SaaS deployment plan.
- UCP-side install/launch/setup/auth/action UX implementation. Requires the sibling UCP plan `plan:ucp-m365-standalone-graph-runtime-pack-activation`.
- Public marketplace publication. Requires a separate marketplace publication plan.

Until those plans are opened and green, the runtime continues to fail closed on any out-of-scope action with the appropriate failure-lattice node.

## Closure

- `P10A` operator runbook: complete (above).
- `P10B` token recovery: complete (Keychain `security` commands and encrypted_pack_local removal documented).
- `P10C` rollback: complete (UCP-driven version replacement procedure documented).
- `P10D` version migration: complete (additive setup schema policy + version-tagged token-store policy).
- `P10E` support evidence policy: complete (what to attach, what never to include).
- `P10F` roadmap gate: complete (explicit list of next-plan dependencies).

This document closes the M365-side operational scope of the original `1.1.x` standalone Graph runtime Integration Pack program. **Superseded as of 2026-04-27:** the `1.1.0` and `1.1.1` artifacts are historical prerelease evidence only. The active artifact is `com.smarthaus.m365@0.1.2`, produced by `plan:m365-standalone-graph-runtime-pack-0-1-2-readiness-fix` (bundle SHA `29c1d05bc30f570373d09a2ebb38313bda8466d4faa31e70a2e865e1c046fd9e`) and distributed as the GitHub Release tagged `com.smarthaus.m365-v0.1.2` per `plan:m365-github-release-and-ucp-handoff-closure`. Live UCP through-the-installed-pack acceptance and any roadmap items beyond read-only Graph remain governed by their respective sibling plans.
