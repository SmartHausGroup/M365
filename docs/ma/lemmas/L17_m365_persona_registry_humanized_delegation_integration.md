# Lemma L17 — Persona Registry and Humanized Delegation Integration

## Claim

The governed runtime can expose named digital employees as the delegation
surface without exposing raw agent identifiers if:

1. persona lookup resolves deterministically from stable aliases;
2. each persona maps to exactly one canonical runtime agent;
3. persona status and allowed executor domains are enforced before execution;
4. persona context is preserved through approval and audit payloads; and
5. unknown or inactive personas fail closed.

## Why This Matters

`B7C` is the runtime act that turns the digital-employee architecture from
`B6A` through `B6E` into an operator-facing execution contract. Without
persona-aware routing, the runtime still exposes raw agent mechanics even if
the documentation says otherwise.

## Inputs

- `registry/agents.yaml`
- `registry/ai_team.json`
- governed persona target supplied by the caller
- agent action request and bounded executor routing metadata

## Outputs

- deterministic persona registry
- stable alias-to-agent resolution
- fail-closed persona responsibility enforcement
- persona-aware approval and audit payloads

## Proof Sketch

If persona records are derived deterministically from the existing team and
agent registries, then the runtime can resolve display names, slugs, and
canonical agent ids to one active persona record. If the resolved persona is
inactive, unknown, or not permitted for the requested executor domain, the
runtime can deny the request before mutation, approval creation, or audit
emission. If the resolved persona is preserved in params, approvals, and audit
payloads, then operators interact with named digital employees while the
runtime still enforces bounded executor semantics.

## Runtime Bindings

- `src/ops_adapter/personas.py`
- `src/ops_adapter/main.py`
- `src/ops_adapter/app.py`
- `src/ops_adapter/approvals.py`
- `tests/test_ops_adapter.py`
- `tests/test_approvals.py`

## Failure Boundary

`B7C` fails closed if:

- persona aliases resolve ambiguously or non-deterministically;
- inactive or unknown personas can execute governed actions;
- persona domain boundaries are not enforced; or
- approvals and audit logs drop persona context.
