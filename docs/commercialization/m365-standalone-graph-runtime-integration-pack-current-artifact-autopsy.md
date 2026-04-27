# M365 Standalone Graph Runtime Integration Pack - P0A Current Artifact Autopsy

**Plan:** `plan:m365-standalone-graph-runtime-integration-pack:R1`
**Phase:** `P0A` - Current artifact autopsy
**Date:** 2026-04-25
**Owner:** SMARTHAUS
**Notebook evidence:** `notebooks/m365/INV-M365-DK-standalone-graph-runtime-pack-p0-current-artifact-autopsy-v1.ipynb`
**Generated verification:** `configs/generated/standalone_graph_runtime_integration_pack_p0_current_artifact_autopsy_v1_verification.json`

## Purpose

Document the truthful current state of the SMARTHAUS M365 marketplace artifact and prove that it is not yet a real standalone Microsoft Graph integration runtime. The point of this autopsy is to make the gap explicit before any math, runtime, or packaging work begins under this plan.

## Artifact Identity Lock

- Pack ID: `com.smarthaus.m365`
- Version: `1.0.0`
- Distribution mode: `marketplace`
- Display name: `Microsoft 365`
- Setup schema ref: `setup_schema.json`
- Entrypoint: `M365PackAdapter` in `ucp_m365_pack.contracts`
- Local store path: `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/1.0.0/`
- Source provenance: `https://github.com/SmartHausGroup/M365.git@main` commit `e871e19ae8337e8098e898419c1fa9da19bed454`
- Bundle SHA256: `e22a8de63a3ab8aa29618dc28cd3463f7f319d727f753bc7019ac393aef04432`

## Bundle Inventory (top-level `.ucp.tar.gz`)

```
manifest.json
payload.tar.gz
signatures/manifest.sig
signatures/payload.sig
evidence/conformance.json
assets/README.md
```

## Payload Inventory (`payload.tar.gz`)

```
ucp_m365_pack/__init__.py
ucp_m365_pack/client.py
ucp_m365_pack/contracts.py
setup_schema.json
registry/agents.yaml
```

That is the entire payload. There is no `m365_server`, no `smarthaus_graph`, no `ops_adapter`, no Microsoft auth implementation, no token store, no Graph client, no launcher, and no Microsoft Graph capability code packaged inside the artifact.

## Setup Schema Truth

The packaged setup schema requires only:

- `M365_OPS_ADAPTER_URL` - external base URL for an unspecified M365 service runtime.
- `M365_SERVICE_JWT_HS256_SECRET` - HS256 secret used to mint a caller bearer token for that external service.
- `M365_SERVICE_ACTOR_UPN` - operator or service principal UPN asserted into the bearer token.
- Optional `M365_SERVICE_JWT_ISSUER` and `M365_SERVICE_JWT_AUDIENCE` claims.

It does not require, and does not advertise, any of the following Microsoft Graph fields:

- `GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET`
- `M365_TENANT_ID`, `M365_CLIENT_ID`, `M365_AUTH_MODE`
- `M365_REDIRECT_URI`, `M365_DEVICE_CODE_FALLBACK`
- `M365_APP_ONLY_CERTIFICATE_REF`, `M365_APP_ONLY_CLIENT_SECRET_REF`
- `M365_TOKEN_STORE`, `M365_KEYCHAIN_SERVICE`

The pack therefore claims readiness only by promising that some other process - not packaged, not launched, not health-checked by the artifact - is reachable at the configured URL.

## Source-Repo Coupling Inside The Pack

Two specific places hardwire the pack to the M365 source repository, which violates the standalone integration target.

1. `src/ucp_m365_pack/client.py`:
   - Reads `M365_REPO_ROOT` and `SMARTHAUS_M365_REPO_ROOT` env vars.
   - In the absence of those env vars, calls `_resolve_m365_repo_root()` which walks the module's parent directories looking for `registry/agents.yaml` or `src/ops_adapter/`.
   - Loads agent metadata from the discovered path via `_load_registry()`.
   - In the absence of `M365_OPS_ADAPTER_URL`, raises `M365ExecutionError(503, "m365_executor_unavailable")` with an explicit comment that direct import fallback has been removed.
