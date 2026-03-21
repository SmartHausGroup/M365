# M365 Cross-Persona Collaboration Contract v1

## Purpose

Allow digital employees to hand off, collaborate, and coordinate within governed bounds
by defining collaboration primitives, handoff semantics, accountability transfer rules,
and cross-department governance.

## Problem

The orchestration contract (E7C) supports multi-step tasks but does not define how
personas interact with each other — handoffs, consultations, co-execution, and
escalation. Without a collaboration contract, inter-persona coordination is implicit
and cannot be governed, audited, or fail-closed.

## Decision

`registry/cross_persona_collaboration_contract_v1.yaml` is now the authoritative
cross-persona collaboration contract.

## Collaboration Primitives

1. **Handoff** — transfer task with full context; accountability transfers
2. **Consultation** — request input without transferring ownership
3. **Co-execution** — concurrent execution with separate accountability
4. **Escalation** — escalate to higher-authority persona; accountability transfers

## Handoff Rules

- Full context required on every handoff
- Cross-department handoffs allowed but require dual department-owner approval
- Handoffs to contract-only personas accepted but resolve to blocked
- Every handoff creates a linked audit envelope

## Required Guarantees

- accountability continuity at every collaboration boundary
- no circular handoffs without justification
- risk tier enforcement at collaboration boundaries
- per-event audit envelopes

## No-Go Conditions

- a task exists without an accountable persona
- a handoff bypasses context or audit requirements
- a collaboration event exceeds risk tier without approval
- a collaboration event produces no audit envelope
