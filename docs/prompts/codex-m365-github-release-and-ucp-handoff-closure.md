# Execution Prompt - M365 GitHub Release And UCP Handoff Closure

Plan Reference: `plan:m365-github-release-and-ucp-handoff-closure`
Repo: `/Users/smarthaus/Projects/GitHub/M365`
Primary Plan: `plans/m365-github-release-and-ucp-handoff-closure/m365-github-release-and-ucp-handoff-closure.md`

## Mission

Close the M365 Integration Pack release properly.

The M365-side `com.smarthaus.m365@0.1.2` pack works locally and has local install/cache evidence, but that is not the same thing as a user-facing release. Your job is to promote the verified source from `development` to `staging` to `main`, create a proper GitHub Release from `main`, verify the release by downloading the release assets, and create the M365-side UCP handoff package.

Do not mutate UCP. The UCP work comes later through a UCP plan.

## Repository Guard

This is a multi-repo workspace. Before doing anything, prove you are in the right repo:

```bash
cd /Users/smarthaus/Projects/GitHub/M365
pwd
git rev-parse --show-toplevel
git branch --show-current
git remote -v
```

Expected:

- `pwd` is `/Users/smarthaus/Projects/GitHub/M365`
- top level is `/Users/smarthaus/Projects/GitHub/M365`
- starting branch is `development`
- origin is `https://github.com/SmartHausGroup/M365.git`

Fail closed if any value differs.

## Governance Contract

Follow `AGENTS.md`, `Operations/NORTHSTAR.md`, `Operations/EXECUTION_PLAN.md`, `.cursor/rules/*.mdc`, and MCP governance.

Before any write, command execution, test run, commit, push, release creation, or config change, call MCP `validate_action` with the correct repo, action type, scope, target, plan reference, approval state, branch, and metadata.

If MCP returns a rules/process/governance error, do not abandon the plan. Fix the missing plan reference, notebook evidence, invariant linkage, scope, metadata, or approval shape that MCP identifies, then continue.

If MCP requires human approval that cannot be satisfied by evidence, stop and report a hard blocker.

## Release Model

The release source of truth must be:

```text
SmartHausGroup/M365 GitHub Release
tag: com.smarthaus.m365-v0.1.2
asset: com.smarthaus.m365-0.1.2.ucp.tar.gz
checksum: SHA256SUMS
```

The local directory below is only a cache/install copy:

```text
/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/
```

Do not describe the local folder as the canonical release authority.

## Current Truth At Prompt Creation

- Repo branch: `development`
- Local HEAD: `257693a33fddcc83dd2ff63ccffc328c010683a8`
- Local state: `development` was ahead of `origin/development` by 5 commits
- GitHub releases: none existed at prompt creation
- Current local bundle SHA256: `29c1d05bc30f570373d09a2ebb38313bda8466d4faa31e70a2e865e1c046fd9e`
- Current local manifest SHA256: `bfc52d4b4e585604cac426d546153e5a7d54180630cadbf9a2b7f7c62a8584e9`
- Current local payload SHA256: `c09625a5b89b1578e2226463d43670dc8355db7d489338f3bf42001db16cabfd`
- Current local conformance SHA256: `ab03f4277ecf700e4b032da843b8d45760358c3dd13a6b42c94033a154af3da7`
- Current dependency lock SHA256: `376f10bab9f3554e5bce73ef55ea157bb8fe866e3d498ea50c6895b87e8f0e0b`

Recheck these values. If they changed, use the live values, update evidence, and explain why.

## Execution Discipline

Execute the plan in exact chunk order:

```text
C0 preflight
C1 review-truth conflicts
C2 development verification
C3 development push
C4 staging promotion
C5 staging verification
C6 main promotion
C7 clean main rebuild
C8 tag
C9 draft GitHub Release
C10 downloaded-release verification
C11 publish GitHub Release
C12 UCP handoff packet
C13 tracker closeout
```

Rules:

- Work one chunk at a time.
- State which chunk you are starting.
- Run the chunk gate before moving on.
- If a gate fails, fix the root cause if it is in scope.
- Do not hide a failure with wording.
- Do not use source-repo behavior to prove release behavior.
- Do not use local IntegrationPacks to prove downloaded-release behavior.

## Non-Negotiable Git Rules

- Do not force-push.
- Do not use `git reset --hard`.
- Do not rewrite or move a tag unless the CTO explicitly approves it.
- Do not publish a release from a dirty worktree.
- If `staging` or `main` cannot fast-forward, stop and report the exact diverging commits.
- If branch protection blocks direct push, create a PR if permitted; otherwise stop with the PR requirement.

## Required Gates

Development and staging gates:

```bash
PYTHONPATH=src .venv/bin/python scripts/ci/verify_standalone_graph_runtime_pack.py
PYTHONPATH=src .venv/bin/python scripts/ci/acceptance_standalone_graph_runtime_pack.py
PYTHONPATH=src .venv/bin/python -m pytest tests/test_m365_runtime_0_1_2_readiness_fix.py tests/test_m365_runtime_p4_runtime_and_auth.py tests/test_m365_runtime_p5_graph_actions.py tests/test_m365_runtime_p5_launcher_app.py tests/test_m365_runtime_p7_packaging.py tests/test_ucp_m365_pack_client.py
cd /Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2 && env LC_ALL=C LANG=C shasum -a 256 -c SHA256SUMS
cd /Users/smarthaus/Projects/GitHub/M365 && git diff --check
```

Downloaded release gate:

```bash
tmpdir="$(mktemp -d)"
cd "$tmpdir"
gh release download com.smarthaus.m365-v0.1.2 --repo SmartHausGroup/M365
env LC_ALL=C LANG=C shasum -a 256 -c SHA256SUMS
mkdir extracted
tar -xzf com.smarthaus.m365-0.1.2.ucp.tar.gz -C extracted
find extracted -maxdepth 3 -type f | sort
```

Then prove the downloaded release extracts, imports `m365_runtime` without `PYTHONPATH=src`, and carries provenance pointing at the final main release commit.

If the verifier cannot target a downloaded release directory, update the verifier under this plan so it can. A verifier that only checks local source or local IntegrationPacks is insufficient.

## Required Release Assets

Upload these to the GitHub Release:

- `com.smarthaus.m365-0.1.2.ucp.tar.gz`
- `SHA256SUMS`
- `manifest.json`
- `conformance.json`
- `provenance.json`

Upload these too if present and relevant:

- `pack_dependencies.json`
- `pack_metadata.json`
- `payload.tar.gz`
- `signatures/manifest.sig`
- `signatures/payload.sig`
- release notes markdown

Create a draft release first. Only publish after downloaded-release verification passes.

## UCP Handoff Requirements

At the end, create an M365-side handoff document. Do not edit UCP.

The handoff must tell UCP:

- admit from `SmartHausGroup/M365` GitHub Release
- use tag `com.smarthaus.m365-v0.1.2`
- use asset `com.smarthaus.m365-0.1.2.ucp.tar.gz`
- verify `SHA256SUMS` before install
- treat `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.2/` as local cache/install only
- do not use `M365_REPO_ROOT`
- do not scan sibling M365 source repo
- launch the runtime from the installed artifact
- use the declared auth lifecycle endpoints
- keep readiness false until tenant auth/config passes

## Final Report

When complete, report:

- final `development`, `staging`, and `main` commit SHAs
- tag SHA
- GitHub Release URL
- release asset names and SHA256 hashes
- downloaded-release verification result
- local IntegrationPacks cache state
- UCP handoff doc path
- any remaining UCP-side work, explicitly outside this M365 plan
