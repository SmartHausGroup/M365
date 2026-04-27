# Execution Prompt - M365 Standalone Graph Runtime Pack 0.1.2 Readiness Fix

Plan Reference: `plan:m365-standalone-graph-runtime-pack-0-1-2-readiness-fix`
Parent Plan: `plan:m365-standalone-graph-runtime-integration-pack`
Repo: `/Users/smarthaus/Projects/GitHub/M365`
Primary Fix Plan: `plans/m365-standalone-graph-runtime-pack-0-1-2-readiness-fix/m365-standalone-graph-runtime-pack-0-1-2-readiness-fix.md`

## Repository And Branch Guardrails

This is a multi-repo workspace. You must work in the M365 repository only unless the plan explicitly names another path.

Required starting commands:

```bash
cd /Users/smarthaus/Projects/GitHub/M365
pwd
git rev-parse --show-toplevel
git branch --show-current
git remote -v
```

Required expected values:

- `pwd` must be `/Users/smarthaus/Projects/GitHub/M365`.
- `git rev-parse --show-toplevel` must be `/Users/smarthaus/Projects/GitHub/M365`.
- `git branch --show-current` must be `development` unless the CTO explicitly tells you to use another branch.
- `origin` must be `https://github.com/SmartHausGroup/M365.git`.

Fail closed if any value differs. Do not continue in the wrong repo, wrong branch, or wrong remote.

Allowed paths in this plan:

- Primary repo: `/Users/smarthaus/Projects/GitHub/M365/**`
- Local artifact store output only: `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/**`

Forbidden unless a separate explicit plan is opened:

- `/Users/smarthaus/Projects/GitHub/UCP/**`
- `/Users/smarthaus/Projects/GitHub/UCP-codex-stable/**` except as read-only test dependency path when the command already uses it
- Other sibling repos under `/Users/smarthaus/Projects/GitHub/**`
- `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/1.1.0/**` and `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/1.1.1/**` except read-only comparison

If you need UCP work, stop and create or request the sibling UCP plan. Do not mutate UCP from this M365 plan.

## Mission

Correct the M365 standalone Graph runtime Integration Pack to the proper `0.1.2` version line and repair the formal pack-readiness defects exposed after the `1.1.1` fix pack.

The existing `1.1.1` artifact has real value: it can complete Microsoft device-code auth and execute a live read-only `graph.me` call. It is still **not formally ready** because installed-payload readiness fails `art=false`, the dependency contract is implicit, acceptance still needs an unpatched real-socket UCP-client path, and provenance does not cleanly reproduce from the recorded commit.

Continue until the plan is complete unless a true hard blocker is reached. If UCP/MCP/governance returns an error, do not stop by default. Treat the error as the next required work item: create the missing notebook, invariant, plan, scope correction, evidence, or metadata exactly as UCP says, rerun the gate, and continue.

## Claude Execution Contract

You are executing a governed SmartHaus M365 repository plan. Do not improvise around defects. Do not treat a workaround as success. Do not mark any phase complete unless its gate is mechanically proven.

Fail closed if anything is unclear:

- If a requirement is ambiguous, stop and ask the CTO a specific question before editing code.
- If a validation result is mixed, record the exact failing clause and keep the phase open.
- If a test only passes because it uses the source repo, repo `.venv`, patched HTTP function, mocked token, or direct internal function path where the phase requires installed-artifact behavior, that test is insufficient.
- If UCP/MCP rejects an action with a rules/governance/process error, do not abandon the plan. Fix the missing plan reference, notebook evidence, invariant, scope correction, metadata shape, or approval state that UCP identifies, then retry.
- If UCP/MCP rejects an action because it requires human approval that cannot be satisfied by repo evidence, write a blocker report and stop.

Do not claim `GO` unless every active gate for `PackReady(0.1.2)` is green. A partial pass is `NO_GO`.

## Chunk Discipline

Use the "Atomic Execution Chunks" section in the plan as your execution checklist. Work one chunk at a time: `C0`, then `C1`, then `C2`, continuing through `C10`.

For every chunk:

1. State the chunk ID you are starting.
2. Run MCP `validate_action` before any command/edit/test that requires it.
3. Touch only files needed for that chunk.
4. Run the chunk gate.
5. If the gate fails, stop that chunk, record the exact failing clause, fix the root cause if it is within the chunk, then rerun.
6. Do not move to the next chunk until the current gate is green or explicitly marked blocked.

If you are tempted to combine chunks, do not. Small chunks are required so review can isolate defects.

## Starting State You Must Preserve

- Repo: `/Users/smarthaus/Projects/GitHub/M365`.
- Local artifact store root: `/Users/smarthaus/Projects/GitHub/IntegrationPacks/`.
- Historical pack snapshots:
  - `1.1.0`: historical prerelease / over-claimed.
  - `1.1.1`: historical prerelease; real Microsoft auth + `graph.me` smoke passed, but formal readiness failed.
