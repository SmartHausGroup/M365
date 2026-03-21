# L24 — M365 Executor Routing v2

## Claim

For the SMARTHAUS workforce control plane to execute through bounded executors deterministically:

1. one machine-readable routing authority must exist
2. canonical v2 actions must route from their executor-domain segment directly
3. legacy CAIO, capability-registry, and agent-registry actions must resolve through explicit alias rules
4. ops-adapter routing, persona-domain derivation, and instruction-router projection must use the same resolver
5. unknown actions must fail closed instead of silently falling back

If any condition fails, executor selection remains fragmented and `E1C` through `E1E` inherit an unstable routing surface.

## Existing Proof Sources

- `Operations/NORTHSTAR.md`
- `plans/m365-ai-workforce-expansion-master-plan/m365-ai-workforce-expansion-master-plan.md`
- `registry/universal_action_contract_v2.yaml`
- `registry/executor_routing_v2.yaml`
- `docs/commercialization/m365-executor-routing-v2.md`
- `src/smarthaus_common/executor_routing.py`
- `src/ops_adapter/actions.py`
- `src/ops_adapter/personas.py`
- `src/provisioning_api/routers/m365.py`
- `tests/test_executor_routing_v2.py`
- `tests/test_env_loading.py`
- `notebooks/m365/INV-M365-Z-executor-routing-v2.ipynb`
- `notebooks/lemma_proofs/L24_m365_executor_routing_v2.ipynb`

## Acceptance Evidence

- the routing registry defines canonical domains, exact aliases, dotted-prefix aliases, and agent-specific overrides
- the shared resolver projects canonical and legacy actions into one executor-domain result
- ops-adapter, persona derivation, and the instruction router all use the same resolver
- unknown actions fail closed
- the active plan and trackers advance from `E1B` to `E1C`

## Deterministic Surface

`ExecutorRouteV2(agent, action) = Override(agent, action) ∨ Canonical(action) ∨ ExactAlias(action) ∨ PrefixAlias(action)`

`E1B_GO = SharedRoutingAuthority ∧ CanonicalProjection ∧ LegacyAliasProjection ∧ FailClosedUnknowns`
