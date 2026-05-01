# SMARTHAUS M365 Integration Pack 0.1.3

**Pack identity:** `com.smarthaus.m365@0.1.3`
**Release tag:** `com.smarthaus.m365-v0.1.3`
**Release source repo:** `https://github.com/SmartHausGroup/M365`
**Release source commit:** `ca3fe24295d2814b10432f4d98a6ba8c4715a30d`
**Release URL:** `https://github.com/SmartHausGroup/M365/releases/tag/com.smarthaus.m365-v0.1.3`
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

Published asset SHA256 values:

- `com.smarthaus.m365-0.1.3.ucp.tar.gz`: `d26278c6c47a650a8750ff0dc6b914fde418b778395661ebd5bba2f440981c4e`
- `manifest.json`: `6294067aadb7909065e32bd7d89562dfbf86e4c0453f114163c76b147735af0e`
- `conformance.json`: `de77f6d111f7f4a4f99671e2773c0afb17c6531a6347dbb6263861f53036e938`
- `provenance.json`: `f03ce347d9e9288ed1592c545cf7f7842352b7e5095c066f703c2171008fc894`
- `SHA256SUMS`: `7f7bf35b186def0e97ac321de3eeb85aab08e0ff3f503f6c7130d3bd24e789eb`
- `payload.tar.gz`: `2e0eaf502ccf657ce8294397d101b35706b367785b01d09e58ebba7849b90d9b`
- `manifest.sig`: `e56c7189cb3b54243a853a471ab2471dfc0ab28861c9cac2e6b1af423634388a`
- `payload.sig`: `66712ed70e910ce97df8b68de50eaf87d3ca823aff1997c456186d2fc565bb03`
- `pack_metadata.json`: `0909f5bbd3f49e867e948db8ea5a6c7a4d02973dcaca9d823f8c3fb6e35b8dc2`
- `pack_dependencies.json`: `56d12d3c1888914f90e96b7a1badd3158af39567202def09e05a57198e5426b6`

Downloaded public-release verification passed against the release-surface `SHA256SUMS`.

## Distribution boundary

- **Canonical authority:** the GitHub Release for `com.smarthaus.m365-v0.1.3`.
- **Local cache/install:** `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.3/` is a cache/install copy only.
- **UCP admission:** out of scope for this M365 release and governed by a sibling UCP plan.

## No-secret posture

No Microsoft access tokens, refresh tokens, device codes after completion, authorization codes, client secrets, certificate private keys, subject object IDs, phone numbers, or passwords may appear in release assets, plan files, evidence, or governance trackers.
