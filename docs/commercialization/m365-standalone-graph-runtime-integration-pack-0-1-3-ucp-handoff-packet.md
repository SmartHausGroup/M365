# UCP Handoff Packet - M365 Standalone Graph Runtime Integration Pack 0.1.3

**Source plan:** `plan:m365-0-1-3-github-release-and-ucp-handoff-closure:R11`
**M365-side closure:** `plan:m365-auth-persistence-reconnect-remediation` and `plan:m365-0-1-3-github-release-and-ucp-handoff-closure`
**Hand-off date:** 2026-05-01
**Boundary:** This document is M365-side only. No UCP repository file is mutated by this handoff.

## Release identity

```yaml
release_repo: SmartHausGroup/M365
release_url: https://github.com/SmartHausGroup/M365/releases/tag/com.smarthaus.m365-v0.1.3
release_tag: com.smarthaus.m365-v0.1.3
release_target_commitish: main
release_target_commit: ca3fe24295d2814b10432f4d98a6ba8c4715a30d
release_name: SMARTHAUS M365 Integration Pack 0.1.3
release_is_draft: false
release_is_prerelease: false
release_is_latest: true
```

## Required UCP admission behavior

UCP must admit `com.smarthaus.m365@0.1.3` from the published GitHub Release asset, not from the M365 source repo or a developer-machine path.

UCP MUST:

1. Download the release asset `com.smarthaus.m365-0.1.3.ucp.tar.gz`.
2. Verify `SHA256SUMS` before extraction.
3. Treat `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.3/` as cache/install evidence only.
4. Launch the runtime from UCP's installed artifact root.
5. Preserve the declared runtime contract: `python -m m365_runtime`, `/v1/auth/*`, `/v1/health/readiness`, `/v1/actions`, and `/v1/actions/{action_id}/invoke`.
6. Request `offline_access` in delegated M365 scope configuration when keep-me-logged-in reconnect is required.

UCP MUST NOT:

1. Scan the M365 source repo for runtime files.
2. Use `M365_REPO_ROOT`, sibling-repo lookup, or parent-walk source assumptions.
3. Treat a fresh access token alone as durable reconnect proof.
4. Claim long-lived delegated reconnect if `offline_access` is absent.

## Offline access requirement

Live `0.1.3` testing proved that `offline_access` is required for Microsoft to issue a refresh token in the delegated device-code flow. Without a refresh token, the runtime can restart while the existing access token is still fresh, but once the token expires it must fail closed as `auth_required`.

The correct UCP delegated scope set must include `offline_access` alongside the Graph scopes required for the selected actions.

## Asset hashes

```text
d26278c6c47a650a8750ff0dc6b914fde418b778395661ebd5bba2f440981c4e  com.smarthaus.m365-0.1.3.ucp.tar.gz
6294067aadb7909065e32bd7d89562dfbf86e4c0453f114163c76b147735af0e  manifest.json
de77f6d111f7f4a4f99671e2773c0afb17c6531a6347dbb6263861f53036e938  conformance.json
f03ce347d9e9288ed1592c545cf7f7842352b7e5095c066f703c2171008fc894  provenance.json
7f7bf35b186def0e97ac321de3eeb85aab08e0ff3f503f6c7130d3bd24e789eb  SHA256SUMS
2e0eaf502ccf657ce8294397d101b35706b367785b01d09e58ebba7849b90d9b  payload.tar.gz
e56c7189cb3b54243a853a471ab2471dfc0ab28861c9cac2e6b1af423634388a  manifest.sig
66712ed70e910ce97df8b68de50eaf87d3ca823aff1997c456186d2fc565bb03  payload.sig
0909f5bbd3f49e867e948db8ea5a6c7a4d02973dcaca9d823f8c3fb6e35b8dc2  pack_metadata.json
56d12d3c1888914f90e96b7a1badd3158af39567202def09e05a57198e5426b6  pack_dependencies.json
```

Downloaded public-release verification passed against the release-surface `SHA256SUMS`.
