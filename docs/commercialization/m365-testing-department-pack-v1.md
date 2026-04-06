# M365 Testing Department Pack v1

## Purpose

Turn the authoritative Testing persona contract into one bounded department pack that can
be governed, delegated to, and measured as a fully action-backed workforce unit.

## Problem

The Testing department-pack authority already carried the correct H3 persona counts, but
its human-readable contract and validation surfaces still described the pack as blocked and
contract-only. H4S corrects that stale readiness claim so H4 can inherit a truthful
department-pack dependency base.

## Decision

`registry/department_pack_testing_v1.yaml` is the authoritative Testing
department-pack contract and now explicitly reflects the fully active staged authority.

The shared runtime remains `src/smarthaus_common/department_pack.py`.

This H4S rebase locks the following truth:

- total personas: `5`
- active personas: `5`
- registry-backed personas: `5`
- supported action count: `38`
- default pack state without queue pressure: `ready`

## Testing Pack Boundary

The Testing pack contains exactly `5` registry-backed personas:
- `api-tester` — Nina Shah (QA Automation Lead); registry-backed; actions=8
- `performance-benchmarker` — Omar Haddad (Performance Engineer); registry-backed; actions=8
- `test-results-analyzer` — Sofia Alvarez (Quality Analyst); registry-backed; actions=7
- `tool-evaluator` — Liam Nguyen (Dev Tools Strategist); registry-backed; actions=7
- `workflow-optimizer` — Ava Johnson (Process Engineer); registry-backed; actions=8

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

- one truthful Testing department-pack authority reconciled to H3/H4S
- one deterministic ready-pack summary for qa automation, benchmarking, quality reporting, and workflow optimization
- fail-closed behavior for missing personas, invalid authorities, or mismatched action counts
- no over-claim beyond the explicit registry-backed action surface

## No-Go Conditions

- the pack fabricates personas not present in `registry/persona_registry_v2.yaml`
- supported action counts drift from the declared authority
- an active Testing persona is reclassified as contract-only without a governed rebase
- the department-pack authority drifts from the staged H3 counts or action surface