2. `src/m365_server/__main__.py`:
   - Imports `from ops_adapter.main import app` at runtime, requiring `src/ops_adapter` to exist on the Python path.
   - Resolves the app root by checking `M365_APP_ROOT` env, then the current working directory for `registry/agents.yaml` or `src/ops_adapter/`.
   - Searches for tenants via `UCP_ROOT`, `REPOS_ROOT`, `UCP_REPOS_ROOT`, and parent-directory walks toward `UCP/tenants` and `SMARTHAUS_MCPSERVER_core/tenants`.
   - Refuses to start if `registry/agents.yaml` is not present at app root.

In effect, the current launcher cannot start from an installed artifact alone. It assumes the M365 source tree, the UCP source tree, and possibly an MCP server source tree are all mounted on the host file system.

## Microsoft Graph Capabilities Packaged

None. The packaged payload contains zero text indicators for any of the following terms when the bundle is grepped:

- `authorization_code`, `pkce`, `device_code`, `client_credentials`
- `keychain`, `keyring`, `msal`, `adal`
- `throttle`, `retry-after`, `x-ms-throttle`
- `GraphClient`, `graph.microsoft.com`

The current `ucp_m365_pack/client.py` mints a JWT bearer token and POSTs it at `${M365_OPS_ADAPTER_URL}/actions/{agent}/{action}`. It does not call Microsoft Graph itself, does not negotiate OAuth, does not store tokens, and does not classify Graph errors.

## Conformance Truth

The current bundle's `evidence/conformance.json` reports `status="conformant"` and 11 passing checks. That is truthful with respect to the existing UCP marketplace pack contract, which does not require a Microsoft Graph runtime service to be packaged inside the artifact. It therefore does not contradict the gap proven above. The autopsy invariants `I1` through `I5` add the missing facts:

- `I1` - The payload is exactly the UCP-facing client + contracts + setup schema + an `agents.yaml` registry, with no Microsoft Graph runtime, auth flow, token store, or launcher present.
- `I2` - The setup schema requires an external ops adapter URL plus a JWT minting secret and does not advertise any Graph auth fields.
- `I3` - The UCP-facing client expects to find the M365 source tree on disk and falls back to `M365_REPO_ROOT`-style env lookup.
- `I4` - The current launcher imports the in-source `ops_adapter` and walks `UCP_ROOT` / `REPOS_ROOT` for tenants, which means the runtime cannot launch without the M365 source checkout.
- `I5` - The packaged payload contains no Microsoft Graph or OAuth implementation indicators at all.

All five invariants closed `true` in the deterministic autopsy notebook. The `dist/m365_pack` and `IntegrationPacks/M365/1.0.0` SHA256SUMS / provenance pair is consistent for the packaged bytes; that consistency is a property of the existing client/contract pack and is not contradicted by the new gap finding.

## Implication For This Plan

The current artifact is truthful for what it actually is: a UCP-facing client and contract bundle. It is not truthful as a real Microsoft Graph integration pack, because:

- It does not include the runtime that would speak to Microsoft Graph.
- It does not include the auth flow that would make Graph calls possible.
- It does not include the token store that would protect Graph credentials.
- It does not include the launcher that would let UCP start the runtime.
- It depends on the M365 source repository being on disk, which violates marketplace portability.

`plan:m365-standalone-graph-runtime-integration-pack` exists exactly to close this gap. P0A locks this autopsy as the starting truth for that work. No subsequent phase may claim the current bundle is a complete integration; readiness can only be claimed once the standalone runtime, auth, token, Graph, permission, UCP contract, and packaging surfaces are all present and proven.

## Closure

- Verification artifact: `configs/generated/standalone_graph_runtime_integration_pack_p0_current_artifact_autopsy_v1_verification.json` (truthful=`true`, all 5 invariants green).
- Notebook: `notebooks/m365/INV-M365-DK-standalone-graph-runtime-pack-p0-current-artifact-autopsy-v1.ipynb`.
- This document closes phase `P0A`. Phase `P0B` (target-state intent) is the next bounded act.
