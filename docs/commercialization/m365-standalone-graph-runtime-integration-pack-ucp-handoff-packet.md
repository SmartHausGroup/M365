# M365 Standalone Graph Runtime Integration Pack - P8 UCP Marketplace Activation Handoff Packet

**Plan:** `plan:m365-standalone-graph-runtime-integration-pack:R9`
**Phase:** `P8` UCP Marketplace Activation Boundary (M365-side handoff)
**Date:** 2026-04-26
**Owner:** SMARTHAUS

This packet is the M365-side handoff to UCP. It declares the artifact path, manifest digest, conformance evidence, setup schema, launch contract, and the named sibling UCP plan under which UCP-side install/launch/setup/auth/readiness work must execute. M365 does not mutate UCP source under this plan.

## 1. Artifact Identity

| Field | Value |
| --- | --- |
| Pack ID | `com.smarthaus.m365` |
| Version | `1.1.1` |
| Distribution mode | `marketplace` |
| Visibility | `optional` |
| Schema version | `0.2.0` |
| Display name | `Microsoft 365` |
| Local store | `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/1.1.1/` |
| Bundle file | `com.smarthaus.m365-1.1.1.ucp.tar.gz` |
| Bundle SHA256 | `b4f3ae56064bdb2d1047dc15308fc6b2df2c8adac334dece11ac8c66b4b62b0f` |
| Manifest SHA256 | `4ece998d2e17888b65bf267d79c156d6d2d5f2a198154cff8d9fb2003b3673c2` |
| Conformance SHA256 | `e9cbea708346a5b5ed8f474a90e989df61b83b4be33314f9ffc7e889b013f8fa` |
| Build determinism | Two consecutive `python scripts/ci/build_standalone_graph_runtime_pack.py` runs produce byte-identical `payload.tar.gz` and `*.ucp.tar.gz` (gzip mtime=0 + normalized TarInfo). |
| Setup schema ref | `setup_schema.json` |
| Notes | Supersedes the historical `1.1.0` artifact, which was over-claimed and is recorded as fix-required in `plans/m365-standalone-graph-runtime-integration-pack-fix/`. |

## 2. Payload Inventory (inside `payload.tar.gz`)

```
m365_runtime/__init__.py
m365_runtime/__main__.py
m365_runtime/_forbidden_tokens.py
m365_runtime/audit.py
m365_runtime/auth/__init__.py
m365_runtime/auth/app_only.py
m365_runtime/auth/oauth.py
m365_runtime/auth/token_store.py
m365_runtime/graph/__init__.py
m365_runtime/graph/actions.py
m365_runtime/graph/client.py
m365_runtime/graph/errors.py
m365_runtime/graph/registry.py
m365_runtime/health.py
m365_runtime/launcher.py
m365_runtime/setup.py
m365_runtime/state.py
registry/action_registry.yaml
registry/agents.yaml
setup_schema.json
ucp_m365_pack/__init__.py
ucp_m365_pack/client.py
ucp_m365_pack/contracts.py
ucp_m365_pack/setup_schema.json
```

The runtime is inside the artifact. There is no `M365_REPO_ROOT` lookup, no `../M365` walk, no `UCP_ROOT` / `REPOS_ROOT` requirement, and no `from ops_adapter` import inside the packaged runtime tree.

## 3. Launch Contract

| Field | Value |
| --- | --- |
| Module | `m365_runtime` |
| Entry command | `python -m m365_runtime` |
| Default host | `127.0.0.1` |
| Default port | `9300` |
| Health path | `GET /v1/health/readiness` |
| Auth status path | `GET /v1/auth/status` |
| Auth clear path | `POST /v1/auth/clear` |
| Actions list path | `GET /v1/actions` |
| Action invoke path | `POST /v1/actions/{action_id}/invoke` |
| Read-only fence | `read_only=true`, `mutation_fence=true` |

The launcher resolves its installed root from the package file location and never reads `M365_REPO_ROOT` or any sibling-repo env var. Launching produces exactly one outcome from `{started, port_conflict, config_invalid, dependency_missing, launch_unknown}`.

## 4. Setup Contract (operator-supplied via UCP)

Required fields (inside the packaged `setup_schema.json`):

- `M365_TENANT_ID`
- `M365_CLIENT_ID`
- `M365_AUTH_MODE` ∈ `{auth_code_pkce, device_code, app_only_secret, app_only_certificate}` (`password` is forbidden by validation)
- `M365_SERVICE_ACTOR_UPN`

Optional fields:

- `M365_RUNTIME_URL` (preferred when UCP routes through the local runtime)
- `M365_REDIRECT_URI`, `M365_DEVICE_CODE_FALLBACK`
- `M365_APP_ONLY_CLIENT_SECRET_REF`, `M365_APP_ONLY_CERTIFICATE_REF`
- `M365_TOKEN_STORE` ∈ `{keychain, encrypted_pack_local}`
- `M365_KEYCHAIN_SERVICE`, `M365_ENCRYPTED_PACK_LOCAL_ALLOWED`
- `M365_GRANTED_SCOPES`
- Legacy ops-adapter fields (`M365_OPS_ADAPTER_URL`, `M365_SERVICE_JWT_HS256_SECRET`, etc.) are accepted but no longer required.

Username/password is rejected at validation. References (Keychain item names, certificate refs) are stored, never the raw secret.

## 5. Auth Contract

