# M365 GitHub Release And UCP Handoff Closure Plan

Plan ID: `m365-github-release-and-ucp-handoff-closure`
Status: `Complete-Released` (closed 2026-04-27)
Date: `2026-04-27`
Repo: `/Users/smarthaus/Projects/GitHub/M365`
Required branch at start: `development`
Remote: `https://github.com/SmartHausGroup/M365.git`
Execution plan reference: `plan:m365-github-release-and-ucp-handoff-closure:R0`

## Closure Outcome

| Field | Value |
| --- | --- |
| GitHub Release URL | https://github.com/SmartHausGroup/M365/releases/tag/com.smarthaus.m365-v0.1.2 |
| Release tag | `com.smarthaus.m365-v0.1.2` |
| Release target commit | `687b69b65d8904457a1c72046e66c8e5f868f635` (`main`) |
| Release name | SMARTHAUS M365 Integration Pack 0.1.2 |
| Draft / Prerelease / Latest | false / false / true |
| Asset count | 11 |
| Bundle SHA256 | `29c1d05bc30f570373d09a2ebb38313bda8466d4faa31e70a2e865e1c046fd9e` |
| Manifest SHA256 | `bfc52d4b4e585604cac426d546153e5a7d54180630cadbf9a2b7f7c62a8584e9` |
| Conformance SHA256 | `ab03f4277ecf700e4b032da843b8d45760358c3dd13a6b42c94033a154af3da7` |
| Payload SHA256 | `c09625a5b89b1578e2226463d43670dc8355db7d489338f3bf42001db16cabfd` |
| Pack-metadata SHA256 | `7ff9c21b465916c7d28fd0e470e465e84b69351413e625b9df339f69a8a577fd` |
| Pack-dependencies SHA256 | `376f10bab9f3554e5bce73ef55ea157bb8fe866e3d498ea50c6895b87e8f0e0b` |
| Downloaded-release verification | passed (LC_ALL=C SHA256SUMS OK; runtime imports without `PYTHONPATH=src`) |
| UCP handoff packet | [docs/commercialization/m365-standalone-graph-runtime-integration-pack-0-1-2-ucp-handoff-packet.md](../../docs/commercialization/m365-standalone-graph-runtime-integration-pack-0-1-2-ucp-handoff-packet.md) |
| Release notes asset | [docs/commercialization/m365-standalone-graph-runtime-integration-pack-0-1-2-release-notes.md](../../docs/commercialization/m365-standalone-graph-runtime-integration-pack-0-1-2-release-notes.md) |
| Local cache role | `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/` is now cache/install only |
| Next step (out of scope here) | sibling UCP plan to admit the GitHub Release asset |

## Chunk Status

| Chunk | Status | Outcome |
| --- | --- | --- |
| C0 - Preflight | done | branch `development` @ `257693a3`, ahead 5 of origin; staging/main both at `e871e19`; tag absent; gh auth OK |
| C1 - Review-truth gate | done | parent integration plan moved to `Closed-via-corrective-plan`; runbook points active artifact at 0.1.2; remaining grep hits are explicitly historical/labeled |
| C2 - Development verification | done | verifier 9/9, real-socket acceptance 21/21 GO, focused pytest 84 passed, install-dir SHA256SUMS OK, `git diff --check` clean |
| C3 - Commit + push development | done | commit `687b69b6 Prepare M365 0.1.2 release closure`, fast-forward `e871e19..687b69b6` |
| C4 - dev -> staging | done | fast-forward `e871e19..687b69b6`, ancestry verified |
| C5 - Staging verification | done | verifier 9/9, real-socket acceptance 21/21 GO, readiness-fix tests 20 passed, install-dir SHA256SUMS OK |
| C6 - staging -> main | done | fast-forward `e871e19..687b69b6`, ancestry verified |
| C7 - Clean-main rebuild + asset freeze | done | two-build-stable bundle SHA `29c1d05b...46fd9e`, install-dir SHA256SUMS OK, verifier 9/9; `git status --short` clean post-build |
| C8 - Release tag | done | annotated tag `com.smarthaus.m365-v0.1.2` created on main commit `687b69b6` and pushed |
| C9 - Draft release | done | `gh release create --draft --target main` with 11 assets including release notes |
| C10 - Downloaded-release verification | done | `gh release download` to `mktemp -d`, LC_ALL=C SHA256SUMS OK, bundle+payload extracted, `m365_runtime` imports from temp dir without source-repo path, manifest version 0.1.2, provenance commit matches the release tag commit `687b69b65d8904457a1c72046e66c8e5f868f635` |
| C11 - Publish | done | `gh release edit --draft=false --latest`; release is published, marked latest |
| C12 - UCP handoff packet | done | M365-side handoff packet written; no UCP repo file mutated; references the published release URL and exact final hashes |
| C13 - Tracker closeout | done | this entry; trackers synchronized; `git diff --check` clean; JSON/YAML parse OK |

