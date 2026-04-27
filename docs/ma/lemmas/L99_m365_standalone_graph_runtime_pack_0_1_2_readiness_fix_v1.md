# L99 - M365 Standalone Graph Runtime Pack 0.1.2 Readiness Fix Invariants v1

**Lemma id:** `L99_m365_standalone_graph_runtime_pack_0_1_2_readiness_fix_v1`
**Plan reference:** `plan:m365-standalone-graph-runtime-pack-0-1-2-readiness-fix:C2`
**Status:** Active
**Owner:** SMARTHAUS
**Module notebook:** `notebooks/m365/INV-M365-DO-standalone-graph-runtime-pack-0-1-2-readiness-fix-v1.ipynb`
**Lemma proof notebook:** `notebooks/lemma_proofs/L99_m365_standalone_graph_runtime_pack_0_1_2_readiness_fix_v1.ipynb`
**Invariant YAML:** `invariants/lemmas/L99_m365_standalone_graph_runtime_pack_0_1_2_readiness_fix_v1.yaml`
**Scorecard:** `artifacts/scorecards/scorecard_l99.json`
**Generated verification:** `configs/generated/standalone_graph_runtime_pack_0_1_2_readiness_fix_v1_verification.json`
**Predecessor:** `L98_m365_standalone_graph_runtime_pack_lemmas_v1`

## Mission

Bind every C1-C8 code/package edit in the `0.1.2` corrective pack release to a notebook-backed invariant. The previous fix-pack closed at `1.1.1` while the installed-payload smoke proved formal readiness was still false (`art=false`, implicit dependency contract, patched release acceptance, stale provenance). This lemma bundle freezes the five conjunctive invariants that the corrective `com.smarthaus.m365@0.1.2` artifact must satisfy.

## Bundled predicate

```
PackReady_0_1_2 =
    L_VERSION_CORRECT
  ∧ L_ARTIFACT_SELFDESC
  ∧ L_DEPENDENCY_CLOSED
  ∧ L_SOCKET_REAL
  ∧ L_PROVENANCE_REPRO
```

Any single false clause means `NO_GO`.

## Lemmas

### L_VERSION_CORRECT

The active marketplace pack must read version `0.1.2` from every authoritative surface: manifest, runtime constant, runtime endpoint, bundle filename, install dir. Historical `1.1.0` and `1.1.1` references appear only as labeled evidence text and never as the active release authority.

**Failure boundary:** any active release authority document, generated metadata source, runtime endpoint, or build constant reading `1.1.0` or `1.1.1`.

### L_ARTIFACT_SELFDESC

After extracting the outer `.ucp.tar.gz` and the inner `payload.tar.gz`, launching `python -m m365_runtime` from the chosen `installed_root` must make `probe_artifact()` return `True`. Required artifact files must exist at that root. The runtime must never resolve required artifacts through source repos, sibling repos, or `M365_REPO_ROOT` / `SMARTHAUS_M365_REPO_ROOT` env vars.

**Failure boundary:** `probe_artifact()` returns `False` from the chosen installed root, or the runtime falls back to source-tree paths to find required metadata.

### L_DEPENDENCY_CLOSED

The pack must declare its Python runtime dependencies in a manifest or lock readable from the installed payload, must run a deterministic startup dependency probe before binding the listener, and must surface missing modules as a structured `dependency_missing` outcome class (with the missing module name list) instead of a raw `ModuleNotFoundError`. Optional certificate/JWT branches must not block delegated `device_code` import unless declared as required.

**Failure boundary:** missing modules surface as raw `ModuleNotFoundError`, the pack quietly inherits the M365 repo `.venv` site-packages, or the optional JWT/cert branch hard-blocks delegated `device_code` import without a declared dependency.

### L_SOCKET_REAL

Release acceptance must (i) extract the outer bundle and inner payload, (ii) launch `python -m m365_runtime` as a subprocess on a dynamic loopback port, (iii) set `M365_RUNTIME_URL`, (iv) call `ucp_m365_pack.client.execute_m365_action()` over real `httpx` against the local socket without monkeypatching `_http_runtime_invoke`, (v) prove at least one legacy alias mapping over real HTTP, and (vi) fail closed if `_http_runtime_invoke` is patched.

**Failure boundary:** release acceptance uses `TestClient` / in-process transport, monkeypatches `_http_runtime_invoke`, or skips the legacy alias HTTP proof.

### L_PROVENANCE_REPRO

Two consecutive deterministic builds must produce byte-identical bundle SHA256 values. `provenance.json` must record `source_commit`, `source_branch`, `source_clean`, `dependency_lock_sha`, `payload_sha`, `bundle_sha`, `manifest_sha`, and `conformance_sha`. Final `GO` requires `source_clean == True`; a dirty worktree forces a dirty-tree digest record and remains `NO_GO` unless the CTO explicitly accepts the weaker state.

**Failure boundary:** consecutive bundle SHAs differ, a required provenance key is missing, or `provenance.json` claims clean reproducibility while the source tree is dirty.

## Test bindings

- `scripts/ci/verify_standalone_graph_runtime_pack.py` (versioned manifest + runtime + payload checks).
- `scripts/ci/acceptance_standalone_graph_runtime_pack.py` (subprocess + real httpx + execute_m365_action()).
- `tests/test_m365_runtime_0_1_2_readiness_fix.py` (artifact layout, dependency contract, real-socket guard, provenance keys - to be added in C3-C8).
- `tests/test_m365_runtime_p7_packaging.py` (runtime version constant equality).
- `cd /Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2 && shasum -a 256 -c SHA256SUMS` (run from the install directory because `SHA256SUMS` indexes files by relative name).

## Determinism

```
seed_locked: true
seed: 0
mode: deterministic-static
```

The module notebook performs no random sampling and no live network. The lemma proof notebook enumerates the 32-row truth table over the five booleans and proves the conjunction is true only when all five lemmas are true.

## Authorization

This lemma bundle authorizes the C1-C8 code/package writes for the `0.1.2` readiness fix under the MA notebook-first contract.
