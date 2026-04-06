# M365 Human Resources Department Pack v1

## Purpose

Turn the authoritative Human Resources persona contract into one bounded department pack that can
be governed, delegated to, and measured against the final post-H5 source-branch authority while
preserving the certified `partial-activation` department taxonomy required by downstream certification.

## Problem

The shared runtime already enforced exact registry parity, but this department-pack authority still left 1 promoted persona staged as contract-only with zero actions. That stale contract layer blocked fresh M1 replay despite the authoritative registry already carrying the final post-H5 action surface.

## Decision

`registry/department_pack_hr_v1.yaml` is the authoritative Human Resources
department-pack contract and now explicitly reflects the final post-H5 source-branch authority.

The shared runtime remains `src/smarthaus_common/department_pack.py`.

This correction locks the following truth:

- total personas: `2`
- active personas: `2`
- registry-backed personas: `2`
- supported action count: `10`
- default pack state without queue pressure: `ready`
- preserved department status taxonomy: `partial-activation`

## Human Resources Pack Boundary

The Human Resources pack contains exactly `2` registry-backed personas:
- `hr-generalist` — Sarah Williams (HR Director); registry-backed; actions=5
- `recruitment-assistance-agent` — Camila Torres (Recruiting Coordinator); registry-backed; actions=5

The pack may claim only those personas and their explicit bounded workflows.

## Runtime Rule

Department-pack state is projected, not hand-maintained.

That means:

- personas come from the authoritative persona registry
- the pack boundary comes from the department-pack authority file
- accountability comes from the shared persona-accountability runtime
- memory and work-history counts come from the shared persona-memory runtime
- the default state is `ready` until queue/accountability evidence moves the pack to `watch` or `attention_required`

## Required Guarantees

- one truthful Human Resources department-pack authority reconciled to the post-H5 source-branch truth
- one deterministic ready-pack summary for the declared workflow families without queue pressure
- fail-closed behavior for missing personas, invalid authorities, or mismatched action counts
- no over-claim beyond the explicit registry-backed action surface
- preservation of the certified partial-activation department taxonomy for downstream certification compatibility

## No-Go Conditions

- the pack fabricates personas not present in registry/persona_registry_v2.yaml
- any promoted persona remains staged as contract-only after the authoritative registry marks it registry-backed
- supported action counts drift from the declared authority
- the department-pack authority drifts from the post-H5 source-branch truth or preserved taxonomy
