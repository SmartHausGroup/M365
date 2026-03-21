# M365 Communication Department Pack v1

## Purpose

Turn the runtime-real Communication persona into one bounded department-operable pack that can be
delegated to, governed, and measured as a single workforce unit.

## Problem

`E5A` through `E5E` made personas, delegation, queues, accountability, and memory real. `E2B`
made the communication workload surface real. But there was still no department-level contract that
said what Communication as a unit is allowed to do, which persona anchors that pack, how
outbound-communication approval works inside the department, and what state makes the Communication
pack ready versus blocked.

## Decision

`registry/department_pack_communication_v1.yaml` is now the authoritative Communication
department-pack contract.

The shared runtime is `src/smarthaus_common/department_pack.py`.

This act delivers the authority and proof surface for Communication on top of the shared runtime:

- the authoritative Communication pack authority in `registry/department_pack_communication_v1.yaml`
- the deterministic verifier in `scripts/ci/verify_communication_department_pack_v1.py`
- the generated proof in `configs/generated/communication_department_pack_v1_verification.json`

## Communication Pack Boundary

The Communication pack contains exactly one registry-backed persona:

- `outreach-coordinator`
  - David Park
  - outbound email, bulk email, scheduled communication, meetings, follow-up, and campaign launch

The pack may claim only that persona and its explicit action-backed workflows.

## Department Pack Contract

Every Communication pack snapshot must include:

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
  - the Communication persona is active and not escalated
- `watch`
  - the Communication persona has entered warning state but is not escalated
- `attention_required`
  - the Communication persona is escalated and the communication lead must intervene
- `blocked`
  - the Communication persona is missing, inactive, or outside the declared authority

## Runtime Rule

Department-pack state is projected, not hand-maintained.

That means:

- personas come from the authoritative persona registry
- the pack boundary comes from the department-pack authority file
- accountability comes from the shared persona-accountability runtime
- memory and work-history counts come from the shared persona-memory runtime
- pack status is derived deterministically from persona status and accountability state

## Required Guarantees

- one Communication department-pack authority
- one deterministic pack summary for the Communication workforce surface
- fail-closed behavior for missing personas, invalid authorities, or mismatched action counts
- deterministic department state derived from persona accountability and registry state
- bounded department claim that does not overstate unsupported communication or non-communication workflows

## No-Go Conditions

- the pack fabricates personas not in the authoritative registry
- supported action counts drift from the declared authority
- an inactive or missing Communication persona still yields `ready`
- the department pack claims website, finance, HR, or security work outside the explicit communication surface
