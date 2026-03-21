# M365 Studio Operations Department Pack v1

## Purpose

Turn the authoritative Studio Operations persona contract into one bounded department pack that can
be governed, delegated to, and measured even before the studio-operations personas become
action-backed.

## Problem

`E5A` through `E5E` made personas, delegation, queues, accountability, and memory real. But the
Studio Operations department still exists only as a set of contract-only personas with no
department-level surface saying which personas belong to Studio Operations, what capability families
they own, how approval works when later activation arrives, and how the runtime should represent a
department that is planned but not yet executable.

## Decision

`registry/department_pack_studio_operations_v1.yaml` is now the authoritative Studio Operations
department-pack contract.

The shared runtime remains `src/smarthaus_common/department_pack.py`, and `E6H` uses the
generalized contract-only pack rules introduced under `E6D` so the Studio Operations department can
be represented deterministically and fail closed as `blocked` instead of being omitted or
overclaimed.

## Studio Operations Pack Boundary

The Studio Operations pack contains exactly five authoritative personas:

- `analytics-reporter`
- `finance-tracker`
- `infrastructure-maintainer`
- `legal-compliance-checker`
- `support-responder`

Every one of those personas is still `persona-contract-only`, so the pack may claim only the
contract boundary, capability families, approval posture, and blocked/planned state.

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

## Contract-Only Runtime Rule

Studio Operations is not action-backed yet, so the runtime must represent that explicitly.

That means:

- contract-only personas may declare zero supported actions
- the pack still validates against the authoritative registry
- the pack state must resolve to `blocked` while the personas remain planned-only
- no department-level ready claim is allowed until later acts activate those personas

## Required Guarantees

- one Studio Operations department-pack authority
- one deterministic blocked-state representation for contract-only Studio Operations personas
- fail-closed behavior for missing personas, invalid authorities, or mismatched coverage/action claims
- bounded department claim that does not pretend Studio Operations is live before later activation acts

## No-Go Conditions

- a contract-only Studio Operations persona declares live supported actions
- the pack claims Studio Operations is ready while all personas remain planned-only
- the pack omits authoritative Studio Operations personas
- the pack silently drifts from the authoritative persona registry
