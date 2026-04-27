# Plan: M365 Standalone Graph Runtime Pack 0.1.2 Readiness Fix

**Plan ID:** `m365-standalone-graph-runtime-pack-0-1-2-readiness-fix`
**Parent plan ID:** `m365-standalone-graph-runtime-integration-pack`
**Supersedes:** `m365-standalone-graph-runtime-integration-pack-fix` final `1.1.1` readiness claim
**Status:** Active - formal fix plan created; implementation not started.
**Date:** 2026-04-27
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-standalone-graph-runtime-pack-0-1-2-readiness-fix:R0`
**North Star alignment:** `Operations/NORTHSTAR.md` - truthful M365-only integration, fail-closed readiness, secure Microsoft auth, and auditable runtime execution.

## Repository And Branch Guardrails

This plan executes in the M365 repository only.

- Required repo root: `/Users/smarthaus/Projects/GitHub/M365`.
- Required branch: `development`, unless the CTO explicitly directs a different branch.
- Required remote: `https://github.com/SmartHausGroup/M365.git`.
- Allowed implementation/edit scope: `/Users/smarthaus/Projects/GitHub/M365/**`.
- Allowed artifact output scope: `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/**`.
- Read-only comparison scope: `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/1.1.0/**` and `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/1.1.1/**`.
- Forbidden mutation scope under this plan: `/Users/smarthaus/Projects/GitHub/UCP/**`, `/Users/smarthaus/Projects/GitHub/UCP-codex-stable/**`, and every other sibling repo under `/Users/smarthaus/Projects/GitHub/**`.

Claude must run `pwd`, `git rev-parse --show-toplevel`, `git branch --show-current`, and `git remote -v` before starting `C0`. If any value does not match the required repo/branch/remote, fail closed and ask for direction.

## Decision Summary

- Correct the pack line to `com.smarthaus.m365@0.1.2`.
- Treat `1.1.0` and `1.1.1` as mis-versioned local prerelease snapshots, not formal release artifacts.
- Do not claim formal readiness until the installed payload can launch, satisfy readiness, and serve the UCP-facing client over a real local socket with an explicit dependency contract.

## Options Considered

- Patch `1.1.1` in place.
  - Pro: Fastest string-level correction.
  - Con: Breaks provenance and hides the fact that `1.1.1` already failed installed-payload readiness.

- Ship `1.1.2`.
  - Pro: Normal semantic patch progression from the mistaken line.
  - Con: Keeps the wrong major/minor version family alive.

- Rebase the real integration-pack release line to `0.1.2`.
  - Pro: Matches actual maturity: real live delegated Graph works, but pack readiness is still pre-1.0.
  - Con: Requires updating build, manifest, runtime, docs, provenance, local store path, and trackers together.

## Evaluation Criteria

- Mathematical soundness: readiness must be a conjunction over version, artifact layout, dependency closure, source independence, auth, Graph, permissions, audit, and provenance.
- Deterministic guarantees: artifact build, dependency resolution, and readiness labels must replay identically.
- Invariant enforceability: every acceptance condition must have a CI or script gate.
- Maintenance overhead: versioning must be simple and truthful before UCP activation.
- Deployment viability: UCP/Marketplace must not rely on the M365 source repo or developer virtual environment.

## Why This Choice

The correct move is a new `0.1.2` governed patch release. The live smoke test proved the important product claim - delegated Microsoft sign-in plus read-only Graph execution can work from the installed payload - but it also proved formal readiness is still false. A version bump alone would preserve the same defect. A `0.1.2` fix must repair the package mechanics and evidence chain at the same time.

## Current Truth

- The installed `com.smarthaus.m365@1.1.1` artifact exists at `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/1.1.1/`.
- `SHA256SUMS` passed for the installed `1.1.1` artifact.
- The runtime can complete real Microsoft `device_code` sign-in through the SmartHaus tenant app registration.
- A live read-only `graph.me` call succeeded from the installed payload runtime.
- The corrected installed-payload smoke returned `readiness_state=not_ready`, `readiness_label=art`, `art=false`.
- The `art=false` cause is an artifact/readiness layout mismatch: the runtime expects `manifest.json` at the payload root, while the manifest currently lives only in the outer UCP envelope.
- Plain system Python import/acceptance still fails when dependencies such as `jwt` are absent; the dependency contract is implicit.
- The acceptance harness still needs a real local socket path through `ucp_m365_pack.client.execute_m365_action()` without patching `_http_runtime_invoke`.
- The installed `1.1.1` provenance points at a commit that does not by itself reproduce the dirty worktree implementation.
- The parent plan/fix plan/tracker set contains conflicting readiness language.

