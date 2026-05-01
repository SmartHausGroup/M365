# UCP Handoff Packet - M365 Standalone Graph Runtime Integration Pack 0.1.3

**Source plan:** `plan:m365-0-1-3-github-release-and-ucp-handoff-closure:R11`
**M365-side closure:** `plan:m365-auth-persistence-reconnect-remediation` and `plan:m365-0-1-3-github-release-and-ucp-handoff-closure`
**Hand-off date:** 2026-05-01
**Boundary:** This document is M365-side only. No UCP repository file is mutated by this handoff.

## Release identity

```yaml
release_repo: SmartHausGroup/M365
release_url: pending
release_tag: com.smarthaus.m365-v0.1.3
release_target_commitish: main
release_target_commit: pending
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

Final required asset SHA256 values are filled during release closeout.
