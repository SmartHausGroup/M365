# SMARTHAUS M365 Integration Pack 0.1.3

**Pack identity:** `com.smarthaus.m365@0.1.3`
**Release tag:** `com.smarthaus.m365-v0.1.3`
**Release source repo:** `https://github.com/SmartHausGroup/M365`
**Release source commit:** `pending`
**Release date:** 2026-05-01
**Plan:** `plan:m365-0-1-3-github-release-and-ucp-handoff-closure`

This release promotes the live-tested auth-persistence reconnect remediation for the standalone Microsoft 365 Graph runtime Integration Pack.

## What changed

- The runtime now hydrates persisted delegated auth state from the configured `TokenStore`.
- The runtime refreshes delegated access tokens from a stored refresh token on startup and before auth status, readiness, and action invocation.
- Refresh failure fails closed as `auth_required`; the runtime does not send stale access tokens to Microsoft Graph.
- Refresh token preservation is explicit when Microsoft returns a new access token without a replacement refresh token.
- `token_expires_at` is stored and used to decide whether a persisted access token is still fresh.

## Live validation

The installed `0.1.3` pack was live-tested against the SmartHaus Microsoft tenant. Device-code sign-in succeeded, `graph.me` returned success for `phil@smarthausgroup.com`, readiness returned `ready/success`, and restart without reauth succeeded.

The critical live finding is:

- `User.Read,Directory.Read.All` allowed login and fresh-token restart, but Microsoft did not issue a refresh token. Forced-expiry restart failed closed with `lazy_refresh:refresh_token_missing`.
- `User.Read,Directory.Read.All,offline_access` issued a refresh token. Forced-expiry restart refreshed from Keychain and remained signed in without another browser login.

Therefore UCP-side setup/admission must request `offline_access` for true keep-me-logged-in delegated reconnect behavior.

## Auth posture

Supported auth modes:

- `auth_code_pkce`
- `device_code`
- `app_only_secret`
- `app_only_certificate`

Microsoft username/password auth is not supported. Tokens land in the configured `TokenStore` (`keychain` on macOS by default). No Microsoft password storage is introduced.

## Release assets

Final asset SHA256 values are recorded in the GitHub Release, `SHA256SUMS`, provenance, and UCP handoff packet.

## Distribution boundary

- **Canonical authority:** the GitHub Release for `com.smarthaus.m365-v0.1.3`.
- **Local cache/install:** `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.3/` is a cache/install copy only.
- **UCP admission:** out of scope for this M365 release and governed by a sibling UCP plan.

## No-secret posture

No Microsoft access tokens, refresh tokens, device codes after completion, authorization codes, client secrets, certificate private keys, subject object IDs, phone numbers, or passwords may appear in release assets, plan files, evidence, or governance trackers.