## Target Truth

- Pack identity: `com.smarthaus.m365`.
- Pack version: `0.1.2`.
- Runtime version: `0.1.2`.
- Local artifact store path: `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/`.
- Bundle name: `com.smarthaus.m365-0.1.2.ucp.tar.gz`.
- Previous `1.1.0` and `1.1.1` artifacts remain historical evidence only and are not final release authorities.
- UCP live marketplace activation remains out of M365-repo scope until a sibling UCP plan executes.

## Governing Formula

For version `v`, formal pack readiness is:

```text
PackReady(v) =
  VersionCorrect(v)
  and ArtifactSelfDescribing(v)
  and DependencyClosed(v)
  and SourceIndependent(v)
  and RuntimeLaunches(v)
  and AuthLifecycleWorks(v)
  and ReadinessReady(v)
  and ClientSocketAcceptance(v)
  and LiveReadOnlyGraph(v)
  and ProvenanceReproducible(v)
  and EvidenceSynchronized(v)
```

For this plan, `v = 0.1.2`. Any false clause means the release is `NO_GO`.

## Required Guarantees

- No username/password auth.
- No token, refresh-token, auth-code, client-secret, certificate private-key, or assertion logging.
- No source repo, sibling repo, `M365_REPO_ROOT`, or developer venv dependency.
- No readiness success unless every readiness vector clause is true.
- No UCP acceptance claim unless the client path uses a real HTTP socket.
- No final artifact claim unless provenance is reproducible from a clean source state or explicitly records a dirty-tree digest. Preferred path: clean committed source before build.

## Parent And Child Phases

### P0 - Baseline Truth And Version Correction

- **P0A:** Record `1.1.0` and `1.1.1` as historical prerelease snapshots.
- **P0B:** Set target artifact line to `0.1.2` in plan, build script, manifest, runtime version, docs, local store path, and tests.
- **P0C:** Freeze current live proof: Microsoft device-code auth plus `graph.me` success.
- **P0D:** Freeze current blockers: `art=false`, implicit dependencies, patched client acceptance, stale provenance, tracker conflict.
- **P0E:** Update parent/fix plan language so no document claims `1.1.1` is formally ready.
- **Gate:** All trackers agree that `0.1.2` is the next corrective artifact and `1.1.1` is not formal ready.

### P1 - MA Formula, Calculus, Lemmas, And Invariants

- **P1A:** Define the formal domain: UCP envelope, payload root, runtime module, dependency environment, auth state, Graph state, provenance state.
- **P1B:** Define the readiness predicate and failure lattice.
- **P1C:** Define dependency closure: declared dependencies, lock/hash policy, install/hydration boundary, missing-dependency fail-closed behavior.
- **P1D:** Define source-independence: no repo-root env names, parent walk, sibling lookup, or source-tree fallback.
- **P1E:** Define socket acceptance: UCP-facing client uses real `httpx` against local runtime URL.
- **Gate:** Notebook-backed invariants exist for version, artifact layout, dependencies, source independence, socket acceptance, readiness, and provenance.

### P2 - Artifact Layout And Readiness Repair

- **P2A:** Stage runtime-readable `manifest.json` at payload root or update readiness to deterministically resolve the outer envelope manifest without source assumptions.
- **P2B:** Stage runtime-readable `conformance.json` and `provenance.json` where health/verifier expects them.
- **P2C:** Update `probe_artifact()` and tests so required files match the actual installed runtime layout.
- **P2D:** Add a regression that extracts the outer bundle, extracts `payload.tar.gz`, launches from payload root, and requires `art=true`.
- **Gate:** Installed payload readiness no longer fails `art`.

### P3 - Dependency Contract Repair

