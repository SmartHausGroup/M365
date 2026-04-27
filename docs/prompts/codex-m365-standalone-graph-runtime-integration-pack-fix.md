# Execution Prompt - Fix The M365 Standalone Graph Runtime Integration Pack

Plan Reference: `plan:m365-standalone-graph-runtime-integration-pack-fix`  
Parent Plan: `plan:m365-standalone-graph-runtime-integration-pack`  
Repo: `/Users/smarthaus/Projects/GitHub/M365`  
Primary Fix Plan: `plans/m365-standalone-graph-runtime-integration-pack-fix/m365-standalone-graph-runtime-integration-pack-fix.md`

## Mission

Repair the incomplete Claude closeout for the M365 standalone Graph runtime Integration Pack. The current `com.smarthaus.m365@1.1.0` artifact is not final `GO`. It contains useful runtime foundation, but conformance and acceptance are over-claimed.

Continue until the fix pack is complete unless a true hard blocker is reached. If UCP/MCP/governance returns an error, treat that error as the next required task: create the missing notebook, invariant, plan, scope correction, evidence, or metadata exactly as requested, rerun the gate, and continue.

## Read First

- `AGENTS.md`
- `.cursor/rules/*.mdc`
- `Operations/NORTHSTAR.md`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`
- `plans/m365-standalone-graph-runtime-integration-pack/m365-standalone-graph-runtime-integration-pack.md`
- `plans/m365-standalone-graph-runtime-integration-pack-fix/m365-standalone-graph-runtime-integration-pack-fix.md`
- `src/ucp_m365_pack/client.py`
- `src/ucp_m365_pack/setup_schema.json`
- `src/m365_runtime/launcher.py`
- `src/m365_runtime/auth/oauth.py`
- `src/m365_runtime/auth/app_only.py`
- `src/m365_runtime/auth/token_store.py`
- `scripts/ci/verify_standalone_graph_runtime_pack.py`
- `scripts/ci/acceptance_standalone_graph_runtime_pack.py`

## Current Known Failures

1. The installed payload still contains source-root fallback strings:
   - `M365_REPO_ROOT`
   - `SMARTHAUS_M365_REPO_ROOT`
   - `M365_REGISTRY_PATH`
   - legacy `M365_OPS_ADAPTER_URL`
   - parent search for `registry/agents.yaml`

2. Conformance is incomplete:
   - `no_source_repo_dependency_contract` says pass, but the payload disproves it.
   - The verifier scans only `src/m365_runtime`, not the complete unpacked payload.

3. Runtime auth service is incomplete:
   - Existing service exposes `/v1/auth/status` and `/v1/auth/clear`.
   - It lacks start/check sign-in endpoints.
   - Token store is not integrated into service readiness.

4. Acceptance is insufficient:
   - It calls internal `invoke()` directly with a synthetic token.
   - It does not prove auth start/check, token storage, readiness after auth, or UCP-facing client invocation.

5. UCP action mapping is missing:
   - Existing actions like `users.read`, `sites.root`, and `directory.org` are not mapped to `graph.users.list`, `graph.sites.root`, and `graph.org_profile`.

6. UCP activation plan is missing:
   - Referenced plan `plan:ucp-m365-standalone-graph-runtime-pack-activation` does not exist under `/Users/smarthaus/Projects/GitHub/UCP/plans/`.

7. Evidence hashes are stale:
   - Some docs cite old bundle/manifest SHAs that do not match the current `SHA256SUMS`.

## Required Fix Order

1. Mark the current `1.1.0` release state as fix-required/NO-GO until this package closes.
2. Remove source-root fallback from packaged `ucp_m365_pack/client.py`.
3. Widen `verify_standalone_graph_runtime_pack.py` to unpack the final bundle and scan the full payload.
4. Make conformance fail if forbidden payload strings or missing auth endpoints are present.
5. Implement auth lifecycle endpoints:
   - `POST /v1/auth/start`
   - `POST /v1/auth/check`
   - `GET /v1/auth/status`
   - `POST /v1/auth/clear`
6. Integrate `TokenStore.from_setup()` into launcher runtime state and readiness.
7. Add UCP action alias mapping from existing action IDs to runtime `graph.*` action IDs.
8. Replace acceptance with installed-runtime HTTP + `ucp_m365_pack.client.execute_m365_action()` acceptance.
9. Rebuild as the next patch version, copy to `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/<next-version>/`, and regenerate all evidence.
10. Create or hand off the missing UCP activation plan under `/Users/smarthaus/Projects/GitHub/UCP` governance. Do not claim UCP live acceptance until that plan executes.

## Acceptance Requirements

- Full payload scan proves no forbidden source-root fallback strings.
- Runtime auth start/check/status/clear endpoints are present and tested.
- Mocked auth/check stores a token through the configured token store.
- Readiness transitions from `not_ready/auth` to `ready/success` through the HTTP service path.
- `execute_m365_action()` maps legacy M365 actions to runtime `graph.*` action IDs.
- Acceptance invokes a read-only action through `execute_m365_action()` against the installed runtime URL.
- Final conformance and SHA evidence match the rebuilt artifact.
- Docs no longer cite stale hashes.
- Operations trackers state the truthful boundary: M365 artifact fixed; UCP live activation remains pending until UCP plan completes.

## Do Not Do

- Do not store usernames/passwords.
- Do not log tokens, refresh tokens, auth codes, client secrets, assertions, private keys, or certificate bytes.
- Do not leave conformance green while the payload contains forbidden source-root strings.
- Do not claim UCP acceptance without creating/executing the UCP plan.
- Do not move Graph implementation into UCP.
- Do not add write/mutation Graph actions.

## Hard Blockers

Only stop if:

- MCP `validate_action` denies and requires human approval that cannot be satisfied by a plan/evidence/scope correction.
- Microsoft tenant/admin consent is needed for live proof and no credentials/consent are available.
- A rule would require username/password auth or secret leakage.
- The UCP repo has contradictory governance requiring CTO decision.

If blocked, produce a blocker report with exact command/action, exact response, completed evidence, and the smallest required CTO/admin action.
