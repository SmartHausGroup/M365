# M365 Persona Accountability v1

## Purpose

Define the deterministic KPI, ownership, accountability, and escalation contract for SMARTHAUS
digital employees.

## Problem

`E5C` gave the workforce a shared task queue and persona-state projection, but it did not yet bind
that runtime to accountable ownership, bounded queue thresholds, or deterministic escalation
targets. The dashboard and persona runtime could show work volume without showing who owns the
result or when the queue must escalate.

## Decision

`registry/persona_accountability_v1.yaml` is now the authoritative accountability contract for the
digital-employee runtime.

The shared runtime is `src/smarthaus_common/persona_accountability.py`.

The same accountability snapshot now projects into:

- the dashboard status and performance surfaces in `src/provisioning_api/routers/agent_dashboard.py`
- the governed persona state and accountability surfaces in `src/ops_adapter/main.py`
- the legacy-aligned persona state and accountability surfaces in `src/ops_adapter/app.py`

## Accountability Contract

Every persona accountability snapshot must include:

- ownership
  - department
  - title
  - manager
  - escalation owner
  - approval owner
  - persona status
  - coverage status
- thresholds
  - target queue depth
  - max queue depth
  - max open tasks
  - blocked-task threshold
  - failed-task threshold
- metrics
  - queue depth
  - open task count
  - queued tasks
  - in-progress tasks
  - blocked tasks
  - failed tasks
  - completed tasks
  - total tasks
  - queued instructions
  - completion ratio
- escalation
  - required or not
  - target role
  - target
  - reasons

## Accountability State Contract

- `on_track`
  - queue and work posture are within the approved operating envelope
- `warning`
  - queue depth has reached the target operating envelope and requires managerial attention
- `escalated`
  - queue, blocked work, or failed work breached the operating envelope and must escalate

## Runtime Rule

Accountability is projected, not manually edited.

That means:

- ownership comes from the authoritative persona registry
- thresholds come from the accountability authority file
- KPI metrics come from the shared queue runtime
- escalation targets follow the declared target-order rule
- blocked and failed work breach the envelope deterministically

## Required Guarantees

- one accountability authority across dashboard and persona runtime
- one deterministic ownership and threshold projection per canonical persona
- fail-closed behavior for unknown personas or invalid authority files
- deterministic escalation targeting from the declared owner precedence
- deterministic warning/escalation state derived from queue metrics and thresholds

## No-Go Conditions

- dashboard and persona runtime disagree on accountability state
- escalation targets are inferred ad hoc instead of from the declared order
- blocked or failed work bypasses the accountability contract
- unknown personas silently receive fabricated ownership or thresholds
