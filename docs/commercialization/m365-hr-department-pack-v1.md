# M365 Human Resources Department Pack v1

## Purpose

Turn the authoritative Human Resources persona contract into one bounded department pack that can
be governed, delegated to, and measured while the staged post-H3 roster remains fail-closed.

## Problem

H3 rebased the authoritative persona registry to `59` personas, but the hr
department-pack contract still encoded pre-H3 counts. H4S corrects that scope gap so H4 can
resume certification/count rebase from truthful department-pack authority.

## Decision

`registry/department_pack_hr_v1.yaml` is the authoritative Human Resources
department-pack contract and now reconciles to the staged post-H3 authoritative roster.

The shared runtime remains `src/smarthaus_common/department_pack.py`.

This H4S rebase locks the following staged truth:

- total personas: `2`
- active personas: `1`
- registry-backed personas: `1`
- persona-contract-only personas: `1`
- supported action count: `5`
- pack state before later activation acts: `blocked`

## Human Resources Pack Boundary

The Human Resources pack now contains exactly `2` authoritative personas:
- `hr-generalist` — Sarah Williams (HR Director); registry-backed; actions=5
- `recruitment-assistance-agent` — Camila Torres (Recruiting Coordinator); persona-contract-only; actions=0

Registry-backed execution coverage is limited to `hr-generalist`.

Persona-contract-only coverage is limited to `recruitment-assistance-agent`.

Sarah Williams remains the only action-backed HR anchor while recruiting support stays contract-only.

## Department Pack Contract

Every Human Resources pack snapshot must include:

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

- one truthful Human Resources department-pack authority reconciled to H3
- one deterministic pack summary for HR administration, recruiting support, review orchestration, and policy governance
- fail-closed behavior for missing personas, invalid authorities, or mismatched action counts
- no over-claim of active or registry-backed coverage beyond the staged authoritative truth

## No-Go Conditions

- the pack fabricates personas not present in `registry/persona_registry_v2.yaml`
- a contract-only persona declares live supported actions
- the pack claims a planned persona is active or registry-backed
- the department-pack authority drifts from the staged H3 counts
