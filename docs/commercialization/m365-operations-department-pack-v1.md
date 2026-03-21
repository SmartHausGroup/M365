# M365 Operations Department Pack v1

## Purpose

Turn the now-runtime-real Operations personas into one bounded department-operable pack that can be
delegated to, governed, and measured as a single workforce unit.

## Problem

`E5A` through `E5E` made personas, delegation, queues, accountability, and memory real. `E2A`
through `E2D` made the Operations workload surfaces real. But there was still no department-level
contract that said what the Operations team as a unit is allowed to do, which personas anchor that
pack, how approvals differ inside the department, and what state makes the department pack ready
versus blocked.

## Decision

`registry/department_pack_operations_v1.yaml` is now the authoritative Operations department-pack
contract.

The shared runtime is `src/smarthaus_common/department_pack.py`.

This act delivers the shared pack runtime and proof surface first:

- the authoritative Operations pack authority in `registry/department_pack_operations_v1.yaml`
- the shared runtime builder in `src/smarthaus_common/department_pack.py`
- the deterministic verifier in `scripts/ci/verify_operations_department_pack_v1.py`
- the generated proof in `configs/generated/operations_department_pack_v1_verification.json`

## Operations Pack Boundary

The Operations pack contains exactly two registry-backed personas:

- `m365-administrator`
  - Marcus Chen
  - identity, licensing, directory, workspace, and SharePoint administration
- `website-manager`
  - Elena Rodriguez
  - website publishing, deployment coordination, analytics, and SEO operations

The pack may claim only those personas and their explicit action-backed workflows.

## Department Pack Contract

Every Operations pack snapshot must include:

- department metadata
  - id
  - display name
  - wave and release track
  - department status
- workload and workflow families
- approval model
  - department owner
  - department lead
  - per-profile approver routing
- KPI contract
  - required personas
  - required active personas
  - required registry-backed personas
  - required workflow families
  - supported action count
- personas
  - persona context from the authoritative persona registry
  - accountability state
  - queue depth
  - memory count
  - work-history event count
- pack summary
  - persona counts
  - supported action count
  - workload-family count
  - workflow-family count
  - pack state

## Pack State Contract

- `ready`
  - every pack persona is active and no persona is escalated
- `watch`
  - at least one persona is in warning state and none are escalated
- `attention_required`
  - at least one persona is escalated and the department lead must intervene
- `blocked`
  - an expected persona is missing, inactive, or outside the declared authority

## Runtime Rule

Department-pack state is projected, not hand-maintained.

That means:

- personas come from the authoritative persona registry
- the pack boundary comes from the department-pack authority file
- accountability comes from the shared persona-accountability runtime
- memory and work-history counts come from the shared persona-memory runtime
- pack status is derived deterministically from persona status and accountability state

## Required Guarantees

- one Operations department-pack authority
- one deterministic pack summary across dashboard and persona runtime
- fail-closed behavior for missing personas, invalid authorities, or mismatched action counts
- deterministic department state derived from persona accountability and registry state
- bounded department claim that does not overstate unsupported personas or workflows

## No-Go Conditions

- the pack fabricates personas not in the authoritative registry
- supported action counts drift from the declared authority
- department runtime and dashboard disagree on pack state
- an inactive or missing Operations persona still yields `ready`
- the department pack claims other departments' responsibilities
