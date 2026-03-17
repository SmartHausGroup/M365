# Phase 2 Calculus — M365 Contract Variables and Boundary Conditions

Plan refs: `plan:m365-ma-scorecard-alignment:R2`, `plan:m365-ma-scorecard-alignment:R5`

## Variables

- `a` — requested instruction action
- `p` — normalized parameter object
- `h` — request headers and auth context
- `i` — idempotency key
- `sigma` — tenant and runtime state
- `g` — governance flags such as mutation gate and audit enablement
- `r` — instruction response
- `q` — emitted audit record set

## Operators

- `normalize(a, p)` — request normalization as implemented by the instruction router
- `allow_mutation(g, a)` — mutating action gate
- `auth_ok(h)` — CAIO API key and session gate
- `hash(a, p)` — idempotency request hash
- `shape(r)` — response-shape check against the contract
- `audit(q)` — one-record-per-request audit emission

## Boundary Conditions

1. Unknown action is rejected fail-closed.
2. Missing required auth is rejected fail-closed.
3. Mutating actions remain blocked when mutation gating is disabled.
4. Idempotency replay returns the cached successful result for the same logical request.
5. Successful and unsuccessful executions both produce audit evidence under the audit invariant.

## Stability and Determinism

Within fixed repository state and fixed normalized inputs:

1. The supported action set is stable.
2. Contract verification artifacts are stable.
3. The response and audit contract is deterministic for the currently proven instruction surface.

The determinism bridge for governance alignment is rooted in:

- `notebooks/m365/INV-M365-C-001-determinism.ipynb`
- the stable intersection of contract, registry, and router action surfaces

## Lemma Mapping

- `L1` — response postcondition and result-shape compliance
- `L2` — idempotency replay stability
- `L3` — authentication fail-closed behavior
- `L4` — audit one-record-per-request behavior
- `L5` — deterministic action-surface and contract replay stability
