# L28 — M365 Entra / Directory Expansion v2

## Claim

For `E2A` to be complete, Entra and directory administration must stop being a split between legacy planned aliases and hidden runtime-only handlers.

`L28` holds only if:

1. the instruction API exposes the expanded Entra / directory action set
2. the Graph client implements the required backing methods
3. the capability registry marks the expanded legacy aliases as implemented
4. executor routing, auth, and approval risk all project those actions into the `directory` domain deterministically
5. the active workforce-expansion plan advances from `E2A` to `E2B`

## Existing Proof Sources

- `plans/m365-ai-workforce-expansion-master-plan/m365-ai-workforce-expansion-master-plan.md`
- `docs/commercialization/m365-entra-directory-expansion-v2.md`
- `registry/entra_directory_expansion_v2.yaml`
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
- `scripts/ci/verify_entra_directory_expansion.py`
- `tests/test_entra_directory_expansion_v2.py`
- `notebooks/m365/INV-M365-AD-entra-directory-expansion-v2.ipynb`
- `notebooks/lemma_proofs/L28_m365_entra_directory_expansion_v2.ipynb`

## Acceptance Evidence

- instruction-schema and supported-action inventory include the expanded directory actions
- Graph client covers the new actions with bounded request contracts
- capability-registry verification treats the expanded directory aliases as implemented
- directory aliases resolve to the `directory` executor with `app_only` auth
- high-impact mutations retain approval-bearing posture while read surfaces stay low-risk
- the active plan and trackers advance from `E2A` to `E2B`

## Deterministic Surface

`DirectoryExpansionV2(action) = InstructionContract(action) ∧ CapabilityRegistry(action) ∧ Route(action)=directory ∧ Auth(action)=app_only ∧ Approval(action)=expected_profile`

`E2A_GO = DirectoryExpansionV2(all_supported_directory_actions) ∧ TrackerAdvance(E2A, E2B)`
