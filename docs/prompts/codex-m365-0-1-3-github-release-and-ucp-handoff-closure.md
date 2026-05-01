# Execution Prompt - M365 0.1.3 GitHub Release And UCP Handoff Closure

Plan Reference: `plan:m365-0-1-3-github-release-and-ucp-handoff-closure`
Repo: `/Users/smarthaus/Projects/GitHub/M365`
Primary Plan: `plans/m365-0-1-3-github-release-and-ucp-handoff-closure/m365-0-1-3-github-release-and-ucp-handoff-closure.md`

## Mission

Commit, push, promote, clean-rebuild, tag, and publish the already live-tested `com.smarthaus.m365@0.1.3` Integration Pack.

The release must be canonical on GitHub:

```text
repo: SmartHausGroup/M365
tag:  com.smarthaus.m365-v0.1.3
asset: com.smarthaus.m365-0.1.3.ucp.tar.gz
```

Do not mutate UCP. The UCP work comes later through a UCP-owned plan.

## Governance Contract

Follow `AGENTS.md`, `Operations/NORTHSTAR.md`, `Operations/EXECUTION_PLAN.md`, `.cursor/rules/*.mdc`, and UCP MCP governance.

Before any mutating action, call MCP `validate_action` with the correct repo, action type, scope, target, plan reference, approval state, branch, and metadata. Include `metadata.has_notebook_backing=true` with `notebooks/m365/INV-M365-DP-auth-persistence-reconnect-v1.ipynb` where required.

## Chunk Order

Execute in order:

```text
C0 preflight
C1 validate and commit feature branch
C2 push feature branch
C3 promote to development
C4 promote to staging
C5 promote to main
C6 clean-source rebuild
C7 tag com.smarthaus.m365-v0.1.3
C8 create draft GitHub Release
C9 downloaded-release verification
C10 publish GitHub Release
C11 write M365-side UCP handoff packet
C12 tracker closeout
```

Stop on first hard blocker.

## Non-Negotiable Rules

- Do not force-push.
- Do not use `git reset --hard`.
- Do not rewrite existing tags.
- Do not publish from a dirty release source.
- Do not log Microsoft tokens, refresh tokens, auth codes, device codes after completion, client secrets, private keys, subject object IDs, or phone numbers.
- Do not claim UCP admission is complete.

## Required Release Finding

The release notes and handoff packet must state plainly that delegated keep-me-logged-in behavior requires `offline_access`. Without it, Microsoft may not issue a refresh token, and forced-expiry restart fails closed as `lazy_refresh:refresh_token_missing`.

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

## Final Report

Report final branch SHAs, tag, GitHub Release URL, release assets and hashes, downloaded-release verification result, local cache state, UCP handoff path, and remaining UCP-side work.