## Intent Definition

We are closing the gap between "the M365 pack works locally" and "the M365 pack is a proper release artifact that UCP can admit without repo hacks."

The current M365-side `0.1.2` pack has local proof:

- Local repo branch: `development`
- Local source head at plan creation: `257693a33fddcc83dd2ff63ccffc328c010683a8`
- Local branch state at plan creation: `development` is ahead of `origin/development` by 5 commits
- Current remote `origin/development`, `origin/staging`, and `origin/main` were still behind this work at the time this plan was created
- GitHub release list was empty at plan creation
- Local install/cache directory: `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/`
- Local bundle: `com.smarthaus.m365-0.1.2.ucp.tar.gz`
- Current local bundle SHA256 at plan creation: `29c1d05bc30f570373d09a2ebb38313bda8466d4faa31e70a2e865e1c046fd9e`
- Current local manifest SHA256 at plan creation: `bfc52d4b4e585604cac426d546153e5a7d54180630cadbf9a2b7f7c62a8584e9`
- Current local payload SHA256 at plan creation: `c09625a5b89b1578e2226463d43670dc8355db7d489338f3bf42001db16cabfd`
- Current local conformance SHA256 at plan creation: `ab03f4277ecf700e4b032da843b8d45760358c3dd13a6b42c94033a154af3da7`
- Current local dependency-lock SHA256 at plan creation: `376f10bab9f3554e5bce73ef55ea157bb8fe866e3d498ea50c6895b87e8f0e0b`

That is not enough for distribution. A real Integration Pack release must be reproducible from the release branch, tagged, published as a GitHub Release, downloaded as release assets, checksum verified, extracted without source-repo assumptions, and handed to UCP as a release artifact.

## Decision Summary

The canonical distribution authority for `com.smarthaus.m365@0.1.2` is a GitHub Release created from `main`, with immutable tag, release assets, checksums, provenance, and release notes.

`/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/` is a local install/cache/store copy. It is not the canonical release authority.

UCP should later admit the GitHub Release asset by tag, asset name, checksum, and provenance. UCP must not reach into the M365 source repo, a sibling repo, or a hand-copied local artifact path as the authoritative release source.

## Options Considered

Option A: Keep using the local IntegrationPacks directory as the artifact source.

- Pro: fastest local testing path.
- Con: not a true release; not reproducible by a user; lets UCP depend on local machine state.
- Decision: rejected as canonical source. Allowed only as local cache/install output.

Option B: Commit generated bundle files to `development` only and tell UCP to scan the repo.

- Pro: source repo contains the bytes.
- Con: still couples UCP to source layout and branch state; does not create a user-facing release.
- Decision: rejected for distribution.

Option C: Promote verified source to `staging`, then `main`; tag `main`; create a GitHub Release with verified assets; hand UCP the release contract.

- Pro: normal user distribution path; reproducible; branch/tag/release provenance is clear; UCP can admit by release asset.
- Con: requires branch hygiene, release asset validation, and no-force promotion discipline.
- Decision: accepted.

## Evaluation Criteria

- Mathematical soundness: release identity is a tuple of `(repo, branch, commit, tag, asset, digest, provenance)` and must resolve to exactly one artifact.
- Deterministic guarantees: repeated clean builds from the release source must either reproduce identical release bytes or fail closed with documented hash drift.
- Invariant enforceability: checksums, release asset download, extraction, import, readiness, and UCP-client socket acceptance are machine-verifiable.
- Maintenance overhead: GitHub Release plus local cache is simpler than source-repo scanning or local path special cases.
- Deployment viability: users and UCP can download a release asset without cloning or knowing repo internals.

