# L31 — M365 Teams / Groups / Planner Expansion v2

## Claim

For `E2D` to be complete, the first deeper Teams, channels, and Planner actions must stop being split between hidden runtime helpers and a narrower public instruction surface.

`L31` holds only if:

1. the instruction API exposes the expanded Teams / channels / Planner action set
2. the shared Graph client implements the required team, channel, plan, bucket, and task backing methods
3. the capability registry marks the expanded collaboration and Planner aliases as implemented
4. executor routing, auth, and approval risk all project those actions into the `collaboration` domain deterministically
5. the active workforce-expansion plan advances from `E2D` to `E2E`

## Existing Proof Sources

- `plans/m365-ai-workforce-expansion-master-plan/m365-ai-workforce-expansion-master-plan.md`
- `docs/commercialization/m365-teams-groups-planner-expansion-v2.md`
- `registry/teams_groups_planner_expansion_v2.yaml`
- `registry/capability_registry.yaml`
- `registry/executor_routing_v2.yaml`
- `registry/auth_model_v2.yaml`
- `registry/approval_risk_matrix_v2.yaml`
- `docs/CAIO_M365_CONTRACT.md`
- `docs/contracts/caio-m365/ACTION_SPECIFICATION.md`
- `src/provisioning_api/routers/m365.py`
- `src/smarthaus_graph/client.py`
- `scripts/ci/verify_caio_m365_contract.py`
- `scripts/ci/verify_capability_registry.py`
- `scripts/ci/verify_teams_groups_planner_expansion.py`
- `tests/test_teams_groups_planner_expansion_v2.py`
- `notebooks/m365/INV-M365-AG-teams-groups-planner-expansion-v2.ipynb`
- `notebooks/lemma_proofs/L31_m365_teams_groups_planner_expansion_v2.ipynb`

## Acceptance Evidence

- instruction-schema and supported-action inventory include the expanded collaboration / Planner actions
- the shared Graph client covers the new team, channel, plan, bucket, and task contracts
- capability-registry verification treats the expanded collaboration / Planner aliases as implemented
- collaboration / Planner aliases resolve to the `collaboration` executor with bounded auth expectations
- reads stay low-risk, channel creation remains high-impact, and Planner mutations remain medium-operational
- the active plan and trackers advance from `E2D` to `E2E`

## Deterministic Surface

`TeamsGroupsPlannerExpansionV2(action) = InstructionContract(action) ∧ CapabilityRegistry(action) ∧ Route(action)=collaboration ∧ Auth(action)=app_only ∧ Approval(action)=expected_profile`

`E2D_GO = TeamsGroupsPlannerExpansionV2(all_supported_e2d_actions) ∧ TrackerAdvance(E2D, E2E)`
