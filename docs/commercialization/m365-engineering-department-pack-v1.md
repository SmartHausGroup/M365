# M365 Engineering Department Pack v1

## Purpose

Turn the authoritative Engineering persona contract into one bounded department pack that can
be governed, delegated to, and measured while the staged post-H3 roster remains fail-closed.

## Problem

H3 rebased the authoritative persona registry to `59` personas, but the engineering
department-pack contract still encoded pre-H3 counts. H4S corrects that scope gap so H4 can
resume certification/count rebase from truthful department-pack authority.

## Decision

`registry/department_pack_engineering_v1.yaml` is the authoritative Engineering
department-pack contract and now reconciles to the staged post-H3 authoritative roster.

The shared runtime remains `src/smarthaus_common/department_pack.py`.

This H4S rebase locks the following staged truth:

- total personas: `8`
- active personas: `7`
- registry-backed personas: `7`
- persona-contract-only personas: `1`
- supported action count: `62`
- pack state before later activation acts: `blocked`

## Engineering Pack Boundary

The Engineering pack now contains exactly `8` authoritative personas:
- `ai-engineer` — Alex Thompson (ML Engineer); registry-backed; actions=10
- `backend-architect` — Jordan Kim (Principal Backend Engineer); registry-backed; actions=13
- `devops-automator` — Casey Johnson (DevOps Engineer); registry-backed; actions=10
- `frontend-developer` — Riley Martinez (UI/UX Developer); registry-backed; actions=7
- `mobile-app-builder` — Taylor Brown (Mobile Engineer); registry-backed; actions=7
- `platform-manager` — Andre Baptiste (Platform Engineering Manager); persona-contract-only; actions=0
- `rapid-prototyper` — Ethan Rivera (Prototype Engineer); registry-backed; actions=8
- `test-writer-fixer` — Grace Lee (Test Engineer); registry-backed; actions=7

Registry-backed execution coverage is limited to `ai-engineer`, `backend-architect`, `devops-automator`, `frontend-developer`, `mobile-app-builder`, `rapid-prototyper`, `test-writer-fixer`.

Persona-contract-only coverage is limited to `platform-manager`.

Seven engineering personas remain action-backed while platform stewardship stays contract-only.

## Department Pack Contract

Every Engineering pack snapshot must include:

- department metadata
- workload and workflow families
- approval model
- KPI contract
- personas
  - persona context from the authoritative persona registry
  - accountability state
  - queue depth
  - memory count
  - work-history event count
  - coverage status
- pack summary
  - persona counts
  - supported action count
  - workload-family count
  - workflow-family count
  - pack state

## Runtime Rule

Department-pack state is projected, not hand-maintained.

That means:

- personas come from the authoritative persona registry
- the pack boundary comes from the department-pack authority file
- accountability comes from the shared persona-accountability runtime
- memory and work-history counts come from the shared persona-memory runtime
- any planned persona keeps the pack fail-closed as `blocked`

## Required Guarantees

- one truthful Engineering department-pack authority reconciled to H3
- one deterministic pack summary for architecture, automation, frontend/mobile delivery, prototyping, testing, and platform stewardship
- fail-closed behavior for missing personas, invalid authorities, or mismatched action counts
- no over-claim of active or registry-backed coverage beyond the staged authoritative truth

## No-Go Conditions

- the pack fabricates personas not present in `registry/persona_registry_v2.yaml`
- a contract-only persona declares live supported actions
- the pack claims a planned persona is active or registry-backed
- the department-pack authority drifts from the staged H3 counts