| Endpoint | Behavior |
| --- | --- |
| `GET /v1/auth/status` | Returns `{state ∈ {unconfigured, auth_required, signed_in, consent_required}, auth_mode}` |
| `POST /v1/auth/clear` | Removes the local access token; transitions to `auth_required` |
| Sign-in flow | Authorization Code + PKCE (preferred) with device-code fallback. App-only flows use client_credentials with secret or RS256 JWT-bearer certificate assertion. |

PKCE state, nonce, and verifier are 16/16/32 bytes from `os.urandom`. Tokens never appear in logs, audit, evidence, or notebook artifacts.

## 6. Health/Readiness Contract

`GET /v1/health/readiness` returns a `vector` over service / auth / token / graph / permission / contract / artifact / source / audit, plus a `state` of `ready | not_ready` and a `label` (the first failing clause or `success`). `Ready=true` requires every clause to be `true` and not `unknown`.

## 7. Action Contract

`GET /v1/actions` lists 11 read-only Microsoft Graph actions. `POST /v1/actions/{action_id}/invoke` returns one of `{success, auth_required, consent_required, permission_missing, throttled, graph_unreachable, policy_denied, mutation_fence, internal_error}` plus a redacted bounded audit envelope. Any action_id not in the read-only registry is fenced with `mutation_fence` and never forwarded to Graph. Mutations remain fenced until a separate mutation-governance plan is approved.

## 8. Lifecycle Contract

UCP-driven lifecycle:

| Operation | Effect |
| --- | --- |
| Install | Extract bundle into `<install_root>/`. UCP retains the `manifest.json`, `conformance.json`, `provenance.json`, and `SHA256SUMS` for evidence. |
| Enable | UCP allows the launcher to be started by the host. |
| Launch | UCP invokes `python -m m365_runtime --host <host> --port <port>` from `<install_root>/`. |
| Stop | UCP terminates the runtime process. |
| Restart | UCP stops then launches. |
| Clear-auth | UCP calls `POST /v1/auth/clear`, the runtime removes the local access token. |
| Uninstall | UCP removes `<install_root>/` and clears any cached UCP-side setup state. |

## 9. UCP-Side Plan Dependency

UCP-side install/launch/setup/auth/readiness/action work is governed by a separate UCP plan. Until that plan exists, UCP integration with this artifact must remain on `development`. This M365 plan does not authorize edits in `/Users/smarthaus/Projects/GitHub/UCP/`.

Recommended UCP-side plan name (to be created in the UCP repo by a UCP-owned planner):

- `plan:ucp-m365-standalone-graph-runtime-pack-activation`

Recommended UCP-side scope:

1. Discover the local pack at `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/1.1.1/`.
2. Verify `SHA256SUMS` against the bytes of `manifest.json`, `conformance.json`, and the bundle file.
3. Read the manifest's `runtime` block and surface the launch command, default host/port, and health/auth/actions paths to the operator.
4. Drive the declared setup schema for the operator. Require `M365_TENANT_ID`, `M365_CLIENT_ID`, `M365_AUTH_MODE`, `M365_SERVICE_ACTOR_UPN`. Reject `password` at the UI layer for symmetry with the runtime validator.
5. Launch the runtime via the manifest's entrypoint command.
6. Poll `GET /v1/health/readiness`. UCP must only project `Ready=true` to the operator when the runtime returns the literal `state="ready"` and `label="success"`.
7. Drive `POST /v1/auth/clear` for clear-sign-in.
8. Project read-only Graph actions through `POST /v1/actions/{action_id}/invoke` with operator-supplied params.

## 10. Boundary Lock Recap

- M365 owns: Microsoft Graph runtime, Microsoft auth flows, token storage, action registry, permission matrix, audit, packaging.
- UCP owns: marketplace lifecycle, host runtime, setup driving, action invocation, readiness projection, cross-pack governance.
- M365 does not embed UCP code. UCP must not embed Microsoft Graph code.
- M365 must not mutate UCP source under this plan.

## 11. Predecessor Evidence

- P0 autopsy: `notebooks/m365/INV-M365-DK-...`, `configs/generated/standalone_graph_runtime_integration_pack_p0_current_artifact_autopsy_v1_verification.json`.
- P1 calculus: `docs/ma/m365-standalone-graph-runtime-integration-pack-formal-calculus.md`.
- P2 lemmas: `docs/ma/lemmas/L98_m365_standalone_graph_runtime_pack_lemmas_v1.md`, `invariants/lemmas/L98_..._v1.yaml`, `artifacts/scorecards/scorecard_l98.json`.
- P3 scorecard: `artifacts/scorecards/scorecard_standalone_graph_runtime_pack_p3.json`.
- P4-P5 runtime: `src/m365_runtime/`.
- P6 verifier: `scripts/ci/verify_standalone_graph_runtime_pack.py`, `configs/generated/standalone_graph_runtime_pack_verification.json` (`overall_ok=true`, 6 checks).
- P7 packaging: `dist/m365_pack/`, `IntegrationPacks/M365/1.1.1/`, `tests/test_m365_runtime_p7_packaging.py` (`8 passed`).

## 12. Closure

- Handoff packet ready for UCP planner to consume.
- M365-side `P8` is closed when this packet exists.
- Live UCP install/launch/setup/auth/readiness/action acceptance is gated on a sibling UCP plan that does not exist in `/Users/smarthaus/Projects/GitHub/UCP/plans/` at the time of writing; this is the truthful boundary.