## Governing Formula

Let:

- `S` be the M365 source repository.
- `B_dev`, `B_stg`, and `B_main` be the development, staging, and main branches.
- `C` be the final release commit.
- `T` be the release tag `com.smarthaus.m365-v0.1.2`.
- `A` be the release asset `com.smarthaus.m365-0.1.2.ucp.tar.gz`.
- `D` be the SHA256 digest set in `SHA256SUMS`.
- `P` be the provenance record.
- `U` be the UCP handoff contract.

The release is closed only if:

```text
ReleaseReady(0.1.2) =
  SourceClean(S, C)
  and BranchPromoted(B_dev -> B_stg -> B_main, C)
  and TagPointsTo(T, C)
  and GitHubReleaseOwns(T, A, D, P)
  and DownloadVerifies(A, D)
  and ExtractsWithoutSourceRepo(A)
  and RuntimeAcceptancePasses(A)
  and LocalStoreIsCacheOfRelease(A)
  and UcpHandoffReferencesRelease(U, T, A, D, P)
  and EvidenceSynchronized(S, T, A, D, P)
```

Failure of any clause is a formal `NO_GO`.

## Hard Boundaries

Claude must obey these boundaries:

- Work in `/Users/smarthaus/Projects/GitHub/M365` only.
- Do not mutate `/Users/smarthaus/Projects/GitHub/UCP` or any UCP sibling repo.
- Do not force-push.
- Do not use `git reset --hard`.
- Do not rewrite tags. If the release tag already exists and points to a different commit, stop.
- Do not publish a GitHub Release from a dirty worktree.
- Do not publish release assets whose downloaded bytes fail `SHA256SUMS`.
- Do not log Microsoft tokens, device codes, auth codes, refresh tokens, client secrets, private keys, subject object IDs, or phone numbers.
- Do not claim UCP admission is complete. This plan only produces the M365 release and a UCP handoff package.

## Required Release Model

The final release model is:

```text
M365 source repo
  -> development branch verified and pushed
  -> staging branch fast-forwarded from development and pushed
  -> main branch fast-forwarded from staging and pushed
  -> annotated tag com.smarthaus.m365-v0.1.2 on main
  -> GitHub Release assets
  -> downloaded-release verification
  -> local IntegrationPacks cache synchronized from release asset
  -> UCP release-admission handoff
```

The local store remains useful, but only as a cache:

```text
/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/
```

It must not be described as the release source of truth after this plan is complete.

## Atomic Execution Chunks

Claude must execute the chunks in order. Each chunk has a gate. Do not move to the next chunk until the gate is green or a hard blocker is recorded.

### C0 - Preflight And Repository Truth

Purpose: prove Claude is in the correct repo and understands the current release state.

Commands to run after MCP validation where required:

```bash
cd /Users/smarthaus/Projects/GitHub/M365
pwd
git rev-parse --show-toplevel
git branch --show-current
git remote -v
git status -sb
git rev-parse HEAD
git fetch --all --tags --prune
git status -sb
git log --oneline --decorate -10
gh auth status
gh release list --limit 20
git tag --list
```

Expected starting truth:

- top-level path is `/Users/smarthaus/Projects/GitHub/M365`
- branch is `development`
- origin is `https://github.com/SmartHausGroup/M365.git`
- release tag `com.smarthaus.m365-v0.1.2` does not already point to a different commit

Gate:

- Claude records the exact local branch, remote heads, local HEAD, dirty/clean status, GitHub auth state, release list, and tag list.
- If remote branches have advanced or diverged, stop and ask for CTO direction.

### C1 - Close Review-Truth Conflicts Before Promotion

Purpose: ensure active governance docs no longer conflict with the real `0.1.2` release state.

Findings to verify and fix if still present:

- `src/m365_runtime/launcher.py` must not fail raw import before the dependency probe can return `dependency_missing`.
- `plans/m365-standalone-graph-runtime-pack-0-1-2-readiness-fix/*.yaml` and `.json` must have coherent phase/chunk status.
- release packet checksum instructions must be directory-safe.
- plan hashes must match the installed `0.1.2` artifact.
- `Operations/ACTION_LOG.md` must not leave a false "no rebuild" claim as active truth.
- `Operations/EXECUTION_PLAN.md` must mark `1.1.1` as historical/superseded by `0.1.2`.
- action-log attribution must not say Codex rebuilt/staged artifacts unless that actually happened.

