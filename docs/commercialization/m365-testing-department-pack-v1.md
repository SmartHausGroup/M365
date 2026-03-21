# M365 Testing Department Pack v1

## Purpose

Turn the authoritative Testing persona contract into one bounded department pack that can
be governed, delegated to, and measured even before the testing personas become
action-backed.

## Problem

`E5A` through `E5E` made personas, delegation, queues, accountability, and memory real. But the
Testing department still exists only as a set of contract-only personas with no
department-level surface saying which personas belong to Testing, what capability families
they own, how approval works when later activation arrives, and how the runtime should represent a
department that is planned but not yet executable.

## Decision

`registry/department_pack_testing_v1.yaml` is now the authoritative Testing
department-pack contract.

The shared runtime remains `src/smarthaus_common/department_pack.py`, and `E6I` uses the
generalized contract-only pack rules introduced under `E6D` so the Testing department can
be represented deterministically and fail closed as `blocked` instead of being omitted or
overclaimed.

## Testing Pack Boundary

The Testing pack contains exactly five authoritative personas:

- `api-tester`
- `performance-benchmarker`
- `test-results-analyzer`
- `tool-evaluator`
- `workflow-optimizer`

Every one of those personas is still `persona-contract-only`, so the pack may claim only the
contract boundary, capability families, approval posture, and blocked/planned state.

## Department Pack Contract

Every Testing pack snapshot must include:

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

Testing is not action-backed yet, so the runtime must represent that explicitly.

That means:

- contract-only personas may declare zero supported actions
- the pack still validates against the authoritative registry
- the pack state must resolve to `blocked` while the personas remain planned-only
- no department-level ready claim is allowed until later acts activate those personas

## Required Guarantees

- one Testing department-pack authority
- one deterministic blocked-state representation for contract-only Testing personas
- fail-closed behavior for missing personas, invalid authorities, or mismatched coverage/action claims
- bounded department claim that does not pretend Testing is live before later activation acts

## No-Go Conditions

- a contract-only Testing persona declares live supported actions
- the pack claims Testing is ready while all personas remain planned-only
- the pack omits authoritative Testing personas
- the pack silently drifts from the authoritative persona registry
