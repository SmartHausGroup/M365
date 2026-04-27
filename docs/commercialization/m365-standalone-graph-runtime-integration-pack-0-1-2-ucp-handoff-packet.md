# UCP Handoff Packet - M365 Standalone Graph Runtime Integration Pack 0.1.2

**Source plan:** `plan:m365-github-release-and-ucp-handoff-closure:C12`
**M365-side closure:** `plan:m365-standalone-graph-runtime-pack-0-1-2-readiness-fix` (Complete-GO)
**Hand-off date:** 2026-04-27
**Boundary:** This document is M365-side only. **No UCP repository file is mutated by this handoff.** All UCP-side admission/activation work belongs to a separate UCP-owned plan.

## Release identity (canonical authority)

UCP must admit `com.smarthaus.m365@0.1.2` from the published GitHub Release.
The local IntegrationPacks directory is a cache/install convenience, not the authoritative release source.

```yaml
release_repo: SmartHausGroup/M365
release_url: https://github.com/SmartHausGroup/M365/releases/tag/com.smarthaus.m365-v0.1.2
release_tag: com.smarthaus.m365-v0.1.2
release_target_commitish: main
release_target_commit: 687b69b65d8904457a1c72046e66c8e5f868f635
release_name: SMARTHAUS M365 Integration Pack 0.1.2
release_published_at: 2026-04-27T13:40:38Z
release_is_draft: false
release_is_prerelease: false
release_is_latest: true
```

## Required release assets and SHA256 (verify before install)

```yaml
required_assets:
  com.smarthaus.m365-0.1.2.ucp.tar.gz: 29c1d05bc30f570373d09a2ebb38313bda8466d4faa31e70a2e865e1c046fd9e
  manifest.json:                       bfc52d4b4e585604cac426d546153e5a7d54180630cadbf9a2b7f7c62a8584e9
  conformance.json:                    ab03f4277ecf700e4b032da843b8d45760358c3dd13a6b42c94033a154af3da7
  SHA256SUMS:                          4788ed7b512fa1e3407475cc061a7c49e36a1c1114a312594c15a31ffe6227a4

recommended_assets:
  payload.tar.gz:                      c09625a5b89b1578e2226463d43670dc8355db7d489338f3bf42001db16cabfd
  pack_metadata.json:                  7ff9c21b465916c7d28fd0e470e465e84b69351413e625b9df339f69a8a577fd
  pack_dependencies.json:              376f10bab9f3554e5bce73ef55ea157bb8fe866e3d498ea50c6895b87e8f0e0b
  provenance.json:                     # embeds built_at_utc; not byte-stable across builds
  manifest.sig:                        # sha256-detached envelope
  payload.sig:                         # sha256-detached envelope
  m365-standalone-graph-runtime-integration-pack-0-1-2-release-notes.md
```

UCP **must** verify the downloaded `SHA256SUMS` before extracting or installing the core envelope. The current `SHA256SUMS` release asset covers exactly `com.smarthaus.m365-0.1.2.ucp.tar.gz`, `manifest.json`, and `conformance.json`. The recommended ancillary assets above are verified by their listed SHA256 values and GitHub release asset digests, not by the current `SHA256SUMS` file.

## Pack identity from the release manifest

```yaml
pack_id:           com.smarthaus.m365
version:           0.1.2
schema_version:    "0.2.0"
display_name:      "Microsoft 365"
publisher:         { name: "SMARTHAUS", contact: "engineering@smarthaus.dev" }
category:          integration
distribution_mode: marketplace
visibility:        optional
entrypoint:
  adapter_class:   M365PackAdapter
  contract_module: ucp_m365_pack.contracts
  runtime_module:  m365_runtime
  runtime_command: ["python", "-m", "m365_runtime"]
capabilities_exposed:
  - m365_runtime
  - m365_directory
  - m365_sites
  - m365_users
  - m365_groups
  - m365_teams
  - m365_drives
  - m365_email_health
  - m365_calendar_health
  - m365_servicehealth
compatibility:
  min_ucp_version:        "1.0.0"
  max_ucp_version:        "<2.0.0"
  required_capabilities:  [agent_comm]
  sdk_contract_major:     1
entitlement:
  mode: license_required
  sku:  com.smarthaus.m365.enterprise
runtime:
  module:                       m365_runtime
  entrypoint_command:           ["python", "-m", "m365_runtime"]
  default_host:                 127.0.0.1
  default_port:                 9300
  health_path:                  /v1/health/readiness
  dependencies_path:            /v1/health/dependencies
  auth_start_path:              /v1/auth/start
  auth_check_path:              /v1/auth/check
  auth_status_path:             /v1/auth/status
  auth_clear_path:              /v1/auth/clear
  actions_path:                 /v1/actions
  invoke_path_template:         /v1/actions/{action_id}/invoke
  read_only:                    true
  mutation_fence:               true
  username_password_supported:  false
  supported_auth_modes:
    - auth_code_pkce
    - device_code
    - app_only_secret
    - app_only_certificate
```

