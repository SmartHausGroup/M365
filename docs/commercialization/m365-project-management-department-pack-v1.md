# M365 Project Management Department Pack v1

## Purpose

Turn the authoritative Project Management persona contract into one bounded department pack that can
be governed, delegated to, and measured while the staged post-H3 roster remains fail-closed.

## Problem

H3 rebased the authoritative persona registry to `59` personas, but the project-management
department-pack contract still encoded pre-H3 counts. H4S corrects that scope gap so H4 can
resume certification/count rebase from truthful department-pack authority.

## Decision

`registry/department_pack_project_management_v1.yaml` is the authoritative Project Management
department-pack contract and now reconciles to the staged post-H3 authoritative roster.

The shared runtime remains `src/smarthaus_common/department_pack.py`.

This H4S rebase locks the following staged truth:

- total personas: `5`
- active personas: `3`
- registry-backed personas: `3`
- persona-contract-only personas: `2`
- supported action count: `26`
- pack state before later activation acts: `blocked`

## Project Management Pack Boundary

The Project Management pack now contains exactly `5` authoritative personas:
- `experiment-tracker` — Emily Carter (Experimentation PM); registry-backed; actions=8
- `project-coordination-agent` — Sofia Petrova (Project Coordinator); persona-contract-only; actions=0
- `project-manager` — Haruto Tanaka (Project Manager); persona-contract-only; actions=0
- `project-shipper` — Ben Foster (Release Manager); registry-backed; actions=9
- `studio-producer` — Olivia Park (Studio Producer); registry-backed; actions=9

Registry-backed execution coverage is limited to `experiment-tracker`, `project-shipper`, `studio-producer`.

Persona-contract-only coverage is limited to `project-coordination-agent`, `project-manager`.

Ben Foster, Emily Carter, and Olivia Park remain the action-backed Project Management anchors.

## Department Pack Contract

Every Project Management pack snapshot must include:

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

- one truthful Project Management department-pack authority reconciled to H3
- one deterministic pack summary for release coordination, project leadership, experimentation reporting, and schedule orchestration
- fail-closed behavior for missing personas, invalid authorities, or mismatched action counts
- no over-claim of active or registry-backed coverage beyond the staged authoritative truth

## No-Go Conditions

- the pack fabricates personas not present in `registry/persona_registry_v2.yaml`
- a contract-only persona declares live supported actions
- the pack claims a planned persona is active or registry-backed
- the department-pack authority drifts from the staged H3 counts
