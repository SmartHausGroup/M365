# M365 Studio Operations Department Pack v1

## Purpose

Turn the authoritative Studio Operations persona contract into one bounded department pack that can
be governed, delegated to, and measured while the staged post-H3 roster remains fail-closed.

## Problem

H3 rebased the authoritative persona registry to `59` personas, but the studio-operations
department-pack contract still encoded pre-H3 counts. H4S corrects that scope gap so H4 can
resume certification/count rebase from truthful department-pack authority.

## Decision

`registry/department_pack_studio_operations_v1.yaml` is the authoritative Studio Operations
department-pack contract and now reconciles to the staged post-H3 authoritative roster.

The shared runtime remains `src/smarthaus_common/department_pack.py`.

This H4S rebase locks the following staged truth:

- total personas: `9`
- active personas: `5`
- registry-backed personas: `5`
- persona-contract-only personas: `4`
- supported action count: `41`
- pack state before later activation acts: `blocked`

## Studio Operations Pack Boundary

The Studio Operations pack now contains exactly `9` authoritative personas:
- `analytics-reporter` — Amanda Foster (Data Scientist); registry-backed; actions=9
- `client-relationship-agent` — Priya Mehta (Client Relationship Manager); persona-contract-only; actions=0
- `finance-tracker` — Lisa Chang (Chief Financial Officer); registry-backed; actions=8
- `financial-operations-agent` — Luis Carvalho (Financial Operations Manager); persona-contract-only; actions=0
- `infrastructure-maintainer` — Jennifer Liu (Site Reliability Engineer); registry-backed; actions=8
- `knowledge-management-agent` — Leah Goldstein (Knowledge Operations Lead); persona-contract-only; actions=0
- `legal-compliance-checker` — Robert Kim (Legal Counsel); registry-backed; actions=8
- `reports` — Youssef Haddad (Reporting and KPI Analyst); persona-contract-only; actions=0
- `support-responder` — Mike Rodriguez (Customer Success Manager); registry-backed; actions=8

Registry-backed execution coverage is limited to `analytics-reporter`, `finance-tracker`, `infrastructure-maintainer`, `legal-compliance-checker`, `support-responder`.

Persona-contract-only coverage is limited to `client-relationship-agent`, `financial-operations-agent`, `knowledge-management-agent`, `reports`.

Five studio-operations personas remain action-backed while four promoted personas stay contract-only.

## Department Pack Contract

Every Studio Operations pack snapshot must include:

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

- one truthful Studio Operations department-pack authority reconciled to H3
- one deterministic pack summary for reporting, finance controls, support coordination, knowledge operations, and client follow-through
- fail-closed behavior for missing personas, invalid authorities, or mismatched action counts
- no over-claim of active or registry-backed coverage beyond the staged authoritative truth

## No-Go Conditions

- the pack fabricates personas not present in `registry/persona_registry_v2.yaml`
- a contract-only persona declares live supported actions
- the pack claims a planned persona is active or registry-backed
- the department-pack authority drifts from the staged H3 counts
