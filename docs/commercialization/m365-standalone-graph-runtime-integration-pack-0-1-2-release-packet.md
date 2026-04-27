# M365 Standalone Graph Runtime Integration Pack 0.1.2 - Release Packet

**Plan reference:** `plan:m365-standalone-graph-runtime-pack-0-1-2-readiness-fix`
**Lemma backing:** `L99_m365_standalone_graph_runtime_pack_0_1_2_readiness_fix_v1`
**Pack identity:** `com.smarthaus.m365@0.1.2`
**Bundle file:** `com.smarthaus.m365-0.1.2.ucp.tar.gz`
**Install dir:** `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/`
**Build date:** 2026-04-27 (UTC, deterministic gzip mtime=0 + normalized TarInfo)
**Status:** `NO_GO` pending clean-source rebuild

## Pack Identity (artifact hashes)

```
bundle_sha256       9af6df20616d652eaf974ca61914da5e9a636b4e5d96f0fc8eccc779cea22eee
manifest_sha256     01d0ca8722880f4ce99b3686cc0511c3052f347d39f8f5e949b8978ec3683e7c
conformance_sha256  4ce8aa952dfc42bf571865c1813d5202f760503d4719a5172041a460172f84c7
payload_sha256      fb65e08ccc80240d7b871019099130a7f7ce4084b603dae219f895d55626d878
dependency_lock_sha 3a01d509acf0a62a4619fd08d958566ddf19140b34af9370a2bb6e95764b2d2a
```

Two consecutive deterministic builds produced byte-identical bundle SHA values.

## Install dir layout

The install dir is directly launchable - both the outer envelope files and the
inner payload's runtime files live at the install root. `python -m m365_runtime`
from the install dir resolves `installed_root` to the install dir and
`probe_artifact()` returns `True` because `manifest.json` (envelope) and
`pack_metadata.json` (in-payload) plus `setup_schema.json` and
`registry/agents.yaml` are all present.

```
/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/
  README.md
  SHA256SUMS                                # bundle + manifest + conformance integrity
  com.smarthaus.m365-0.1.2.ucp.tar.gz       # outer marketplace bundle
  manifest.json                              # outer envelope manifest (full content_digest)
  conformance.json                           # 17-check conformance evidence
  provenance.json                            # source/build provenance with dirty_files_digests
  m365_runtime/                              # standalone Microsoft Graph runtime service (extracted)
  ucp_m365_pack/                             # UCP-facing client + contracts (extracted)
  registry/                                  # agents.yaml + action_registry.yaml (extracted)
  pack_metadata.json                         # in-payload self-describing identity (extracted)
  pack_dependencies.json                     # declared dependency contract (extracted)
  setup_schema.json                          # declared setup schema (extracted)
```

## Conformance Checks (17 / 17 pass)

```
payload_sources_contract                  pass
manifest_schema_contract                  pass
public_classification_contract            pass
compatibility_contract                    pass
entrypoint_contract                       pass
runtime_contract                          pass
auth_lifecycle_contract                   pass
legacy_action_alias_contract              pass
payload_self_describing_contract          pass    (C3 fix - new)
dependency_contract_present               pass    (C4 fix - new)
read_only_contract                        pass
bundle_structure_contract                 pass
digest_integrity_contract                 pass
signature_contract                        pass
setup_schema_contract                     pass
private_host_boundary                     pass
public_evidence_posture                   pass
no_source_repo_dependency_contract        pass
```

## Real Local Socket Acceptance (21 / 21 GO)

`scripts/ci/acceptance_standalone_graph_runtime_pack.py` extracts the outer
bundle and inner payload, picks a free loopback port, spawns a Python
subprocess that builds the runtime app with `httpx.MockTransport` for OAuth
and Graph and runs `uvicorn.Server`, then drives the auth lifecycle and
action endpoints over real `httpx`. `_http_runtime_invoke` is NOT patched;
`_assert_unpatched_http_runtime_invoke` fails the run if patching is detected.

```
install_dir_present                                      true
integrity_sha256sums                                     true
runtime_subprocess_no_error                              true
runtime_version_locked                                   true   (0.1.2)
actions_count_locked                                     true   (11)
art_true_after_extract                                   true   (C3 fix verified)
readiness_after_is_ready                                 true
readiness_after_label_is_success                         true
auth_check_is_signed_in                                  true
status_after_is_signed_in                                true
audit_does_not_leak_access_token                         true
audit_redacts_secrets_in_params                          true
mutation_action_fenced                                   true
runtime_http_action_succeeds                             true
dependency_probe_no_missing                              true   (C4 fix verified)
http_runtime_invoke_unpatched                            true   (C5 guard verified)
ucp_client_legacy_alias_succeeds                         true
ucp_client_legacy_alias_targets_runtime_action           true   (users.read -> graph.users.list)
ucp_client_routing_path_is_http_runtime                  true
ucp_client_directory_org_alias_targets_runtime_action    true   (directory.org -> graph.org_profile)
ucp_client_directory_org_alias_fences_pkce_correctly     true   (auth_required for app-only-only action)
```