- **P3A:** Inventory actual runtime imports and classify required dependencies.
- **P3B:** Add a pack dependency manifest, lock, or wheelhouse strategy that UCP/Marketplace can enforce.
- **P3C:** Add a deterministic startup dependency probe that reports missing modules as `dependency_missing` with exact module names.
- **P3D:** Remove module-import-time dependency hazards where possible, especially optional app-only certificate/JWT paths.
- **P3E:** Add acceptance for clean extraction without the M365 source repo or repo `.venv`.
- **Gate:** The pack either runs from its declared pack-local dependency environment or fails closed with an explicit dependency contract error. It never accidentally passes because the repo `.venv` is nearby.

### P4 - Real Local Socket Acceptance

- **P4A:** Replace patched `TestClient` release acceptance with a real loopback socket runtime launch.
- **P4B:** Set `M365_RUNTIME_URL` and call `ucp_m365_pack.client.execute_m365_action()` without patching `_http_runtime_invoke`.
- **P4C:** Prove legacy alias mapping over real HTTP for at least `users.read -> graph.users.list` and `directory.org -> graph.org_profile`.
- **P4D:** Preserve mocked unit tests separately, labeled as unit tests only.
- **Gate:** Release acceptance proves the UCP-facing client uses real HTTP to the local installed runtime.

### P5 - Provenance And Reproducible Build

- **P5A:** Require clean source state before final `0.1.2` build, or explicitly record dirty-tree digest and changed-file manifest.
- **P5B:** Prefer clean committed source as the only `GO` path.
- **P5C:** Keep deterministic gzip/tar metadata and prove two consecutive builds produce identical bundle SHA.
- **P5D:** Record source commit, tree state, build command, dependency lock hash, payload hash, bundle hash, manifest hash, and conformance hash.
- **Gate:** A clean checkout of the recorded source can reproduce the `0.1.2` artifact.

### P6 - Build, Install, And Evidence Sync

- **P6A:** Build `com.smarthaus.m365-0.1.2.ucp.tar.gz`.
- **P6B:** Copy to `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/`.
- **P6C:** Regenerate `SHA256SUMS`, `manifest.json`, `conformance.json`, `provenance.json`, README, diagnostics, and verification JSON.
- **P6D:** Update parent plan YAML/JSON/MD, fix-plan status, handoff packet, release packet, operations runbook, execution plan, action log, and project file index.
- **Gate:** Every reference to the active artifact points to `0.1.2` and every stale `1.1.x` claim is marked historical or superseded.

### P7 - Live Read-Only Proof And Release Decision

- **P7A:** Re-run installed-payload live `device_code` auth through the SmartHaus tenant app.
- **P7B:** Re-run live read-only `graph.me`.
- **P7C:** Confirm readiness is `ready/success` after auth, or record the exact failing vector with `NO_GO`.
- **P7D:** Confirm no secrets/tokens/auth codes are logged.
- **P7E:** Publish release decision.
- **Gate:** `PackReady(0.1.2) = true` for M365-side readiness, or the release stays `NO_GO`.

## Atomic Execution Chunks

Claude must execute this plan one chunk at a time. A chunk may update only the listed purpose/surface, must run its local proof, and must stop if the gate is not green. Do not batch multiple chunks into one unreviewable change.

### C0 - Preflight And Worktree Truth

- **Purpose:** Establish current state before edits.
- **Allowed work:** Read-only inspection plus required MCP validation.
- **Tasks:**
  - C0.1 Read `AGENTS.md`, `.cursor/rules/*.mdc`, North Star, execution plan, action log, file index, and this plan.
  - C0.2 Run `git status --short` and record dirty/untracked surfaces without reverting user work.
  - C0.3 Inspect current version declarations in runtime, manifest builder, docs, and install artifacts.
  - C0.4 Inspect current readiness failure evidence for `art=false`.
- **Gate:** Produce a short baseline note. No code/package edits yet.

### C1 - Version Authority Only

- **Purpose:** Make `0.1.2` the only active target.
- **Allowed work:** Version constants, build metadata sources, plan/doc authority text.
- **Tasks:**
  - C1.1 Change active pack version source to `0.1.2`.
  - C1.2 Change active runtime version source to `0.1.2`.
  - C1.3 Change bundle/install path sources to `0.1.2`.
  - C1.4 Mark `1.1.0` and `1.1.1` references historical unless they are old evidence.
