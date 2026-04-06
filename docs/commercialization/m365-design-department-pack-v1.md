# M365 Design Department Pack v1

## Purpose

Turn the authoritative Design persona contract into one bounded department pack that can
be governed, delegated to, and measured as a fully action-backed workforce unit.

## Problem

The Design department-pack authority already carried the correct H3 persona counts, but
its human-readable contract and validation surfaces still described the pack as blocked and
contract-only. H4S corrects that stale readiness claim so H4 can inherit a truthful
department-pack dependency base.

## Decision

`registry/department_pack_design_v1.yaml` is the authoritative Design
department-pack contract and now explicitly reflects the fully active staged authority.

The shared runtime remains `src/smarthaus_common/department_pack.py`.

This H4S rebase locks the following truth:

- total personas: `5`
- active personas: `5`
- registry-backed personas: `5`
- supported action count: `36`
- default pack state without queue pressure: `ready`

## Design Pack Boundary

The Design pack contains exactly `5` registry-backed personas:
- `brand-guardian` — Isabella Rossi (Brand Guardian); registry-backed; actions=8
- `ui-designer` — Noah Anderson (UI Designer); registry-backed; actions=7
- `ux-researcher` — Mila Novak (UX Researcher); registry-backed; actions=7
- `visual-storyteller` — Diego Alvarez (Visual Storyteller); registry-backed; actions=7
- `whimsy-injector` — Luna Park (Delight Designer); registry-backed; actions=7

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

- one truthful Design department-pack authority reconciled to H3/H4S
- one deterministic ready-pack summary for brand governance, interface design, research synthesis, visual storytelling, and delight design
- fail-closed behavior for missing personas, invalid authorities, or mismatched action counts
- no over-claim beyond the explicit registry-backed action surface

## No-Go Conditions

- the pack fabricates personas not present in `registry/persona_registry_v2.yaml`
- supported action counts drift from the declared authority
- an active Design persona is reclassified as contract-only without a governed rebase
- the department-pack authority drifts from the staged H3 counts or action surface