## Dependency contract (asset: `pack_dependencies.json`)

```yaml
python_requires: ">=3.10"
required:
  - { module: httpx,   constraint: ">=0.27,<1.0", purpose: "HTTP client for Microsoft Graph and runtime invoke" }
  - { module: fastapi, constraint: ">=0.110,<1.0", purpose: "runtime launcher web framework" }
  - { module: uvicorn, constraint: ">=0.27,<1.0", purpose: "ASGI server for runtime launch" }
auth_mode_dependencies:
  app_only_certificate:
    - { module: jwt, package: PyJWT, constraint: ">=2.8,<3.0", purpose: "client_assertion JWT minting (RS256)" }
ucp_adapter_optional:
  - { module: jwt,                package: PyJWT,            constraint: ">=2.8,<3.0",  purpose: "service-token minting for the legacy ops-adapter shim path" }
  - { module: yaml,               package: PyYAML,           constraint: ">=6.0,<7.0",  purpose: "in-pack agents.yaml registry parsing for the legacy adapter path" }
  - { module: smarthaus_mcp_sdk,  package: smarthaus_mcp_sdk, constraint: ">=1.0,<2.0", purpose: "UCP MCP SDK contracts; only loaded when the pack adapter class is constructed" }
fail_closed_outcome_class: dependency_missing
probe_endpoint:            /v1/health/dependencies
```

If a required module is missing at launch, the runtime returns `LaunchPlan.outcome = "dependency_missing"` with a structured `missing_modules` list. Importing `m365_runtime.launcher` itself succeeds even when `httpx` / `fastapi` / `uvicorn` are absent (verified by subprocess tests in `tests/test_m365_runtime_0_1_2_readiness_fix.py`).

## Local cache/install path (UCP runtime materialization target)

```yaml
local_install_dir: /Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/
local_install_role: cache_of_release_asset
canonical_authority_for_install: github_release_asset_only
```

UCP must materialize the installed payload under its OWN runtime root, derived from the GitHub Release asset, not from this M365-developer-machine path.

## UCP admission contract

UCP MUST:

1. **Admit from GitHub Release asset.** Do not scan the M365 source repo. Do not hand-copy from a developer machine path. Do not use `M365_REPO_ROOT` / `SMARTHAUS_M365_REPO_ROOT` / `M365_REGISTRY_PATH` / parent-walk lookups. Do not consult any sibling repo path (`UCP_ROOT`, `REPOS_ROOT`, etc.).
2. **Verify integrity before install.** Run the downloaded `SHA256SUMS` against the core envelope assets (`com.smarthaus.m365-0.1.2.ucp.tar.gz`, `manifest.json`, `conformance.json`) and refuse to install on mismatch. If UCP downloads ancillary assets (`payload.tar.gz`, `pack_metadata.json`, `pack_dependencies.json`, signatures, provenance, or release notes), verify them against the SHA256 values listed in this handoff and the GitHub release asset digests; do not assume the current `SHA256SUMS` file covers those ancillary assets.
3. **Materialize the installed payload under a UCP-owned runtime root.** Extract the outer `.ucp.tar.gz` and the inner `payload.tar.gz` into the same root so `pack_metadata.json` + `setup_schema.json` + `registry/agents.yaml` (and the staged `m365_runtime/` and `ucp_m365_pack/`) all sit at the chosen root.
4. **Launch the runtime from the installed artifact.** Use the manifest's `runtime.entrypoint_command` (`python -m m365_runtime`) with the chosen root on `PYTHONPATH`. Do not require any M365 source checkout.
5. **Drive the auth lifecycle through the declared endpoints.**
   - Initial state: `GET /v1/auth/status` returns `auth_required`.
   - Start: `POST /v1/auth/start` (body chooses the configured `auth_mode`).
   - Check / poll: `POST /v1/auth/check` (with `code` + `state` for PKCE; with the device-code session for device flow; auto for app-only).
   - Status: `GET /v1/auth/status` (eventually `signed_in`).
   - Clear: `POST /v1/auth/clear` (zeroes token state and Keychain entries).