- Current active target:
  - pack id: `com.smarthaus.m365`
  - pack version: `0.1.2`
  - runtime version: `0.1.2`
  - install dir: `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/`
  - bundle: `com.smarthaus.m365-0.1.2.ucp.tar.gz`
- Existing live proof to preserve truthfully:
  - SmartHaus `device_code` delegated sign-in succeeded.
  - live Microsoft Graph `graph.me` succeeded.
  - installed-payload readiness failed with `art=false`.
- Known defects to fix, not hide:
  - artifact/readiness layout mismatch
  - implicit dependency contract
  - release acceptance patched `_http_runtime_invoke`
  - provenance not reproducible from the recorded clean commit
  - parent/fix tracker truth conflicts

## Exact Phase Order

Execute these phases in order. Do not skip ahead.

### R1 - Baseline Truth And Version Correction

Goal: make every active authority agree that `0.1.2` is the corrective target and `1.1.x` is historical.

Required actions:

- Update version constants and generated metadata sources to `0.1.2`.
- Update build output naming to `com.smarthaus.m365-0.1.2.ucp.tar.gz`.
- Update install target to `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/`.
- Update runtime version response to `0.1.2`.
- Ensure parent/fix/readiness plans do not claim `1.1.1` is formal ready.

Gate:

- grep/review proves no active-release claim points to `1.1.x`.
- historical references to `1.1.x` remain only as explicitly labeled evidence.

### R2 - MA Evidence And Invariants

Goal: satisfy AGENTS.md and repo governance before runtime/package extraction.

Required actions:

- Create or update notebook-backed evidence for:
  - version correctness
  - installed-payload artifact layout
  - dependency closure
  - source independence
  - real local socket client acceptance
  - readiness predicate
  - provenance reproducibility
- Create or update lemma/invariant artifacts if MCP demands them.
- Generate deterministic scorecard/verification JSON.

Gate:

- MCP admits the runtime/package file edits.
- Scorecard is green.

### R3 - Artifact Layout And Readiness Repair

Goal: extracted installed payload is self-describing and readiness no longer fails `art=false`.

Required actions:

- Decide one clean layout contract:
  - preferred: include runtime-readable `manifest.json`, `conformance.json`, and `provenance.json` in payload root; or
  - explicitly teach readiness to resolve the outer envelope manifest without source/sibling assumptions.
- Update `src/m365_runtime/health.py` and packaging script/tests to match that contract.
- Add tests that extract the outer `.ucp.tar.gz`, extract inner `payload.tar.gz`, launch from the payload root, and require `art=true`.

Gate:

- installed-payload readiness vector has `art=true`.
- no source repo path or sibling repo path is needed.

### R4 - Dependency Contract Repair

Goal: pack dependency behavior is explicit and deterministic.

Required actions:

- Inventory runtime/client imports from the installed payload.
- Add a dependency manifest/lock/contract that UCP Marketplace can consume.
- Add a startup dependency probe that returns structured `dependency_missing` with missing module names.
- Remove avoidable import-time failures. In particular, optional app-only certificate/JWT paths must not break delegated `device_code` import unless JWT is part of the declared runtime dependency contract.
- Do not silently rely on repo `.venv`.

Gate:

- plain extracted payload behavior is one of:
  - runs in a declared pack dependency environment; or
  - fails closed with explicit `dependency_missing`, not raw `ModuleNotFoundError`.

### R5 - Real Local Socket Acceptance

Goal: release acceptance proves actual UCP-facing client HTTP behavior.

Required actions:

- Update `scripts/ci/acceptance_standalone_graph_runtime_pack.py` so release acceptance:
  - extracts outer bundle
  - extracts inner payload
  - launches `python -m m365_runtime --host 127.0.0.1 --port <dynamic>`
  - sets `M365_RUNTIME_URL`
  - calls `ucp_m365_pack.client.execute_m365_action()` without patching `_http_runtime_invoke`
  - proves at least one legacy alias over real local HTTP
- Keep TestClient/mocked transport tests as unit tests only; label them that way.

Gate:

- acceptance fails if `_http_runtime_invoke` is patched.
- acceptance passes through real `httpx` to the local socket.

### R6 - Provenance And Reproducible Build

Goal: final artifact can be reproduced from the recorded source state.

Required actions:

- Make deterministic tar/gzip behavior remain stable.
- Run two consecutive builds and prove identical bundle hash.
- Record source commit, branch, clean/dirty state, dependency-lock hash, payload hash, bundle hash, manifest hash, and conformance hash.
- Preferred final state: clean source commit before final build. If source is dirty, artifact cannot be `GO` unless provenance explicitly records dirty-file digests and the CTO accepts that weaker state.

Gate:

- final `GO` requires clean-source reproducible provenance.

### R7 - Build, Install, Evidence Sync, And Live Read-Only Proof

