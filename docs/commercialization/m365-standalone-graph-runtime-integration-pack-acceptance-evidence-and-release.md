# M365 Standalone Graph Runtime Integration Pack - P9 Acceptance Evidence And Release

**Plan:** `plan:m365-standalone-graph-runtime-integration-pack:R9`
**Phase:** `P9` Acceptance Evidence And Release
**Date:** 2026-04-26
**Owner:** SMARTHAUS

This document captures the bounded acceptance evidence the standalone M365 Graph runtime Integration Pack must satisfy before release, and records the release decision.

## P9A - Source-Removal Test

The acceptance harness `scripts/ci/acceptance_standalone_graph_runtime_pack.py`:

1. Locates the latest installed pack at `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/<latest>/`.
2. Verifies `SHA256SUMS` against the bytes of `manifest.json`, `conformance.json`, and `com.smarthaus.m365-<version>.ucp.tar.gz`.
3. Extracts the bundle and inner `payload.tar.gz` into a temporary directory.
4. Spawns a fresh Python child whose `PYTHONPATH` contains only the extracted pack root - **the M365 source repo is NOT on this PATH** - and exercises the runtime end-to-end.

This is the source-removal acceptance: if the runtime depended on the M365 source repo, the child process would fail to import or to launch. It does neither.

## P9B - Mock Acceptance

The harness child process performs:

- `import m365_runtime` -> succeeds.
- `plan_launch(env={...valid setup env...}).outcome == "started"`.
- `invoke(action_id="graph.org_profile", ..., transport=httpx.MockTransport(handler))` returns `status_class == "success"` against the mocked Microsoft Graph response `{"value": []}`.
- `invoke(action_id="graph.users.create", ...)` (a write action that is not in the read-only registry) returns `status_class == "mutation_fence"`. Mutations are fenced even when the operator supplies a token and write-class scope.
- The audit envelope for the `graph.org_profile` call returns `extra_redacted.params.client_secret == "[redacted]"` for an injected `client_secret` field; no token or secret material reaches the audit.
- `compose_readiness(...)` before sign-in reports `state="not_ready"` and `label="auth"`. Readiness is fail-closed before auth completes.

## P9C - Live Read-Only Acceptance Through UCP

Live UCP-driven acceptance is gated on the sibling UCP plan `plan:ucp-m365-standalone-graph-runtime-pack-activation` (see `docs/commercialization/m365-standalone-graph-runtime-integration-pack-ucp-handoff-packet.md`). M365 does not mutate UCP source under this plan. The truthful boundary is recorded:

- The M365-side artifact, contracts, packaging, and acceptance harness are complete.
- Live UCP install/launch/setup/auth/action acceptance must be opened in a separate UCP-owned plan.
- No UCP-side activation plan exists in `/Users/smarthaus/Projects/GitHub/UCP/plans/` at the time of writing.

## P9D - Readiness Proof

`compose_readiness` over the installed root produces a vector covering service / auth / token / graph / permission / contract / artifact / source / audit. Before sign-in:

```
{ "svc": true, "auth": false, "tok": false, "graph": false, "perm": false, "ctr": true, "art": true, "src": true, "aud": true }
state = not_ready, label = auth
```

This is the fail-closed default the plan requires. Once a real Microsoft sign-in completes (P9C), the auth/token/graph/permission probes must turn `true` before `Ready=true` is permitted.

## P9E - Evidence Packet

