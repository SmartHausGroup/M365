# M365 Studio Operations Department Pack v1

## Purpose

Turn the authoritative Studio Operations persona contract into one bounded department pack that can
be governed, delegated to, and measured against the final post-H5 source-branch authority while
preserving the certified `partial-activation` department taxonomy required by downstream certification.

## Problem

The shared runtime already enforced exact registry parity, but this department-pack authority still left 4 promoted personas staged as contract-only with zero actions. That stale contract layer blocked fresh M1 replay despite the authoritative registry already carrying the final post-H5 action surface.

## Decision

`registry/department_pack_studio_operations_v1.yaml` is the authoritative Studio Operations
department-pack contract and now explicitly reflects the final post-H5 source-branch authority.

The shared runtime remains `src/smarthaus_common/department_pack.py`.

This correction locks the following truth:

- total personas: `9`
- active personas: `9`
- registry-backed personas: `9`
- supported action count: `61`
- default pack state without queue pressure: `ready`
- preserved department status taxonomy: `partial-activation`

## Studio Operations Pack Boundary

The Studio Operations pack contains exactly `9` registry-backed personas:
- `analytics-reporter` — Amanda Foster (Data Scientist); registry-backed; actions=9
- `finance-tracker` — Lisa Chang (Chief Financial Officer); registry-backed; actions=8
- `infrastructure-maintainer` — Jennifer Liu (Site Reliability Engineer); registry-backed; actions=8
- `legal-compliance-checker` — Robert Kim (Legal Counsel); registry-backed; actions=8
- `support-responder` — Mike Rodriguez (Customer Success Manager); registry-backed; actions=8
- `client-relationship-agent` — Priya Mehta (Client Relationship Manager); registry-backed; actions=5
- `financial-operations-agent` — Luis Carvalho (Financial Operations Manager); registry-backed; actions=5
- `knowledge-management-agent` — Leah Goldstein (Knowledge Operations Lead); registry-backed; actions=5
- `reports` — Youssef Haddad (Reporting and KPI Analyst); registry-backed; actions=5

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

- one truthful Studio Operations department-pack authority reconciled to the post-H5 source-branch truth
- one deterministic ready-pack summary for the declared workflow families without queue pressure
- fail-closed behavior for missing personas, invalid authorities, or mismatched action counts
- no over-claim beyond the explicit registry-backed action surface
- preservation of the certified partial-activation department taxonomy for downstream certification compatibility

## No-Go Conditions

- the pack fabricates personas not present in registry/persona_registry_v2.yaml
- any promoted persona remains staged as contract-only after the authoritative registry marks it registry-backed
- supported action counts drift from the declared authority
- the department-pack authority drifts from the post-H5 source-branch truth or preserved taxonomy