- **Gate:** grep shows no active `1.1.x` release claim. Runtime and manifest version tests are still allowed to fail only if they point to the next planned chunk.

### C2 - Notebook / Invariant Admission

- **Purpose:** Satisfy MA and MCP before runtime extraction.
- **Allowed work:** notebooks, lemma docs, invariant YAML, scorecards, generated verification, plan tracker updates.
- **Tasks:**
  - C2.1 Add version-correction invariant.
  - C2.2 Add artifact-layout/readiness invariant.
  - C2.3 Add dependency-contract invariant.
  - C2.4 Add real-socket-acceptance invariant.
  - C2.5 Add provenance-reproducibility invariant.
  - C2.6 Run MCP validation for the intended code/package write set.
- **Gate:** scorecard green and MCP admits next chunk. If MCP denies, create the exact scope-correction package it asks for.

### C3 - Payload Metadata Layout

- **Purpose:** Fix `art=false` root cause.
- **Allowed work:** packaging script, payload staging, health artifact probe, focused packaging tests.
- **Tasks:**
  - C3.1 Decide and document the payload metadata contract.
  - C3.2 Stage runtime-readable metadata into the installed payload root or update health to resolve envelope metadata deterministically.
  - C3.3 Update `probe_artifact()` required file list to match the contract.
  - C3.4 Add a test that extracts outer bundle and inner payload and proves required artifact files exist where runtime expects them.
- **Gate:** installed-payload artifact probe returns `art=true`.

### C4 - Dependency Contract

- **Purpose:** Remove accidental repo-venv dependency.
- **Allowed work:** dependency manifest/lock, dependency probe, launcher failure reporting, import-boundary cleanup, focused tests.
- **Tasks:**
  - C4.1 Inventory imports from packaged `m365_runtime` and `ucp_m365_pack`.
  - C4.2 Add dependency contract artifact to the pack.
  - C4.3 Add startup probe for missing modules.
  - C4.4 Convert raw `ModuleNotFoundError` into structured `dependency_missing`.
  - C4.5 Avoid importing optional JWT/app-only code on delegated-client import unless declared dependency is present.
- **Gate:** clean extracted payload has deterministic dependency behavior and no unstructured missing-module crash.

### C5 - Real Socket Acceptance

- **Purpose:** Replace synthetic/patched release acceptance.
- **Allowed work:** acceptance script and tests only.
- **Tasks:**
  - C5.1 Extract outer bundle and inner payload in acceptance.
  - C5.2 Launch runtime on dynamic loopback port.
  - C5.3 Set `M365_RUNTIME_URL`.
  - C5.4 Call unpatched `ucp_m365_pack.client.execute_m365_action()`.
  - C5.5 Prove representative legacy alias mapping over real HTTP.
  - C5.6 Add a guard that fails if `_http_runtime_invoke` is monkeypatched in release acceptance.
- **Gate:** acceptance demonstrates real `httpx` to local socket.

### C6 - Mocked Readiness To Ready

- **Purpose:** Prove readiness can become green before live Microsoft.
- **Allowed work:** mocked acceptance, token-store fixture/probe, readiness tests.
- **Tasks:**
  - C6.1 Drive auth start/check through HTTP with mocked Microsoft token endpoint.
  - C6.2 Store token through configured token store.
  - C6.3 Mock Graph `/organization` success.
  - C6.4 Assert readiness vector is all true and label is `success`.
- **Gate:** installed-payload mocked acceptance returns `ready/success`.

### C7 - Deterministic Build And Install

- **Purpose:** Produce the `0.1.2` local artifact.
- **Allowed work:** build script, dist output, local IntegrationPacks copy, checksums.
- **Tasks:**
  - C7.1 Build once.
  - C7.2 Build twice.
  - C7.3 Prove bundle hashes match.
  - C7.4 Copy to `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/`.
  - C7.5 Verify `SHA256SUMS`.
- **Gate:** deterministic build and install-dir checksum pass.

### C8 - Provenance

