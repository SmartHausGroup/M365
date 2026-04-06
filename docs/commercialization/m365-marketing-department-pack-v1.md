# M365 Marketing Department Pack v1

## Purpose

Turn the authoritative Marketing persona contract into one bounded department pack that can
be governed, delegated to, and measured against the final post-H5 source-branch authority while
preserving the certified `partial-activation` department taxonomy required by downstream certification.

## Problem

The shared runtime already enforced exact registry parity, but this department-pack authority still left Lucia Fernandez staged as contract-only while the authoritative registry had already promoted her to registry-backed execution. That stale layer blocked fresh M1 replay even though the only remaining planned personas are the five deferred external-platform roles.

## Decision

`registry/department_pack_marketing_v1.yaml` is the authoritative Marketing
department-pack contract and now explicitly reflects the final post-H5 source-branch authority.

The shared runtime remains `src/smarthaus_common/department_pack.py`.

This correction locks the following truth:

- total personas: `8`
- active personas: `3`
- registry-backed personas: `3`
- persona-contract-only personas: `5`
- supported action count: `24`
- default pack state without queue pressure: `blocked`
- preserved department status taxonomy: `partial-activation`

## Marketing Pack Boundary

The Marketing pack contains exactly `8` authoritative personas. Only the three registry-backed personas may claim action-backed execution; the five deferred external-platform personas remain contract-only.
- `app-store-optimizer` — Jake Thompson (ASO Specialist); persona-contract-only; actions=0
- `content-creator` — Taylor Swift (Content Strategist); registry-backed; actions=8
- `growth-hacker` — Morgan Davis (Growth Lead); registry-backed; actions=10
- `instagram-curator` — Zoe Martinez (Visual Content Specialist); persona-contract-only; actions=0
- `reddit-community-builder` — Priya Singh (Community Manager); persona-contract-only; actions=0
- `tiktok-strategist` — Ryan O'Connor (Short-form Video Expert); persona-contract-only; actions=0
- `twitter-engager` — Jamie Lee (Social Media Director); persona-contract-only; actions=0
- `website-operations-specialist` — Lucia Fernandez (Website Operations Specialist); registry-backed; actions=6

The pack may claim only those personas and their explicit bounded workflows.

## Runtime Rule

Department-pack state is projected, not hand-maintained.

That means:

- personas come from the authoritative persona registry
- the pack boundary comes from the department-pack authority file
- accountability comes from the shared persona-accountability runtime
- memory and work-history counts come from the shared persona-memory runtime
- the default state remains `blocked` while any planned persona remains in the boundary

## Required Guarantees

- one truthful Marketing department-pack authority reconciled to the post-H5 source-branch truth
- one deterministic blocked-pack summary while the five deferred external-platform personas remain planned
- fail-closed behavior for missing personas, invalid authorities, or mismatched action counts
- no over-claim beyond the three explicit registry-backed marketing personas
- preservation of the certified partial-activation department taxonomy for downstream certification compatibility

## No-Go Conditions

- website-operations-specialist remains contract-only after the authoritative registry marks her registry-backed
- any deferred external-platform persona declares live supported actions
- supported action counts drift from the declared authority
- the department-pack authority drifts from the post-H5 source-branch truth or preserved taxonomy
