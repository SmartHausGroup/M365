# Lemma L16 — Runtime Executor Routing and Domain Selection

## Claim

The governed runtime can route each supported action to exactly one bounded
executor domain while preserving actor-based approval and audit semantics if:

1. action-to-domain selection is deterministic;
2. tenant routing metadata resolves that domain to exactly one executor;
3. unknown or unmapped routes fail closed; and
4. the approvals backend is bound explicitly to the SharePoint executor path.

## Why This Matters

`B7B` is the first runtime act after the tenant-contract extension in `B7A`.
The rebased multi-executor target is not real until governed actions select one
bounded executor instead of silently falling back to the legacy giant executor.

## Inputs

- governed agent/action pair
- tenant executor registry metadata
- bounded executor definitions
- approval-path route requirement

## Outputs

- deterministic action-to-domain mapping
- fail-closed route resolution
- executor identity preserved in action, approval, and audit payloads
- SharePoint approval backend pinned to the SharePoint executor path

## Proof Sketch

If the runtime first maps `(agent, action)` to one route key, then resolves
that route key to one executor using tenant metadata, then projects that
executor into the Graph token path and audit payloads, every action has a
single bounded executor identity. If resolution fails, the runtime can halt
before mutation or approval creation, preserving fail-closed behavior.

## Runtime Bindings

- `src/smarthaus_common/tenant_config.py`
- `src/ops_adapter/actions.py`
- `src/ops_adapter/main.py`
- `src/ops_adapter/app.py`
- `src/ops_adapter/approvals.py`
- `tests/test_ops_adapter.py`
- `tests/test_approvals.py`

## Failure Boundary

`B7B` fails closed if:

- a supported action does not resolve to exactly one executor domain;
- multi-executor tenants silently fall back to the wrong executor;
- the approvals backend does not bind to the SharePoint executor path; or
- actor/executor audit semantics are lost during routing.
