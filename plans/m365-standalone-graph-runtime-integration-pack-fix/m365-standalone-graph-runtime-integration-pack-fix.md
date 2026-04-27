# Plan: M365 Standalone Graph Runtime Integration Pack Fix Pack

**Plan ID:** `m365-standalone-graph-runtime-integration-pack-fix`
**Parent plan ID:** `m365-standalone-graph-runtime-integration-pack`
**Status:** Superseded / readiness correction required - `R1`-`R8` produced the historical `1.1.1` snapshot, but the 2026-04-27 installed-payload live smoke proved formal readiness is still false (`art=false`) and the active corrective target is now `com.smarthaus.m365@0.1.2`.
**Date:** 2026-04-26
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-standalone-graph-runtime-integration-pack-fix:R0`
**North Star alignment:** `Operations/NORTHSTAR.md` - truthful M365-only integration, fail-closed readiness, secure auth, policy enforcement, and audit coverage.
**Purpose:** Correct the incomplete Claude closeout for `com.smarthaus.m365@1.1.0` before it is treated as a finished real Microsoft 365 integration pack.

## Review Verdict

Claude created a meaningful foundation: `src/m365_runtime/` exists, the `1.1.0` artifact is present in `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/1.1.0/`, and `SHA256SUMS` passes. However, the work is incomplete and the current `GO` is over-claimed.

The current artifact must be treated as **NO-GO / fix required** until this package is complete.

## Findings

### F1 - Payload Source-Repo Dependency Claim Is False

Evidence:

- Installed payload file `ucp_m365_pack/client.py` still contains:
  - `M365_REPO_ROOT`
  - `SMARTHAUS_M365_REPO_ROOT`
  - `M365_REGISTRY_PATH`
  - parent-directory search for `registry/agents.yaml`
  - legacy `M365_OPS_ADAPTER_URL`
- `dist/m365_pack/evidence/conformance.json` says `no_source_repo_dependency_contract` is `pass`.
- `scripts/ci/verify_standalone_graph_runtime_pack.py` only scans `src/m365_runtime`, not the complete payload that UCP installs.

Required fix:

- Remove source-repo and sibling-root fallback behavior from the packaged UCP client path.
- Resolve registry/config only from installed artifact paths or explicit UCP-provided setup state.
- Widen verifier/conformance checks to unpack the final bundle and scan the entire payload.
- Rebuild the artifact only after the complete payload scan is green.

### F2 - Runtime Auth Contract Is Not Complete

Evidence:

- `src/m365_runtime/launcher.py` exposes `/v1/auth/status` and `/v1/auth/clear`.
- It does not expose start sign-in, check sign-in, callback handling, or token acquisition endpoints.
- The runtime keeps `state["access_token"] = None` and never sets it through the HTTP service.
- `compose_readiness()` is called with `store=None`, so token-store readiness cannot become true through the service.

Required fix:

- Add HTTP auth lifecycle endpoints, at minimum:
  - `POST /v1/auth/start`
  - `POST /v1/auth/check`
  - `POST /v1/auth/clear`
  - `GET /v1/auth/status`
- Support `auth_code_pkce`, `device_code`, `app_only_secret`, and `app_only_certificate` through secure references.
- Integrate `TokenStore.from_setup()` into launcher state and readiness.
- Prove readiness can become `ready/success` using a mocked token and mocked Graph only through the service path.

### F3 - Acceptance Harness Does Not Prove The Release Claim

Evidence:

- `scripts/ci/acceptance_standalone_graph_runtime_pack.py` calls `m365_runtime.graph.actions.invoke()` directly with `access_token='SYNTHETIC_TEST_TOKEN'`.
- It does not call the installed runtime HTTP auth endpoints to acquire/store/check a token.
- It does not prove readiness after token acquisition.
- It does not go through `ucp_m365_pack.client.execute_m365_action()`.
- It does not prove UCP install/launch/setup/auth/action acceptance.

Required fix:

- Replace direct `invoke()` acceptance with installed-artifact service acceptance.
- Start the FastAPI app from the extracted artifact.
- Drive auth start/check with mocked Microsoft endpoints and token-store-backed state.
- Drive at least one read-only action through `ucp_m365_pack.client.execute_m365_action()` with `M365_RUNTIME_URL` set.
- Assert readiness transitions from `not_ready/auth` to `ready/success`.
- Keep live tenant acceptance clearly separate and blocked until UCP plan execution.

### F4 - UCP Runtime Action Mapping Is Missing

Evidence:

- Existing M365 pack actions in `registry/agents.yaml` include names such as `users.read`, `sites.root`, and `directory.org`.
- New runtime actions are named `graph.users.list`, `graph.sites.root`, `graph.org_profile`, etc.
- `execute_m365_action()` sends dotted action names as-is, so `sites.root` is sent to `/v1/actions/sites.root/invoke`, which is not in the runtime registry.
- Existing tests do not prove legacy M365 action IDs map into the new runtime action registry.

Required fix:

- Add an explicit alias/mapping table from existing M365 action IDs to runtime `graph.*` action IDs.
- Add tests proving representative mappings:
  - `directory.org -> graph.org_profile`
  - `users.read -> graph.users.list`
  - `sites.root -> graph.sites.root`
  - `sites.search -> graph.sites.search`
  - `groups.read -> graph.groups.list`
  - `teams.read -> graph.teams.list`
- Unknown or write actions must return `mutation_fence` or a deterministic fail-closed class.

### F5 - UCP Activation Plan Is Referenced But Missing

Evidence:

- Docs reference `plan:ucp-m365-standalone-graph-runtime-pack-activation`.
- `/Users/smarthaus/Projects/GitHub/UCP/plans/` does not contain that plan.
- The original acceptance target included UCP install/launch/setup/auth/action acceptance.

Required fix:

- Do not claim final end-to-end completion until the UCP plan exists and is either complete or explicitly blocked.
- Create the sibling UCP activation plan under UCP governance when moving to that repo.
- The UCP plan must install the `1.1.x` artifact, launch the installed runtime, drive setup/auth/health, and execute a read-only action through UCP.

### F6 - Evidence Hashes Are Stale/Inconsistent

Evidence:

- Current installed bundle SHA is `281e58a80fb73d672f36f03a730c7728fbdc6c83988ff8255218b73a2e4e5166`.
- Current manifest SHA is `19895e060a7ee4b8f407b5951fe39b1ab83d800441c2cc86c337e8dbaa50fe8c`.
- Current conformance SHA is `5d0c5470ff0b97cd2b485f40cc62c8696e710da3450f03ea554a85fc60bcdf09`.
- The parent plan and UCP handoff docs still cite stale bundle/manifest hashes.

Required fix:

- Regenerate all evidence after the artifact rebuild.
- Synchronize plan, handoff, acceptance, provenance, conformance, SHA256SUMS, action log, execution plan, and file index to the same hash truth.

## Fix Requirements

- `R1` Publish this review/fix baseline and mark the previous `GO` as over-claimed until repaired.
- `R2` Remove source-repo fallback from packaged payload and verifier coverage.
- `R3` Complete runtime auth lifecycle endpoints and token-store-backed readiness.
- `R4` Repair UCP action ID mapping into runtime `graph.*` actions.
- `R5` Replace acceptance harness with installed-runtime HTTP and UCP-client-path acceptance.
- `R6` Rebuild the package, copy it to `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/<next-version>/`, and pass complete-payload conformance.
- `R7` Open or complete the UCP activation plan under `/Users/smarthaus/Projects/GitHub/UCP` governance.
- `R8` Synchronize stale hashes and governance trackers.

## Acceptance Criteria

- Complete payload scan finds zero `M365_REPO_ROOT`, `SMARTHAUS_M365_REPO_ROOT`, `M365_REGISTRY_PATH`, `../M365`, sibling repo lookup, or source-tree fallback strings outside explicitly named verifier fixtures.
- `ucp_m365_pack/client.py` resolves installed resources from the installed artifact root, not source root env vars.
- Runtime auth lifecycle endpoints exist and are tested through FastAPI.
- Token store is integrated into readiness, and mocked acceptance proves `not_ready/auth -> ready/success`.
- `execute_m365_action()` with `M365_RUNTIME_URL` maps existing M365 action names to runtime `graph.*` action names.
- Acceptance goes through the installed artifact service and UCP-facing client path, not direct internal `invoke()`.
- Conformance fails when forbidden payload strings or missing auth endpoints are present.
- Release docs no longer claim final end-to-end `GO` while UCP activation remains unexecuted.
- UCP activation plan exists or the package is explicitly marked blocked by missing UCP plan.

## Stop Conditions

- Any attempt to leave conformance marked pass while the payload still contains source-root fallbacks.
- Any attempt to claim full runtime auth without start/check/token-store-backed readiness.
- Any attempt to claim UCP acceptance without a UCP plan and UCP-side execution.
- Any username/password auth support.
- Any token/secret/private-key logging.

## Validation Commands

Claude must run only after MCP admits the run:

```bash
PYTHONPATH=src python3 scripts/ci/verify_standalone_graph_runtime_pack.py
PYTHONPATH=src python3 scripts/ci/acceptance_standalone_graph_runtime_pack.py
PYTHONPATH=src:/Users/smarthaus/Projects/GitHub/UCP-codex-stable/src .venv/bin/pytest -q tests/test_m365_runtime_p4_runtime_and_auth.py tests/test_m365_runtime_p5_graph_actions.py tests/test_m365_runtime_p5_launcher_app.py tests/test_m365_runtime_p7_packaging.py tests/test_ucp_m365_pack_contracts.py tests/test_ucp_m365_pack_client.py
env LC_ALL=C LANG=C shasum -a 256 -c SHA256SUMS
```

Run the checksum command from the final Integration Pack version directory.

## Governance Closure

- [x] Fix pack created.
- [x] Execution plan updated.
- [x] Project file index updated.
- [x] Action log updated.
- [x] Runtime/package fixes implemented (`1.1.1`).
- [x] UCP activation plan handoff prepared (`docs/commercialization/m365-standalone-graph-runtime-integration-pack-ucp-activation-plan-handoff.md`); UCP-side plan must be opened by a UCP planner.
- [x] Evidence regenerated (full-payload verifier 9/9, fix-pack acceptance 20/20, install-dir SHA256SUMS verify-clean).

## Superseded State

- Historical artifact: `com.smarthaus.m365@1.1.1`.
- Install dir: `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/1.1.1/`.
- Bundle SHA256: `b4f3ae56064bdb2d1047dc15308fc6b2df2c8adac334dece11ac8c66b4b62b0f` (deterministic across rebuilds).
- Manifest SHA256: `4ece998d2e17888b65bf267d79c156d6d2d5f2a198154cff8d9fb2003b3673c2`.
- Conformance SHA256: `e9cbea708346a5b5ed8f474a90e989df61b83b4be33314f9ffc7e889b013f8fa`.
- Fix-pack acceptance evidence: `artifacts/diagnostics/m365_standalone_graph_runtime_pack_acceptance.json` (`release_decision = GO`, 20/20 clauses).
- Verifier evidence: `configs/generated/standalone_graph_runtime_pack_verification.json` (`overall_ok = true`, 9 checks).
- Combined regression `pytest tests/test_m365_runtime_p4_runtime_and_auth.py tests/test_m365_runtime_p5_graph_actions.py tests/test_m365_runtime_p5_launcher_app.py tests/test_m365_runtime_p7_packaging.py tests/test_m365_runtime_fix_auth_lifecycle.py tests/test_ucp_m365_pack_contracts.py tests/test_ucp_m365_pack_client.py`: `76 passed`.

## 2026-04-27 Correction

The `1.1.1` snapshot is no longer the active readiness authority. A live installed-payload smoke proved real SmartHaus Microsoft device-code sign-in and live `graph.me` success, but readiness still returned `not_ready/art` because the payload-root artifact contract does not match the runtime health probe. Plain dependency behavior also remains implicit, and release acceptance still needs an unpatched real-socket UCP client path. The active corrective plan is `plan:m365-standalone-graph-runtime-pack-0-1-2-readiness-fix`, targeting `com.smarthaus.m365@0.1.2`.