- **Purpose:** Make artifact reproducible and honest.
- **Allowed work:** provenance generation, source-state capture, docs/tests.
- **Tasks:**
  - C8.1 Record source commit.
  - C8.2 Record clean/dirty state.
  - C8.3 Record changed-file digest list if dirty.
  - C8.4 Prefer committing/clean source before final release build.
  - C8.5 Block `GO` if provenance claims clean while tree is dirty.
- **Gate:** provenance truth matches actual source state.

### C9 - Live Read-Only Smoke

- **Purpose:** Prove real Microsoft read-only path for `0.1.2`.
- **Allowed work:** runtime launch/test command only; no tenant mutation.
- **Tasks:**
  - C9.1 Launch installed `0.1.2` payload.
  - C9.2 Start device-code auth.
  - C9.3 Wait for CTO/admin user sign-in.
  - C9.4 Confirm auth status signed in.
  - C9.5 Invoke `graph.me`.
  - C9.6 Confirm readiness.
- **Gate:** live Graph succeeds and readiness is either `ready/success` or exact false vector is recorded as `NO_GO`.

### C10 - Evidence And Tracker Sync

- **Purpose:** Close the plan truthfully.
- **Allowed work:** docs, plan YAML/JSON/MD, action log, execution plan, file index, diagnostics.
- **Tasks:**
  - C10.1 Update release packet.
  - C10.2 Update runbook.
  - C10.3 Update handoff packet.
  - C10.4 Update parent/fix/readiness plans.
  - C10.5 Update operations trackers.
  - C10.6 Run parse/checksum/diff checks.
- **Gate:** every active reference points to `0.1.2`, historical `1.1.x` is labeled, and release decision matches the evidence.

## Acceptance Criteria

- `manifest.json` reports `version=0.1.2`.
- Runtime `/v1/runtime/version` reports `runtime_version=0.1.2`.
- Final install directory is `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/`.
- Installed payload launch resolves `m365_runtime` from the payload path only.
- Installed payload readiness returns `ready/success` after auth in mocked acceptance.
- Live installed payload readiness returns `ready/success` after SmartHaus device-code auth, or the exact false vector blocks release.
- Plain dependency probe no longer fails with an unstructured `ModuleNotFoundError`; dependency behavior is declared and fail-closed.
- Release acceptance uses a real local socket and unpatched `ucp_m365_pack.client.execute_m365_action()`.
- Conformance scans the full payload and fails on forbidden source-root fallback strings.
- Two consecutive builds produce identical bundle SHA.
- Provenance is reproducible from clean source or explicitly dirty-tree recorded; final `GO` requires clean source.
- `SHA256SUMS` passes in the `0.1.2` install directory.

## Validation Commands

Commands must run only after MCP `validate_action` admits them.

```bash
PYTHONPATH=src .venv/bin/python scripts/ci/verify_standalone_graph_runtime_pack.py
PYTHONPATH=src .venv/bin/python scripts/ci/acceptance_standalone_graph_runtime_pack.py
PYTHONPATH=src:/Users/smarthaus/Projects/GitHub/UCP-codex-stable/src .venv/bin/pytest -q \
  tests/test_m365_runtime_p4_runtime_and_auth.py \
  tests/test_m365_runtime_p5_graph_actions.py \
  tests/test_m365_runtime_p5_launcher_app.py \
  tests/test_m365_runtime_p7_packaging.py \
  tests/test_m365_runtime_fix_auth_lifecycle.py \
  tests/test_ucp_m365_pack_contracts.py \
  tests/test_ucp_m365_pack_client.py
cd /Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2 && shasum -a 256 -c SHA256SUMS
```

The final implementation must add or update validation commands for the dependency contract, installed-payload readiness, real local socket acceptance, deterministic rebuild replay, and live read-only smoke proof.

## Stop Conditions

- Any attempt to treat `1.1.1` as the formal ready artifact.
- Any artifact build that emits `1.1.x` as the active pack line.
- Any readiness success that skips the installed payload path.
- Any dependency pass that relies on repo `.venv` without an explicit dependency contract.
- Any patched release acceptance that bypasses real `httpx` client execution.
- Any provenance that claims clean reproducibility while the source tree is dirty.
- Any username/password auth support.
- Any token, secret, private key, auth code, or refresh token in logs, docs, evidence, or tests.

## Governance Closure Checklist