Gate:

```bash
rg -n "active artifact.*1\\.1\\.1|no rebuild was performed|pre-F1 launcher|shasum -a 256 -c /Users/.*/SHA256SUMS|P0: active|source\\.clean=false|Fix-Required" Operations plans docs src
```

The command may still find historical references, but every hit must be explicitly historical, superseded, or non-active. Any active contradiction blocks promotion.

### C2 - Development Branch Release Verification

Purpose: prove the current `development` branch is internally ready before pushing or promoting.

Required gates:

```bash
PYTHONPATH=src .venv/bin/python scripts/ci/verify_standalone_graph_runtime_pack.py
PYTHONPATH=src .venv/bin/python scripts/ci/acceptance_standalone_graph_runtime_pack.py
PYTHONPATH=src .venv/bin/python -m pytest tests/test_m365_runtime_0_1_2_readiness_fix.py tests/test_m365_runtime_p4_runtime_and_auth.py tests/test_m365_runtime_p5_graph_actions.py tests/test_m365_runtime_p5_launcher_app.py tests/test_m365_runtime_p7_packaging.py tests/test_ucp_m365_pack_client.py
cd /Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2 && env LC_ALL=C LANG=C shasum -a 256 -c SHA256SUMS
cd /Users/smarthaus/Projects/GitHub/M365 && git diff --check
```

Gate:

- verifier passes
- real-socket acceptance passes
- focused regression passes
- install-dir `SHA256SUMS` passes
- `git diff --check` passes

### C3 - Commit And Push Development

Purpose: make the verified `development` source and evidence available on GitHub.

Rules:

- Inspect `git status --short` and `git diff --stat`.
- Stage only files that belong to the M365 `0.1.2` release closure.
- Do not stage unrelated user work.
- If untracked or modified files are unrelated and cannot be separated safely, stop.
- Commit with a message that names the release closure.
- Push `development` to origin.

Suggested commit message if new files are present:

```text
Prepare M365 0.1.2 release closure
```

Gate:

```bash
git status -sb
git rev-parse HEAD
git rev-parse origin/development
```

`origin/development` must equal the verified local `development` commit.

### C4 - Promote Development To Staging

Purpose: move the exact verified source to `staging` without rewriting history.

Allowed path:

```bash
git switch staging || git switch -c staging --track origin/staging
git merge --ff-only origin/development
git push origin staging
```

If fast-forward is not possible:

- stop
- record the diverging commits
- do not merge with a non-fast-forward merge commit unless CTO explicitly approves
- do not force-push

Gate:

```bash
git rev-parse staging
git rev-parse origin/staging
git merge-base --is-ancestor origin/development origin/staging
```

The staging branch must contain the verified development commit.

### C5 - Staging Verification

Purpose: prove staging is not just pushed, but still release-valid.

Required gates:

```bash
PYTHONPATH=src .venv/bin/python scripts/ci/verify_standalone_graph_runtime_pack.py
PYTHONPATH=src .venv/bin/python scripts/ci/acceptance_standalone_graph_runtime_pack.py
PYTHONPATH=src .venv/bin/python -m pytest tests/test_m365_runtime_0_1_2_readiness_fix.py
cd /Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2 && env LC_ALL=C LANG=C shasum -a 256 -c SHA256SUMS
```

Gate:

- all staging gates pass

### C6 - Promote Staging To Main

Purpose: make `main` the release source branch for a user-facing M365 pack release.

Allowed direct path if repo permissions allow it:

```bash
git switch main || git switch -c main --track origin/main
git merge --ff-only origin/staging
git push origin main
```

If branch protection blocks direct push:

- create a PR from `staging` into `main`
- do not bypass branch protection
- stop after the PR is opened unless the tooling permits governed merge and all checks are green

If fast-forward is not possible:

- stop
- record the diverging commits
- do not force-push

Gate:

```bash
git rev-parse main
git rev-parse origin/main
git merge-base --is-ancestor origin/staging origin/main
```

The main branch must contain the verified staging commit.