| Artifact | Path |
| --- | --- |
| Acceptance harness | `scripts/ci/acceptance_standalone_graph_runtime_pack.py` |
| Acceptance evidence (machine-readable) | `artifacts/diagnostics/m365_standalone_graph_runtime_pack_acceptance.json` |
| Verifier | `scripts/ci/verify_standalone_graph_runtime_pack.py` |
| Verifier evidence | `configs/generated/standalone_graph_runtime_pack_verification.json` |
| P0 autopsy notebook | `notebooks/m365/INV-M365-DK-...` |
| P0 autopsy verification | `configs/generated/standalone_graph_runtime_integration_pack_p0_current_artifact_autopsy_v1_verification.json` |
| P1 calculus | `docs/ma/m365-standalone-graph-runtime-integration-pack-formal-calculus.md` |
| P1 calculus verification | `configs/generated/standalone_graph_runtime_integration_pack_p1_formal_calculus_v1_verification.json` |
| P2 lemma | `docs/ma/lemmas/L98_m365_standalone_graph_runtime_pack_lemmas_v1.md` |
| P2 lemma invariants | `invariants/lemmas/L98_m365_standalone_graph_runtime_pack_lemmas_v1.yaml` |
| P2 lemma scorecard | `artifacts/scorecards/scorecard_l98.json` |
| P2 lemma evidence | `notebooks/m365/INV-M365-DM-...`, `notebooks/lemma_proofs/L98_...` |
| P3 prototype notebook | `notebooks/m365/INV-M365-DN-...` |
| P3 scorecard | `artifacts/scorecards/scorecard_standalone_graph_runtime_pack_p3.json` |
| Runtime modules | `src/m365_runtime/` |
| UCP-facing client (P6) | `src/ucp_m365_pack/client.py`, `src/ucp_m365_pack/setup_schema.json` |
| Build script | `scripts/ci/build_standalone_graph_runtime_pack.py` |
| Marketplace bundle | `dist/m365_pack/com.smarthaus.m365-1.1.1.ucp.tar.gz` |
| Installed pack | `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/1.1.1/` |
| UCP handoff packet | `docs/commercialization/m365-standalone-graph-runtime-integration-pack-ucp-handoff-packet.md` |

## P9F - Release Decision

| Clause | Status |
| --- | --- |
| `integrity_sha256sums` | **PASS** |
| `runtime_imports_from_extracted_bundle` | **PASS** |
| `runtime_version_locked` | **PASS** |
| `action_count_locked` (11 read-only actions) | **PASS** |
| `launch_outcome_started` | **PASS** |
| `action_returns_success_against_mock_graph` | **PASS** |
| `audit_redacts_secrets_in_params` | **PASS** |
| `mutation_action_fenced` | **PASS** |
| `readiness_before_signin_is_not_ready` | **PASS** |
| `readiness_before_signin_label_is_auth` | **PASS** |

**Initial release decision (2026-04-26, withdrawn):** the original `com.smarthaus.m365@1.1.0` GO claim was withdrawn after static review found that the packaged `ucp_m365_pack/client.py` still walked source-repo paths, the runtime auth contract lacked `/v1/auth/start` and `/v1/auth/check`, the acceptance harness used a synthetic token rather than installed-runtime HTTP plus the UCP client path, legacy action IDs were not mapped to runtime `graph.*` IDs, the referenced UCP activation plan did not exist, and several evidence hashes were stale. See `plans/m365-standalone-graph-runtime-integration-pack-fix/` for the full finding set.

**Final release decision (2026-04-26): GO (M365-side)** for `com.smarthaus.m365@1.1.1`. The fix-pack acceptance harness drives `/v1/auth/start` and `/v1/auth/check` against an installed-runtime FastAPI service spawned from the extracted bundle, uses an in-memory token store backend, observes readiness flip from `not_ready/auth` to `ready/success` only after auth completes, dispatches a read-only Graph action through `ucp_m365_pack.client.execute_m365_action()` with the legacy alias `users.read` correctly projected to `graph.users.list`, and confirms the mutation fence still rejects unknown action IDs. All 20 acceptance clauses pass. Live UCP through-the-installed-pack acceptance remains the explicit scope of the sibling UCP plan handed off in `m365-standalone-graph-runtime-integration-pack-ucp-activation-plan-handoff.md`.

### Tenant / license limitations to surface in release notes

- Microsoft tenant must register an Entra app and grant the read-only Graph scopes used by the action registry.
- Authorization Code + PKCE requires a redirect URI reachable by the operator's machine.
- Device-code fallback requires the operator to complete the device-flow on a separate browser session.
- App-only flows require admin consent for application permissions.
- ServiceHealth.Read.All requires Microsoft 365 admin role; if absent, `graph.servicehealth` returns `permission_missing`.
- Mail.Read / Calendars.Read are user-scope; mailbox-disabled accounts will return `permission_missing` instead of mailbox content.
- Graph throttling is bounded by retry/`Retry-After`; tenants under heavy throttle may see `throttled` end-states.

## Closure

- `P9A` source-removal: PASS.
- `P9B` mock acceptance: PASS.
- `P9C` live UCP read-only acceptance: deferred to the sibling UCP plan; M365-side artifact is ready.
- `P9D` readiness proof: PASS (vector recorded above).
- `P9E` evidence packet: assembled.
- `P9F` release decision: **GO**.
