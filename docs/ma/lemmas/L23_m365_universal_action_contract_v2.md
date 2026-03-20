# L23 — M365 Universal Action Contract v2

## Claim

For the SMARTHAUS workforce control plane to expand beyond the bounded standalone slice, the action surface is admissible iff:

1. one canonical action key exists for all future actions
2. legacy CAIO, capability-registry, and agent-registry names are treated as aliases, not authorities
3. every action definition carries identity, semantics, execution, governance, and evidence fields
4. the request and response envelopes preserve action identity and control-plane metadata
5. later phases use the v2 contract instead of inventing workload-local schemas

If any of those conditions fails, the workforce remains fragmented into incompatible action surfaces and `E1` cannot proceed deterministically.

## Existing Proof Sources

- `Operations/NORTHSTAR.md`
- `plans/m365-ai-workforce-expansion-master-plan/m365-ai-workforce-expansion-master-plan.md`
- `docs/CAIO_M365_CONTRACT.md`
- `docs/contracts/caio-m365/ACTION_SPECIFICATION.md`
- `registry/capability_registry.yaml`
- `registry/agents.yaml`
- `registry/universal_action_contract_v2.yaml`
- `docs/commercialization/m365-universal-action-contract-v2.md`
- `notebooks/m365/INV-M365-Y-universal-action-contract-v2.ipynb`
- `notebooks/lemma_proofs/L23_m365_universal_action_contract_v2.ipynb`

## Acceptance Evidence

- the machine-readable contract defines canonical naming, envelopes, projection rules, and minimum action-definition fields
- the human-readable contract explains the three current action dialects and how they project into v2
- the active plan and trackers advance from `E1A` to `E1B`
- no later `E1` act needs to invent a new action-language surface

## Deterministic Surface

`ActionV2 = Identity × Semantics × Execution × Governance × Evidence`

`CanonicalAction = executor_domain.resource.operation`

`LegacyAliasResolution = CAIOAlias ∨ CapabilityRegistryAlias ∨ AgentRegistryAlias`

`E1A_GO = CanonicalActionDefined ∧ EnvelopeDefined ∧ AliasProjectionDefined`
