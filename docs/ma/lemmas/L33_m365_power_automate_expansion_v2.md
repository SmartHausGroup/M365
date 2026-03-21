# L33 — M365 Power Automate Expansion v2

## Claim

For `E3A` to be complete, the M365 pack must stop treating Power Automate as an external manual surface and instead expose a bounded, deterministic flow-administration workload through the v2 control plane.

`L33` holds only if:

1. the instruction API exposes the `E3A` Power Automate actions
2. the shared runtime can execute bounded Power Automate admin and callback-invocation behavior deterministically
3. the capability registry marks the `E3A` aliases as implemented
4. executor routing, auth, and approval risk all project those actions into the `powerplatform` domain deterministically
5. the active workforce-expansion plan advances from `E3A` to `E3B`

## Existing Proof Sources

- `plans/m365-ai-workforce-expansion-master-plan/m365-ai-workforce-expansion-master-plan.md`
- `docs/commercialization/m365-power-automate-expansion-v2.md`
- `registry/power_automate_expansion_v2.yaml`
- `registry/capability_registry.yaml`
- `registry/executor_routing_v2.yaml`
- `registry/auth_model_v2.yaml`
- `registry/approval_risk_matrix_v2.yaml`
- `docs/CAIO_M365_CONTRACT.md`
- `docs/contracts/caio-m365/ACTION_SPECIFICATION.md`
- `src/provisioning_api/routers/m365.py`
- `src/smarthaus_common/power_automate_client.py`
- `scripts/ci/verify_caio_m365_contract.py`
- `scripts/ci/verify_capability_registry.py`
- `scripts/ci/verify_power_automate_expansion.py`
- `tests/test_power_automate_expansion_v2.py`
- `notebooks/m365/INV-M365-AI-power-automate-expansion-v2.ipynb`
- `notebooks/lemma_proofs/L33_m365_power_automate_expansion_v2.ipynb`

## Acceptance Evidence

- instruction-schema and supported-action inventory include the `E3A` Power Automate actions
- the Power Automate runtime fails closed on missing admin modules or credentials and remains replay-stable for fixed mocked inputs
- capability-registry verification treats the `E3A` aliases as implemented
- Power Automate aliases resolve to the `powerplatform` executor with bounded app-only auth expectations
- the approval matrix marks read-only inventory actions as low-observe-create and lifecycle / invocation actions as high-impact
- the active plan and trackers advance from `E3A` to `E3B`

## Deterministic Surface

`PowerAutomateExpansionV2(action) = InstructionContract(action) ∧ CapabilityRegistry(action) ∧ Route(action)=powerplatform ∧ Auth(action)=app_only ∧ Approval(action)∈{low-observe-create, high-impact}`

`E3A_GO = PowerAutomateExpansionV2(all_supported_e3a_actions) ∧ TrackerAdvance(E3A, E3B)`