Acceptance evidence: `artifacts/diagnostics/m365_standalone_graph_runtime_pack_acceptance.json`

## Verifier (9 / 9 PASSED)

`scripts/ci/verify_standalone_graph_runtime_pack.py` extracts the bundle,
scans every payload `.py`/`.yaml`/`.json`/`.md`/`.txt` for the forbidden
token list (`M365_REPO_ROOT`, `SMARTHAUS_M365_REPO_ROOT`, `M365_REGISTRY_PATH`,
parent-walk patterns), confirms the manifest declares the auth lifecycle
paths, and confirms the packaged launcher contains the `/v1/auth/start`
and `/v1/auth/check` routes.

## Regression Suite (96 / 96 passed)

```
PYTHONPATH=src:/Users/smarthaus/Projects/GitHub/UCP-codex-stable/src .venv/bin/pytest -q \
  tests/test_m365_runtime_p4_runtime_and_auth.py \
  tests/test_m365_runtime_p5_graph_actions.py \
  tests/test_m365_runtime_p5_launcher_app.py \
  tests/test_m365_runtime_p7_packaging.py \
  tests/test_m365_runtime_fix_auth_lifecycle.py \
  tests/test_m365_runtime_0_1_2_readiness_fix.py \
  tests/test_ucp_m365_pack_contracts.py \
  tests/test_ucp_m365_pack_client.py
```

Result: `96 passed`. The new `tests/test_m365_runtime_0_1_2_readiness_fix.py`
file adds 16 tests that bind L99 invariants to executable assertions:
version, pack_metadata layout, art-after-overlay, dependency probe,
launcher dependency_missing outcome, lazy jwt import (verified statically),
acceptance script no monkey-patch + uvicorn + subprocess, monkey-patch
guard fires when patched, readiness flips to ready/success against the new
layout, and provenance never claims clean while dirty.

## Provenance (honest)

`provenance.json` records:

- `artifact.bundle_sha256`, `payload_sha256`, `manifest_sha256`,
  `conformance_sha256`, `dependency_lock_sha256`.
- `source.repository`, `source.branch`, `source.commit`, `source.clean`,
  `source.state`, `source.dirty_files`, `source.dirty_files_digests`.
- `reproducibility.claims_clean_reproducible` (mirrors `source.clean`),
  `reproducibility.release_blocker_if_dirty=true`,
  `reproducibility.two_build_byte_identical_required=true`.

Current state: `source.clean=false` because the worktree has the readiness
fix work in progress. `claims_clean_reproducible=false` is recorded
truthfully. Final `GO` requires CTO commit + clean-source rebuild.

## Live Read-Only Smoke

The installed `0.1.2` runtime completed live Microsoft device-code auth for
`phil@smarthausgroup.com` on 2026-04-27. The smoke invoked `graph.me`
successfully and readiness returned `ready/success` with every readiness vector
bit true: `svc`, `auth`, `tok`, `graph`, `perm`, `ctr`, `art`, `src`, and
`aud`.

Evidence: `artifacts/diagnostics/m365_standalone_graph_runtime_pack_0_1_2_live_smoke.json`

No access token, refresh token, auth code, client secret, private key, subject
object ID, or phone number is recorded in the evidence packet.

## Release Decision: NO_GO

The M365-side `release_decision` for `com.smarthaus.m365@0.1.2` is `NO_GO`
until clean-source provenance is rebuilt.

### Remaining Blocker - C8 Source Cleanliness

`provenance.source.clean=false`. Final `GO` requires the worktree to be
committed and the deterministic build to be re-run from the clean commit so
`provenance.source.clean=true` and `claims_clean_reproducible=true`.

## Path to GO

1. CTO commits the readiness-fix worktree.
2. Re-run `.venv/bin/python scripts/ci/build_standalone_graph_runtime_pack.py`
   from the clean commit (deterministic, identical bundle SHA expected).
3. Re-run `.venv/bin/python scripts/ci/verify_standalone_graph_runtime_pack.py`.
4. Re-run `.venv/bin/python scripts/ci/acceptance_standalone_graph_runtime_pack.py`
   against the freshly-rebuilt install dir.
5. Verify `cd /Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2 && shasum -a 256 -c SHA256SUMS` (the `SHA256SUMS` index lists files by relative path, so the command must run from the install directory).
6. Update this packet's `Release Decision` section to `GO` with
   `provenance.source.clean=true`.

## Boundary

Live UCP through-the-installed-pack acceptance is intentionally out of
scope for this M365-side plan and remains the responsibility of the
sibling UCP plan `plan:ucp-m365-standalone-graph-runtime-pack-activation`.
M365 does not mutate UCP source under this plan.

## No-Secret Posture

No tokens, refresh tokens, authorization codes, client secrets, certificate
private keys, or assertions appear in any of the build output, evidence
files, plan files, action log entries, or test artifacts produced by this
plan. The acceptance harness uses synthetic tokens (`ACCEPT_AT`,
`ACCEPT_RT`) that exist only inside `httpx.MockTransport` handlers.
