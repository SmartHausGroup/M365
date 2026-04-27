# SMARTHAUS M365 Integration Pack 0.1.2

**Pack identity:** `com.smarthaus.m365@0.1.2`
**Release tag:** `com.smarthaus.m365-v0.1.2`
**Release source repo:** `https://github.com/SmartHausGroup/M365`
**Release source commit:** `687b69b65d8904457a1c72046e66c8e5f868f635` (`main`)
**Release date:** 2026-04-27
**Plan:** [`plan:m365-github-release-and-ucp-handoff-closure`](https://github.com/SmartHausGroup/M365/blob/main/plans/m365-github-release-and-ucp-handoff-closure/m365-github-release-and-ucp-handoff-closure.md)

This is the canonical GitHub Release for `com.smarthaus.m365@0.1.2`.
Any local copy under `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/`
is a cache/install copy of this release - it is **not** the release authority.

## What this pack is

A standalone Microsoft 365 Graph runtime Integration Pack that ships:

- A local FastAPI runtime (`m365_runtime`) exposing the auth lifecycle
  (`/v1/auth/start`, `/v1/auth/check`, `/v1/auth/status`, `/v1/auth/clear`),
  health and dependency probes (`/v1/health/readiness`,
  `/v1/health/dependencies`), and a read-only Graph action surface
  (`/v1/actions`, `/v1/actions/{action_id}/invoke`).
- A UCP-facing client + contracts module (`ucp_m365_pack`) that routes
  `execute_m365_action(...)` traffic to the runtime over a local HTTP
  socket using real `httpx` (no monkey-patched transports).
- An in-payload self-describing identity file (`pack_metadata.json`) and
  declared dependency contract (`pack_dependencies.json`) so the runtime
  satisfies `probe_artifact()` from any extraction layout and fails
  closed with structured `dependency_missing` outcomes when a required
  module is absent.

## Auth posture

Supported auth modes:

- `auth_code_pkce`
- `device_code`
- `app_only_secret`
- `app_only_certificate`

Microsoft username/password auth is explicitly **not** supported. The
manifest carries `runtime.username_password_supported = false` and the
setup schema rejects username/password fields.

The runtime never reads or persists Microsoft secret material directly.
Tokens land in the configured `TokenStore` (`keychain` on macOS by
default).

## Scope guarantees

- **Read-only:** the manifest declares `runtime.read_only = true` and
  `runtime.mutation_fence = true`. Write actions outside the read-only
  registry return `status_class = mutation_fence`.
- **No source-repo dependency:** the packaged runtime resolves its
  installed root from its package file location only. It does not read
  `M365_REPO_ROOT`, `SMARTHAUS_M365_REPO_ROOT`, parent-walk patterns, or
  any sibling-repo path.
- **Source independence verified:** the verifier scans every payload
  `.py`/`.yaml`/`.json`/`.md`/`.txt` for the forbidden token list and
  fails closed on any hit.

## Release assets

| Asset | Purpose | SHA256 |
| --- | --- | --- |
| `com.smarthaus.m365-0.1.2.ucp.tar.gz` | Outer UCP marketplace bundle | `29c1d05bc30f570373d09a2ebb38313bda8466d4faa31e70a2e865e1c046fd9e` |
| `manifest.json` | Pack identity, runtime contract, capabilities, content_digest | `bfc52d4b4e585604cac426d546153e5a7d54180630cadbf9a2b7f7c62a8584e9` |
| `conformance.json` | 18-check conformance evidence | `ab03f4277ecf700e4b032da843b8d45760358c3dd13a6b42c94033a154af3da7` |
| `payload.tar.gz` | Inner payload (runtime + client + registry + metadata) | `c09625a5b89b1578e2226463d43670dc8355db7d489338f3bf42001db16cabfd` |
| `provenance.json` | Source/build provenance with clean-source proof | (varies; embeds built_at_utc) |
| `pack_metadata.json` | In-payload self-describing pack identity | `7ff9c21b465916c7d28fd0e470e465e84b69351413e625b9df339f69a8a577fd` |
| `pack_dependencies.json` | Declared Python runtime dependency contract | `376f10bab9f3554e5bce73ef55ea157bb8fe866e3d498ea50c6895b87e8f0e0b` |
| `signatures/manifest.sig` | sha256-detached manifest signature | (envelope) |
| `signatures/payload.sig` | sha256-detached payload signature | (envelope) |
| `SHA256SUMS` | Integrity index over bundle + manifest + conformance | (computed by gh release) |

## Verification

Two consecutive deterministic builds produced byte-identical bundle
SHA256 values. Real-local-socket acceptance returned 21/21 GO. The
verifier returned 9/9 PASSED. The focused regression suite returned
`84 passed`. The live SmartHaus Microsoft device-code sign-in and
read-only `graph.me` invocation completed for `phil@smarthausgroup.com`
against the installed runtime; readiness returned `state=ready`,
`label=success`.

## Distribution boundary

- **Canonical authority:** this GitHub Release.
- **Local cache/install:** `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/`
  exists as a local install copy. Do not treat it as the release
  authority. Re-fetch from the GitHub Release if there is any doubt.

## What is out of scope for this release

- UCP Marketplace admission of this pack is governed by a separate
  sibling UCP plan, not by this M365-side release.
- Live UCP through-the-installed-pack acceptance is the responsibility
  of that UCP plan.
- This release does not commit or claim any UCP-side changes.

## How to verify locally

```bash
tmpdir="$(mktemp -d)" && cd "$tmpdir"
gh release download com.smarthaus.m365-v0.1.2 --repo SmartHausGroup/M365
env LC_ALL=C LANG=C shasum -a 256 -c SHA256SUMS
mkdir extracted
tar -xzf com.smarthaus.m365-0.1.2.ucp.tar.gz -C extracted
tar -xzf extracted/payload.tar.gz -C extracted
ls extracted/m365_runtime extracted/ucp_m365_pack extracted/registry
```

After extraction the runtime is launchable from the extracted directory
without `PYTHONPATH=src` and without any M365 source repo path on disk.

## No-secret posture

No Microsoft access tokens, refresh tokens, device codes (after
completion), authorization codes, client secrets, certificate private
keys, subject object IDs, or phone numbers appear in any release asset,
plan file, evidence document, or governance tracker produced by the M365
side of this release. Tenant identifiers (tenant id, client id, actor
UPN) are recorded in evidence because they are required to reproduce the
auth posture; they are not secrets in this context.
