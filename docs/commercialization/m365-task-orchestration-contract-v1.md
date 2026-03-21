# M365 Task Orchestration Contract v1

## Purpose

Support composed multi-step work across workload and persona boundaries by defining
orchestration primitives, step dependency semantics, failure handling, and audit
requirements for multi-step task graphs.

## Problem

The delegation contract (E7A) defines how a single request flows through UCP. But many
real-world tasks require multiple steps across different personas and workloads. Without
an orchestration contract, composed tasks cannot be governed, audited, or fail-closed
deterministically.

## Decision

`registry/task_orchestration_contract_v1.yaml` is now the authoritative multi-step task
orchestration contract.

## Orchestration Primitives

1. **Sequential** — steps execute in order, stop on first failure
2. **Parallel** — independent steps execute concurrently, collect all results
3. **Conditional** — step executes only if predecessor condition is met
4. **Fallback** — if primary step fails, fallback step executes

## Step Contract

Every orchestration step must declare: step_id, persona_id, action_or_task, inputs,
outputs, and dependency_on. Steps transition through: pending, running, completed,
failed, skipped, blocked.

## Required Guarantees

- deterministic step ordering for fixed plans
- fail-closed on missing or unregistered personas
- per-step audit envelopes
- no implicit risk escalation in composed tasks

## No-Go Conditions

- an orchestration step bypasses the delegation contract
- a step references a persona not in the registry
- a composed task implicitly escalates risk beyond individual step tiers
- a step produces no audit envelope
