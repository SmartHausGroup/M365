# L25 — M365 Auth Model v2

## Claim

For the SMARTHAUS workforce control plane to execute through bounded executors without auth drift:

1. one machine-readable auth authority must exist
2. each action must resolve to exactly one auth class
3. hybrid actions must choose delegated self-context only through explicit deterministic rules
4. runtime mail, calendar, chat, files, and drives handlers must consume the shared auth resolver
5. app-only admin and provisioning actions must remain app-only by default

If any condition fails, `E1D` and later workload-expansion phases inherit an unstable auth surface.

## Existing Proof Sources

- `Operations/NORTHSTAR.md`
- `plans/m365-ai-workforce-expansion-master-plan/m365-ai-workforce-expansion-master-plan.md`
- `registry/universal_action_contract_v2.yaml`
- `registry/executor_routing_v2.yaml`
- `registry/auth_model_v2.yaml`
- `docs/commercialization/m365-auth-model-v2.md`
- `src/smarthaus_common/auth_model.py`
- `src/ops_adapter/actions.py`
- `tests/test_auth_model_v2.py`
- `notebooks/m365/INV-M365-AA-auth-model-v2.ipynb`
- `notebooks/lemma_proofs/L25_m365_auth_model_v2.ipynb`

## Acceptance Evidence

- the auth registry defines deterministic executor-domain defaults plus exact and prefix overrides
- the shared auth resolver returns one auth class and delegated-preference decision per action
- user-context runtime handlers project hybrid actions through `/me` only when the auth model allows it
- current certified-core admin and provisioning actions remain `app_only`
- the active plan and trackers advance from `E1C` to `E1D`

## Deterministic Surface

`AuthModeV2(agent, action, params) = ExactPolicy(action) ∨ PrefixPolicy(action) ∨ DomainDefault(Route(agent, action))`

`HybridPreference = PreferDelegated iff auth_class ∈ {hybrid, mixed} ∧ ExplicitContextAbsent(params)`

`E1C_GO = SharedAuthAuthority ∧ DeterministicHybridPreference ∧ RuntimeProjection ∧ AppOnlyAdminDefault`