6. **Treat readiness as conditional.** `GET /v1/health/readiness` MAY return `not_ready` until tenant auth and configuration complete. The vector clauses (`svc / art / src / ctr / auth / tok / perm / graph / aud`) are reported individually. UCP must not declare admission "complete" until readiness reaches `state=ready, label=success`.
7. **Probe declared dependencies.** `GET /v1/health/dependencies` returns the present and missing module lists. UCP should treat any non-empty `missing_modules` as a hard failure at admission time.
8. **Execute Graph actions through the UCP-facing client.** `ucp_m365_pack.client.execute_m365_action(agent, action, params, correlation_id, actor_identity)` routes to `M365_RUNTIME_URL` over real `httpx`. Do not monkey-patch `_http_runtime_invoke`; the M365-side acceptance script (`scripts/ci/acceptance_standalone_graph_runtime_pack.py`) ships a guard `_assert_unpatched_http_runtime_invoke` that fails closed on any patch.

UCP MUST NOT:

- Include this pack in a Studio app bundle (`provenance.policy.studio_app_bundle_inclusion = false`).
- Register an external MCP server for this pack (`provenance.policy.external_mcp_server_registration = false`).
- Permit Microsoft username/password auth (`runtime.username_password_supported = false`).
- Write Microsoft access tokens, refresh tokens, device codes, authorization codes, client secrets, or certificate private keys to UCP-side logs, evidence, or telemetry.
- Treat the local M365 developer-machine `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/` as the canonical source.

## Provenance the release carries

The release `provenance.json` records `source.commit = 687b69b65d8904457a1c72046e66c8e5f868f635` (the `main` head at release tag time), `source.clean = true`, `claims_clean_reproducible = true`, `bundle_sha256 = 29c1d05bc30f570373d09a2ebb38313bda8466d4faa31e70a2e865e1c046fd9e`, and the per-file SHA256 set above. Two consecutive deterministic builds produce byte-identical bundle bytes (`built_at_utc` and `dirty_files_digests` legitimately differ between runs and are part of the `provenance.json` envelope, not the integrity-checked release set).

## Suggested UCP-side plan (out of M365 scope)

A sibling UCP plan should:

- Open as `plan:ucp-m365-standalone-graph-runtime-pack-activation` (or equivalent UCP-naming).
- Admit the GitHub Release asset by `(repo, tag, asset, SHA256)`.
- Materialize the installed payload under the UCP runtime root.
- Launch the runtime via `python -m m365_runtime` and bind to a UCP-managed port.
- Wire UCP auth/identity surfaces to the `/v1/auth/*` endpoints.
- Drive admission acceptance through `ucp_m365_pack.client.execute_m365_action(...)` over the local HTTP socket.
- Open the readiness gate only when `/v1/health/readiness` returns `ready/success` and `/v1/health/dependencies` returns no missing modules.

That UCP plan owns its own admission criteria, evidence, and release decision. The M365 side does not pre-declare it complete.

## Verification UCP can replay locally

```bash
tmpdir="$(mktemp -d)" && cd "$tmpdir"
gh release download com.smarthaus.m365-v0.1.2 --repo SmartHausGroup/M365
env LC_ALL=C LANG=C shasum -a 256 -c SHA256SUMS

mkdir extracted
tar -xzf com.smarthaus.m365-0.1.2.ucp.tar.gz -C extracted
tar -xzf extracted/payload.tar.gz -C extracted

env PYTHONPATH="$tmpdir/extracted" python -c "
import m365_runtime
from m365_runtime.launcher import plan_launch
print('runtime version:', m365_runtime.RUNTIME_VERSION)
print('launch outcome:', plan_launch().outcome)
"
```

Expected: `runtime version: 0.1.2`, `launch outcome: started`.

## What this handoff does NOT cover

- UCP marketplace listing, billing, license enforcement, or admission UX.
- UCP-side environment provisioning beyond what is needed to launch the runtime.
- Tenant-side Microsoft consent, app registration, or admin policy. Those are tenant operator responsibilities documented in the M365 operations runbook.
- Live UCP through-the-installed-pack acceptance. That is the responsibility of the sibling UCP plan referenced above.
