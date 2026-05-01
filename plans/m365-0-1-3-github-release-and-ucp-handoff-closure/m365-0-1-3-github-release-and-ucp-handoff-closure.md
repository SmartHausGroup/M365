# M365 0.1.3 GitHub Release And UCP Handoff Closure Plan

Plan ID: `m365-0-1-3-github-release-and-ucp-handoff-closure`
Status: `Active`
Date: `2026-05-01`
Repo: `/Users/smarthaus/Projects/GitHub/M365`
Source branch: `codex/m365-auth-persistence-reconnect-remediation`
Remote: `https://github.com/SmartHausGroup/M365.git`
Execution plan reference: `plan:m365-0-1-3-github-release-and-ucp-handoff-closure:R0`
Governance evidence: `notebooks/m365/INV-M365-DP-auth-persistence-reconnect-v1.ipynb`, `configs/generated/auth_persistence_reconnect_v1_verification.json`

## Intent

Promote the already live-tested `com.smarthaus.m365@0.1.3` auth-persistence reconnect remediation from a local feature branch and local install cache into the canonical GitHub Release authority that UCP can later admit by tag, asset, checksum, and provenance.

## North Star Alignment

This release supports the M365 North Star by making Microsoft 365 runtime auth self-service, fail-closed, auditable, and distributable without sibling-repo or developer-machine assumptions. It preserves the M365-only integration boundary, does not store Microsoft passwords, and does not mutate the UCP repository.

## Scope

In scope:

- Commit the `codex/m365-auth-persistence-reconnect-remediation` branch.
- Push the feature branch.
- Merge or fast-forward the release work through `development`, `staging`, and `main`.
- Rebuild `com.smarthaus.m365@0.1.3` from a clean source tree.
- Validate the clean package, downloaded release assets, hashes, signatures, provenance, and runtime import behavior.
- Tag `com.smarthaus.m365-v0.1.3`.
- Publish a GitHub Release with the `.ucp.tar.gz`, manifest, evidence, provenance, checksums, signatures, payload, dependency metadata, pack metadata, and release notes.
- Create the M365-side UCP handoff packet for `0.1.3`.
- Synchronize governance trackers.

Out of scope:

- UCP repository mutation.
- UCP marketplace admission or installed-pack activation.
- Microsoft tenant permission changes beyond documenting that delegated reconnect requires `offline_access`.
- Apple notarization. This is a UCP integration-pack archive, not a macOS `.app`, `.pkg`, or `.dmg`.
- Rewriting or deleting the already published `0.1.2` release.

## Required Release Model

```text
feature branch
  -> commit
  -> push feature branch
  -> development
  -> staging
  -> main
  -> clean-source rebuild
  -> annotated tag com.smarthaus.m365-v0.1.3
  -> draft GitHub Release
  -> downloaded-release verification
  -> publish GitHub Release
  -> M365-side UCP handoff packet
```

The local path `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.3/` is a cache/install copy only. The GitHub Release is the canonical distribution authority.

## Requirements

- **R0 - Governed release package:** Create this plan, structured mirrors, prompt pair, tracker entries, and release collateral shell.
- **R1 - Feature branch commit:** Validate and commit all governed `0.1.3` remediation files on `codex/m365-auth-persistence-reconnect-remediation`.
- **R2 - Feature branch push:** Push the feature branch to `origin` without force.
- **R3 - Development promotion:** Integrate the feature branch into `development`, push `development`, and preserve ancestry.
- **R4 - Staging promotion:** Fast-forward `staging` from `development`, push `staging`, and rerun scoped release gates.
- **R5 - Main promotion:** Fast-forward `main` from `staging`, push `main`, and block on any divergence.
- **R6 - Clean-source rebuild:** Rebuild `0.1.3` from clean `main`; require clean-source provenance and deterministic package evidence.
- **R7 - Release tag:** Create and push annotated tag `com.smarthaus.m365-v0.1.3` on the release commit.
- **R8 - Draft release:** Create a draft GitHub Release with all required assets.
- **R9 - Downloaded release verification:** Download the draft release into a temp directory, verify checksums, extract, import runtime without `PYTHONPATH=src`, and verify provenance.
- **R10 - Publish release:** Publish the release as latest only after R9 is green.
- **R11 - UCP handoff:** Write the M365-side `0.1.3` UCP handoff packet. Do not mutate UCP.
- **R12 - Tracker closeout:** Update this plan, `Operations/EXECUTION_PLAN.md`, `Operations/ACTION_LOG.md`, and `Operations/PROJECT_FILE_INDEX.md`.

## Gates

- No force push.
- No `git reset --hard`.
- No tag rewrite. If `com.smarthaus.m365-v0.1.3` exists and points elsewhere, stop.
- No release publication from dirty source.
- No release asset whose downloaded bytes fail verification.
- No tokens, refresh tokens, device codes after completion, auth codes, client secrets, private keys, subject object IDs, or phone numbers in release assets or evidence.
- UCP validation must be called before mutating actions.

## Required Assets

- `com.smarthaus.m365-0.1.3.ucp.tar.gz`
- `SHA256SUMS`
- `manifest.json`
- `conformance.json`
- `provenance.json`
- `pack_metadata.json`
- `pack_dependencies.json`
- `payload.tar.gz`
- `manifest.sig`
- `payload.sig`
- `m365-standalone-graph-runtime-integration-pack-0-1-3-release-notes.md`

## Validation Commands

Use project venv commands:

```bash
PYTHONPATH=src .venv/bin/pytest -q tests/test_m365_runtime_fix_auth_lifecycle.py tests/test_m365_runtime_0_1_2_readiness_fix.py tests/test_m365_runtime_p5_launcher_app.py tests/test_m365_runtime_p7_packaging.py
.venv/bin/pre-commit run --all-files
PYTHONPATH=src .venv/bin/python scripts/ci/verify_standalone_graph_runtime_pack.py
PYTHONPATH=src .venv/bin/python scripts/ci/acceptance_standalone_graph_runtime_pack.py
env LC_ALL=C LANG=C shasum -a 256 -c /Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.3/SHA256SUMS
git diff --check
```

Downloaded-release verification must not rely on the M365 source checkout.

## Initial Truth

- Feature branch: `codex/m365-auth-persistence-reconnect-remediation`
- Base remote branches at plan creation: `origin/development`, `origin/staging`, and `origin/main` all at `6d909ff6ccebf945750a410a4e096968e269f45f`
- Existing published GitHub Release: `com.smarthaus.m365-v0.1.2`
- New tag target: `com.smarthaus.m365-v0.1.3`
- Local live-tested bundle SHA before clean-release rebuild: `d26278c6c47a650a8750ff0dc6b914fde418b778395661ebd5bba2f440981c4e`
- Live finding: true long-lived delegated reconnect requires `offline_access`.

## Execution Outcome

Pending.