### C7 - Clean Main Rebuild And Release Asset Freeze

Purpose: build the release from `main`, not from a development-only local state.

Required checks:

```bash
git switch main
git status --short
.venv/bin/python scripts/ci/build_standalone_graph_runtime_pack.py
cd /Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2 && env LC_ALL=C LANG=C shasum -a 256 -c SHA256SUMS
cd /Users/smarthaus/Projects/GitHub/M365 && PYTHONPATH=src .venv/bin/python scripts/ci/verify_standalone_graph_runtime_pack.py
```

If the rebuild changes bundle, manifest, payload, conformance, provenance, release packet, or diagnostic hashes:

1. inspect why
2. update evidence if the change is legitimate
3. commit the updated generated/evidence files on `main`
4. rebuild again from a clean tree
5. repeat until clean-main rebuild is stable or fail closed

Gate:

- final source tree is clean or contains only explicitly expected release-generated files that are committed before proceeding
- installed provenance records clean source truth
- final release asset hash set is recorded
- no release asset is created from a dirty worktree

### C8 - Create Release Tag

Purpose: bind the release identity to one main commit.

Tag:

```text
com.smarthaus.m365-v0.1.2
```

Allowed path:

```bash
git switch main
git status --short
git tag -a com.smarthaus.m365-v0.1.2 -m "Release com.smarthaus.m365 0.1.2"
git push origin com.smarthaus.m365-v0.1.2
```

If the tag already exists:

- if it points to the same main commit, record that and continue
- if it points to a different commit, stop
- do not delete or move the tag without explicit CTO approval

Gate:

```bash
git rev-list -n 1 com.smarthaus.m365-v0.1.2
git rev-parse origin/main
```

The tag commit must equal the final release main commit.

### C9 - Create Draft GitHub Release And Upload Assets

Purpose: publish a release candidate as a draft first, then validate the downloaded bytes before publishing.

Release title:

```text
SMARTHAUS M365 Integration Pack 0.1.2
```

Required assets:

- `com.smarthaus.m365-0.1.2.ucp.tar.gz`
- `SHA256SUMS`
- `manifest.json`
- `conformance.json`
- `provenance.json`

Recommended additional assets if present and relevant:

- `pack_dependencies.json`
- `pack_metadata.json`
- `payload.tar.gz`
- `signatures/manifest.sig`
- `signatures/payload.sig`
- release notes markdown

Release notes must say:

- this is the canonical `com.smarthaus.m365@0.1.2` GitHub Release
- the pack is read-only
- no username/password auth is used
- auth is Microsoft OAuth/device-code or configured app-only auth
- local IntegrationPacks is a cache/install path, not the canonical release authority
- UCP admission is a follow-on UCP plan

Gate:

```bash
gh release view com.smarthaus.m365-v0.1.2 --json tagName,targetCommitish,name,isDraft,isPrerelease,assets
```

The release must exist as draft with all required assets.

### C10 - Downloaded Release Verification

Purpose: verify the GitHub Release from the user/UCP perspective.

Use a temp directory. Do not verify by reading local dist or local IntegrationPacks directly.

Suggested flow:

```bash
tmpdir="$(mktemp -d)"
cd "$tmpdir"
gh release download com.smarthaus.m365-v0.1.2 --repo SmartHausGroup/M365
env LC_ALL=C LANG=C shasum -a 256 -c SHA256SUMS
mkdir extracted
tar -xzf com.smarthaus.m365-0.1.2.ucp.tar.gz -C extracted
find extracted -maxdepth 3 -type f | sort
```

Then prove:

- the bundle extracts
- the payload extracts
- `m365_runtime` imports from extracted payload without `PYTHONPATH=src`
- no M365 source repo path is required
- release manifest version is `0.1.2`
- release provenance points to the final main release commit

If the existing verifier cannot target a downloaded release directory, update the verifier under this plan so it can. Do not accept a verifier that only checks local source or local IntegrationPacks.

Gate:

- downloaded `SHA256SUMS` passes
- extracted release imports/launches without source repo
- release provenance matches tag/main commit

### C11 - Publish GitHub Release

Purpose: move from draft to real user-facing release after downloaded-release verification passes.

Allowed path:

```bash
gh release edit com.smarthaus.m365-v0.1.2 --draft=false --latest
```

Gate:

```bash
gh release view com.smarthaus.m365-v0.1.2 --json tagName,targetCommitish,name,isDraft,isPrerelease,isLatest,assets
```

The release must be non-draft and reference the final tag/main commit.

### C12 - UCP Handoff Packet

Purpose: create a precise M365-to-UCP handoff without mutating UCP.

Create M365-side handoff docs under `docs/commercialization/` and optionally `docs/prompts/`.

The handoff must tell the UCP agent:

- release repo: `SmartHausGroup/M365`
- tag: `com.smarthaus.m365-v0.1.2`
- release asset: `com.smarthaus.m365-0.1.2.ucp.tar.gz`
- required checksum file: `SHA256SUMS`
- manifest version: `0.1.2`
- runtime entrypoint from manifest
- dependency contract asset/path
- install/cache target: `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/`
- UCP must admit from GitHub Release asset, not from source repo and not from a hand-copied local folder
- UCP must verify checksum before install
- UCP must materialize installed payload under its runtime root
- UCP must launch runtime from installed artifact
- UCP must drive auth lifecycle through declared endpoints
- UCP readiness may be false until tenant auth/config is completed
- UCP must not require `M365_REPO_ROOT`, sibling repo lookup, or local source checkout

Gate:

- handoff file exists
- no UCP repo file was modified
- handoff references the published GitHub Release URL and exact final hashes

### C13 - Tracker Closeout

Purpose: make the governance state match reality.

Update:

- `Operations/ACTION_LOG.md`
- `Operations/EXECUTION_PLAN.md`
- `Operations/PROJECT_FILE_INDEX.md`
- this plan triplet `.md`, `.yaml`, `.json`
- prompt artifacts if final URLs/hashes need synchronization

Final gates:

```bash
git status -sb
git diff --check
.venv/bin/python -m json.tool plans/m365-github-release-and-ucp-handoff-closure/m365-github-release-and-ucp-handoff-closure.json >/dev/null
.venv/bin/python - <<'PY'
import yaml
from pathlib import Path
yaml.safe_load(Path("plans/m365-github-release-and-ucp-handoff-closure/m365-github-release-and-ucp-handoff-closure.yaml").read_text())
PY
gh release view com.smarthaus.m365-v0.1.2 --json tagName,targetCommitish,name,isDraft,isPrerelease,isLatest,assets
```

Gate:

- all trackers agree the M365 GitHub Release is complete
- UCP handoff is complete
- final repo state is clean after the closure commit/push, or the only uncommitted files are explicitly listed as a hard blocker

## Release Acceptance Criteria

The plan is complete only when all of the following are true:

- `origin/development` contains the verified M365 `0.1.2` source/evidence.
- `origin/staging` contains the same release source by fast-forward or governed PR/merge.
- `origin/main` contains the same release source by fast-forward or governed PR/merge.
- tag `com.smarthaus.m365-v0.1.2` points to the final main release commit.
- GitHub Release `SMARTHAUS M365 Integration Pack 0.1.2` exists and is non-draft.
- required release assets are present.
- downloaded release assets verify with `SHA256SUMS`.
- downloaded release bundle extracts and imports without source repo paths.
- local IntegrationPacks `0.1.2` is documented as a cache/install copy.
- UCP handoff tells UCP to admit from GitHub Release, not local source or sibling lookup.
- action log and execution plan are synchronized.

## Hard Blockers

Claude must stop and report a hard blocker if any of these occur:

- wrong repo, wrong remote, or unexpected branch
- remote branch divergence
- branch protection blocks direct push and no PR path is available
- release tag exists on a different commit
- GitHub CLI lacks release permission
- downloaded asset checksum mismatch
- clean-main rebuild cannot converge
- source-repo dependency reappears
- UCP mutation is required to finish this M365 plan
- secrets or tokens would need to be written to disk or logs

## Final State To Report

Claude's final report must include:

- final `development`, `staging`, and `main` commit SHAs
- tag SHA
- GitHub Release URL
- final release asset names and SHA256 hashes
- downloaded-release verification result
- local IntegrationPacks cache state
- UCP handoff doc path
- remaining UCP-side work, explicitly framed as outside the M365 repo
