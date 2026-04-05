# M365 Operations Department Pack v1

## Purpose

Turn the authoritative Operations persona contract into one bounded department pack that can
be governed, delegated to, and measured while the staged post-H3 roster remains fail-closed.

## Problem

H3 rebased the authoritative persona registry to `59` personas, but the operations
department-pack contract still encoded pre-H3 counts. H4S corrects that scope gap so H4 can
resume certification/count rebase from truthful department-pack authority.

## Decision

`registry/department_pack_operations_v1.yaml` is the authoritative Operations
department-pack contract and now reconciles to the staged post-H3 authoritative roster.

The shared runtime remains `src/smarthaus_common/department_pack.py`.

This H4S rebase locks the following staged truth:

- total personas: `10`
- active personas: `2`
- registry-backed personas: `2`
- persona-contract-only personas: `8`
- supported action count: `43`
- pack state before later activation acts: `blocked`

## Operations Pack Boundary

The Operations pack now contains exactly `10` authoritative personas:
- `audit-operations` — Naomi Brooks (Audit Operations Lead); persona-contract-only; actions=0
- `compliance-monitoring-agent` — Farah Alvi (Compliance Monitoring Lead); persona-contract-only; actions=0
- `device-management` — Connor Walsh (Endpoint Operations Administrator); persona-contract-only; actions=0
- `identity-security` — Amara Okoye (Identity Security Administrator); persona-contract-only; actions=0
- `it-operations-manager` — Peter Novak (IT Operations Manager); persona-contract-only; actions=0
- `m365-administrator` — Marcus Chen (Senior IT Administrator); registry-backed; actions=37
- `security-operations` — Tunde Adeyemi (Security Operations Lead); persona-contract-only; actions=0
- `service-health` — Chloe Martin (Service Reliability Coordinator); persona-contract-only; actions=0
- `ucp-administrator` — Omar El-Masry (UCP Control Plane Administrator); persona-contract-only; actions=0
- `website-manager` — Elena Rodriguez (Website Manager); registry-backed; actions=6

Registry-backed execution coverage is limited to `m365-administrator`, `website-manager`.

Persona-contract-only coverage is limited to `audit-operations`, `compliance-monitoring-agent`, `device-management`, `identity-security`, `it-operations-manager`, `security-operations`, `service-health`, `ucp-administrator`.

Marcus Chen and Elena Rodriguez remain the only action-backed Operations anchors in the staged model.

## Department Pack Contract

Every Operations pack snapshot must include:

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

- one truthful Operations department-pack authority reconciled to H3
- one deterministic pack summary for tenant operations, security/compliance monitoring, audit review, device oversight, and website operations
- fail-closed behavior for missing personas, invalid authorities, or mismatched action counts
- no over-claim of active or registry-backed coverage beyond the staged authoritative truth

## No-Go Conditions

- the pack fabricates personas not present in `registry/persona_registry_v2.yaml`
- a contract-only persona declares live supported actions
- the pack claims a planned persona is active or registry-backed
- the department-pack authority drifts from the staged H3 counts
