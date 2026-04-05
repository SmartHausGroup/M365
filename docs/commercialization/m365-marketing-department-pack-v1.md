# M365 Marketing Department Pack v1

## Purpose

Turn the authoritative Marketing persona contract into one bounded department pack that can
be governed, delegated to, and measured while the staged post-H3 roster remains fail-closed.

## Problem

H3 rebased the authoritative persona registry to `59` personas, but the marketing
department-pack contract still encoded pre-H3 counts. H4S corrects that scope gap so H4 can
resume certification/count rebase from truthful department-pack authority.

## Decision

`registry/department_pack_marketing_v1.yaml` is the authoritative Marketing
department-pack contract and now reconciles to the staged post-H3 authoritative roster.

The shared runtime remains `src/smarthaus_common/department_pack.py`.

This H4S rebase locks the following staged truth:

- total personas: `8`
- active personas: `2`
- registry-backed personas: `2`
- persona-contract-only personas: `6`
- supported action count: `18`
- pack state before later activation acts: `blocked`

## Marketing Pack Boundary

The Marketing pack now contains exactly `8` authoritative personas:
- `app-store-optimizer` — Jake Thompson (ASO Specialist); persona-contract-only; actions=0
- `content-creator` — Taylor Swift (Content Strategist); registry-backed; actions=8
- `growth-hacker` — Morgan Davis (Growth Lead); registry-backed; actions=10
- `instagram-curator` — Zoe Martinez (Visual Content Specialist); persona-contract-only; actions=0
- `reddit-community-builder` — Priya Singh (Community Manager); persona-contract-only; actions=0
- `tiktok-strategist` — Ryan O'Connor (Short-form Video Expert); persona-contract-only; actions=0
- `twitter-engager` — Jamie Lee (Social Media Director); persona-contract-only; actions=0
- `website-operations-specialist` — Lucia Fernandez (Website Operations Specialist); persona-contract-only; actions=0

Registry-backed execution coverage is limited to `content-creator`, `growth-hacker`.

Persona-contract-only coverage is limited to `app-store-optimizer`, `instagram-curator`, `reddit-community-builder`, `tiktok-strategist`, `twitter-engager`, `website-operations-specialist`.

Taylor Swift and Morgan Davis remain the only action-backed Marketing anchors in the staged model.

## Department Pack Contract

Every Marketing pack snapshot must include:

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

- one truthful Marketing department-pack authority reconciled to H3
- one deterministic pack summary for growth experimentation, content preparation, social planning, and website operations support
- fail-closed behavior for missing personas, invalid authorities, or mismatched action counts
- no over-claim of active or registry-backed coverage beyond the staged authoritative truth

## No-Go Conditions

- the pack fabricates personas not present in `registry/persona_registry_v2.yaml`
- a contract-only persona declares live supported actions
- the pack claims a planned persona is active or registry-backed
- the department-pack authority drifts from the staged H3 counts