Goal: install and prove `0.1.2`.

Required actions:

- Build `com.smarthaus.m365-0.1.2.ucp.tar.gz`.
- Copy to `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/`.
- Regenerate `manifest.json`, `conformance.json`, `provenance.json`, `SHA256SUMS`, README, verifier output, acceptance output, and release evidence.
- Run mocked installed-artifact acceptance.
- Run real local socket UCP-client acceptance.
- Run live SmartHaus read-only smoke only after CTO/admin performs Microsoft sign-in if needed.
- Sync `Operations/EXECUTION_PLAN.md`, `Operations/PROJECT_FILE_INDEX.md`, `Operations/ACTION_LOG.md`, parent plan, fix plan, runbook, handoff, release packet.

Gate:

- `SHA256SUMS` passes in `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/`.
- readiness is `ready/success` after auth in acceptance.
- live `graph.me` succeeds or release remains `NO_GO` with exact blocker.

## Read First

- `AGENTS.md`
- `.cursor/rules/*.mdc`
- `Operations/NORTHSTAR.md`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`
- `plans/m365-standalone-graph-runtime-integration-pack/m365-standalone-graph-runtime-integration-pack.md`
- `plans/m365-standalone-graph-runtime-integration-pack-fix/m365-standalone-graph-runtime-integration-pack-fix.md`
- `plans/m365-standalone-graph-runtime-pack-0-1-2-readiness-fix/m365-standalone-graph-runtime-pack-0-1-2-readiness-fix.md`
- `scripts/ci/build_standalone_graph_runtime_pack.py`
- `scripts/ci/verify_standalone_graph_runtime_pack.py`
- `scripts/ci/acceptance_standalone_graph_runtime_pack.py`
- `src/m365_runtime/health.py`
- `src/m365_runtime/launcher.py`
- `src/m365_runtime/__init__.py`
- `src/ucp_m365_pack/client.py`

## Required Fix Order

1. Freeze the truth that `1.1.0` and `1.1.1` are historical prerelease snapshots, not the formal ready line.
2. Create the MA evidence required by the repo rules before runtime/package code extraction.
3. Set the active target to:
   - pack id: `com.smarthaus.m365`
   - pack version: `0.1.2`
   - runtime version: `0.1.2`
   - bundle: `com.smarthaus.m365-0.1.2.ucp.tar.gz`
   - install directory: `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/`
4. Repair the artifact/readiness layout so the extracted installed payload is self-describing and no longer fails `art=false`.
5. Repair the dependency contract so the pack never accidentally depends on the M365 repo `.venv`.
6. Replace patched release acceptance with real local socket acceptance through unpatched `ucp_m365_pack.client.execute_m365_action()`.
7. Repair provenance so the final `0.1.2` artifact is reproducible from clean source.
8. Build, install, verify, and live smoke `0.1.2`.
9. Synchronize parent plan, fix plan, handoff packet, release packet, operations runbook, execution plan, project file index, action log, manifest, conformance, provenance, and SHA256SUMS.

## Non-Negotiable Acceptance

- `manifest.json` reports `version=0.1.2`.
- `/v1/runtime/version` reports `runtime_version=0.1.2`.
- The local store path is `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/`.
- Extracted installed payload launches with `m365_runtime` resolving from the payload path only.
- Readiness reaches `ready/success` after auth in installed-payload acceptance.
- Plain dependency behavior is declared and deterministic; no unstructured `ModuleNotFoundError` is acceptable as a final pack result.
- Release acceptance uses a real local socket and unpatched `execute_m365_action()`.
- Full payload conformance scans for source-root fallback strings.
- Two consecutive builds produce byte-identical bundle hashes.
- Provenance is clean-source reproducible for final `GO`.
- Live read-only SmartHaus device-code auth plus `graph.me` succeeds, with no token/secret/auth-code logging.

## Do Not Do

- Do not ship or claim any active `1.1.x` version for this pack.
- Do not patch the existing `1.1.1` artifact in place.
- Do not depend on the source repo, sibling repo, or repo `.venv` for final readiness.
- Do not bypass readiness with a mocked or partial vector.
- Do not patch `_http_runtime_invoke` in release acceptance.
- Do not introduce username/password auth.
- Do not log tokens, refresh tokens, auth codes, client secrets, assertions, certificates, or private keys.
- Do not mutate UCP source from this M365 plan.

## Hard Blockers

Only stop if:

- MCP denies an action and the denial requires human approval that cannot be satisfied by plan/evidence/scope correction.
- A rule requires username/password auth or secret leakage.
- A clean-source reproducible artifact cannot be produced from the current repository state.
- Live Microsoft tenant/admin consent is needed and the CTO/admin cannot provide it.
- UCP governance contradicts this M365-side boundary and requires a CTO decision.

If blocked, produce a blocker report with exact command/action, exact response, completed evidence, and the smallest required CTO/admin action.
