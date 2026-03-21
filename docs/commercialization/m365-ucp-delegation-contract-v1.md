# M365 UCP Delegation Contract v1

## Purpose

Define the top-level delegation contract between Claude, UCP, and the workforce runtime
so that every Claude-originated request follows a deterministic path from natural language
intent through persona resolution, risk assessment, approval gating, executor routing, and
audited execution.

## Problem

Sections 0 through 6 built the persona registry, department packs, accountability, memory,
task queues, and the humanized delegation interface. But no single contract defines how
Claude delegates work through UCP to the workforce runtime end-to-end. Without this
contract, the delegation path is implicit and cannot be validated, audited, or governed
deterministically.

## Decision

`registry/ucp_delegation_contract_v1.yaml` is now the authoritative Claude-to-UCP
delegation contract.

The contract defines six ordered delegation phases: intent capture, persona resolution,
risk assessment, approval gating, executor routing, and audited execution. Each phase
has declared inputs, outputs, failure modes, and authority references.

## Delegation Phases

1. **Intent Capture** — Claude extracts structured delegation request from natural language
2. **Persona Resolution** — UCP resolves to specific persona using humanized delegation interface
3. **Risk Assessment** — UCP evaluates risk tier and approval requirements
4. **Approval Gating** — Routes through approval workflow if required
5. **Executor Routing** — Routes to correct executor domain; contract-only returns blocked
6. **Audited Execution** — Executor performs action; result wrapped in audit envelope

## Governance Rules

- **Fail Closed** — Any phase that cannot produce outputs must fail closed
- **Audit Completeness** — Every delegation attempt produces an audit envelope
- **Contract-Only Handling** — Contract-only personas return blocked at executor routing
- **Approval Integrity** — Approval decisions traceable to department pack authority
- **Idempotency** — Same request + same state = same routing and audit outcome

## Required Guarantees

- one authoritative delegation contract defining the end-to-end path
- deterministic phase ordering from intent through execution
- fail-closed behavior at every phase boundary
- contract-only personas handled explicitly rather than silently dropped
- audit envelope for every delegation attempt regardless of outcome

## No-Go Conditions

- a delegation request bypasses persona resolution
- a contract-only persona returns a successful execution result
- an approval-required action proceeds without approval
- a delegation attempt produces no audit envelope
- the delegation path is non-deterministic for fixed state
