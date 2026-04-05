# M365 Communication Department Pack v1

## Purpose

Turn the authoritative Communication persona contract into one bounded department pack that can
be governed, delegated to, and measured while the staged post-H3 roster remains fail-closed.

## Problem

H3 rebased the authoritative persona registry to `59` personas, but the communication
department-pack contract still encoded pre-H3 counts. H4S corrects that scope gap so H4 can
resume certification/count rebase from truthful department-pack authority.

## Decision

`registry/department_pack_communication_v1.yaml` is the authoritative Communication
department-pack contract and now reconciles to the staged post-H3 authoritative roster.

The shared runtime remains `src/smarthaus_common/department_pack.py`.

This H4S rebase locks the following staged truth:

- total personas: `4`
- active personas: `1`
- registry-backed personas: `1`
- persona-contract-only personas: `3`
- supported action count: `7`
- pack state before later activation acts: `blocked`

## Communication Pack Boundary

The Communication pack now contains exactly `4` authoritative personas:
- `calendar-management-agent` — Mateo Alvarez (Calendar Operations Coordinator); persona-contract-only; actions=0
- `email-processing-agent` — Hannah Kim (Email Operations Specialist); persona-contract-only; actions=0
- `outreach-coordinator` — David Park (Communications Manager); registry-backed; actions=7
- `teams-manager` — Alicia Nguyen (Teams Collaboration Administrator); persona-contract-only; actions=0

Registry-backed execution coverage is limited to `outreach-coordinator`.

Persona-contract-only coverage is limited to `calendar-management-agent`, `email-processing-agent`, `teams-manager`.

David Park remains the only action-backed Communication anchor before later activation acts.

## Department Pack Contract

Every Communication pack snapshot must include:

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

- one truthful Communication department-pack authority reconciled to H3
- one deterministic pack summary for outbound coordination, calendar handling, mailbox triage, and Teams collaboration administration
- fail-closed behavior for missing personas, invalid authorities, or mismatched action counts
- no over-claim of active or registry-backed coverage beyond the staged authoritative truth

## No-Go Conditions

- the pack fabricates personas not present in `registry/persona_registry_v2.yaml`
- a contract-only persona declares live supported actions
- the pack claims a planned persona is active or registry-backed
- the department-pack authority drifts from the staged H3 counts
