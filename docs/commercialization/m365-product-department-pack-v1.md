# M365 Product Department Pack v1

## Purpose

Turn the authoritative Product persona contract into one bounded department pack that can
be governed, delegated to, and measured as a fully action-backed workforce unit.

## Problem

The Product department-pack authority already carried the correct H3 persona counts, but
its human-readable contract and validation surfaces still described the pack as blocked and
contract-only. H4S corrects that stale readiness claim so H4 can inherit a truthful
department-pack dependency base.

## Decision

`registry/department_pack_product_v1.yaml` is the authoritative Product
department-pack contract and now explicitly reflects the fully active staged authority.

The shared runtime remains `src/smarthaus_common/department_pack.py`.

This H4S rebase locks the following truth:

- total personas: `3`
- active personas: `3`
- registry-backed personas: `3`
- supported action count: `22`
- default pack state without queue pressure: `ready`

## Product Pack Boundary

The Product pack contains exactly `3` registry-backed personas:
- `feedback-synthesizer` — Maya Patel (User Research Lead); registry-backed; actions=7
- `sprint-prioritizer` — Sam Chen (Product Manager); registry-backed; actions=8
- `trend-researcher` — Chris Wong (Market Analyst); registry-backed; actions=7

The pack may claim only those personas and their explicit action-backed workflows.

## Runtime Rule

Department-pack state is projected, not hand-maintained.

That means:

- personas come from the authoritative persona registry
- the pack boundary comes from the department-pack authority file
- accountability comes from the shared persona-accountability runtime
- memory and work-history counts come from the shared persona-memory runtime
- the default state is `ready` until queue/accountability evidence moves the pack to `watch`
  or `attention_required`

## Required Guarantees

- one truthful Product department-pack authority reconciled to H3/H4S
- one deterministic ready-pack summary for backlog planning, feedback synthesis, and market opportunity analysis
- fail-closed behavior for missing personas, invalid authorities, or mismatched action counts
- no over-claim beyond the explicit registry-backed action surface

## No-Go Conditions

- the pack fabricates personas not present in `registry/persona_registry_v2.yaml`
- supported action counts drift from the declared authority
- an active Product persona is reclassified as contract-only without a governed rebase
- the department-pack authority drifts from the staged H3 counts or action surface