- [x] Formal `0.1.2` fix plan created.
- [x] Prompt pair created.
- [x] Execution plan updated.
- [x] Project file index updated.
- [x] Action log updated.
- [x] CTO approves implementation start. (2026-04-27 user-initiated continuation)
- [x] MA notebooks and invariants created. (L99 bundle, scorecard green)
- [x] Runtime/package fixes implemented. (C1, C3, C4, C5, C6, C8 changes shipped)
- [x] `0.1.2` artifact built and installed. (deterministic SHA `df714fa6...f6650`, install-dir SHA256SUMS clean)
- [ ] Acceptance and live smoke prove `PackReady(0.1.2)`. (mocked acceptance + verifier + regression all green; live smoke C9 passed against installed `0.1.2`; clean-source provenance C8 remains blocked on CTO commit)

## Chunk Progress (2026-04-27)

| Chunk | Status | Notes |
| --- | --- | --- |
| C0 - Preflight & Worktree Truth | done | Baseline note recorded in chat; confirmed `art=false` root cause from required-files mismatch. |
| C2 - Notebook / Invariant Admission | done | L99 lemma bundle published; MCP admits the C1+ code edits with `has_notebook_backing=true`. (Executed before C1 to satisfy `notebook_backing` predicate.) |
| C1 - Version Authority Only | done | `RUNTIME_VERSION` 0.1.0 -> 0.1.2; build `VERSION` 1.1.1 -> 0.1.2; acceptance + p7 packaging assertions updated. Parent/fix plans already labeled 1.1.x historical. |
| C3 - Payload Metadata Layout | done | In-payload `pack_metadata.json` added; `probe_artifact()` accepts manifest.json OR pack_metadata.json plus the payload pair; install dir extracts inner payload so probe_artifact returns True at install_dir. |
| C4 - Dependency Contract | done | Lazy `jwt`/`yaml` imports; `RUNTIME_REQUIRED_MODULES` + `_probe_required_dependencies()` + `outcome=dependency_missing` with `missing_modules` list; `/v1/health/dependencies` endpoint; staged `pack_dependencies.json`. |
| C5 - Real Socket Acceptance | done | `scripts/ci/acceptance_standalone_graph_runtime_pack.py` rewritten to spawn a subprocess+uvicorn on a dynamic loopback port and call `execute_m365_action()` over real `httpx`; `_assert_unpatched_http_runtime_invoke` guard fails closed if `_http_runtime_invoke` is monkey-patched; 21/21 GO. |
| C6 - Mocked Readiness To Ready | done | `test_readiness_flips_to_ready_success_with_pack_metadata_layout` proves the full readiness vector (svc, art, src, ctr, auth, tok, perm, graph, aud) flips to `ready/success` against the new layout. |
| C7 - Deterministic Build & Install | done | Two consecutive builds produce identical bundle SHA `df714fa62420b77709c37e1bc647566f9c4ab48f653e85669a4b5684b62f6650`. Install-dir `SHA256SUMS` verifies clean. Verifier 9/9, acceptance 21/21, regression 96 passed. |
| C8 - Provenance | done | `_emit_provenance` now records `source.clean`, `source.state`, `dirty_files`, `dirty_files_digests`, `payload_sha256`, `dependency_lock_sha256`, and a `reproducibility` block whose `claims_clean_reproducible` mirrors `source.clean`. Current state: `source.clean=false` (truthful). |
| C9 - Live Read-Only Smoke | done | Installed `0.1.2` runtime completed Microsoft device-code sign-in for `phil@smarthausgroup.com`; `graph.me` returned success; readiness returned `ready/success`. Evidence: `artifacts/diagnostics/m365_standalone_graph_runtime_pack_0_1_2_live_smoke.json`. |
| C10 - Evidence & Tracker Sync | done | Action log + execution plan + project file index synchronized; release packet `docs/commercialization/m365-standalone-graph-runtime-integration-pack-0-1-2-release-packet.md` published with `release_decision=NO_GO` pending clean-source rebuild. |

**Current M365-side release decision (2026-04-27 08:14 EDT):** `NO_GO`. One blocker remains:

1. C8 source cleanliness must reach `provenance.source.clean=true` via a clean-source rebuild from a committed worktree.
