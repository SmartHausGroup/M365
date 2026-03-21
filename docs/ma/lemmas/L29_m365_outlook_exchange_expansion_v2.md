# L29 — M365 Outlook / Exchange Expansion v2

## Claim

For `E2B` to be complete, Outlook / Exchange operations must stop being split between hidden runtime handlers and a narrower public instruction surface.

`L29` holds only if:

1. the instruction API exposes the expanded Outlook / Exchange action set
2. the shared Graph client implements the required mail, calendar, mailbox, and contact backing methods
3. the capability registry marks the expanded messaging aliases as implemented
4. executor routing, auth, and approval risk all project those actions into the `messaging` domain deterministically
5. the active workforce-expansion plan advances from `E2B` to `E2C`

## Existing Proof Sources

- `plans/m365-ai-workforce-expansion-master-plan/m365-ai-workforce-expansion-master-plan.md`
- `docs/commercialization/m365-outlook-exchange-expansion-v2.md`
- `registry/outlook_exchange_expansion_v2.yaml`
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
- `scripts/ci/verify_outlook_exchange_expansion.py`
- `tests/test_outlook_exchange_expansion_v2.py`
- `notebooks/m365/INV-M365-AE-outlook-exchange-expansion-v2.ipynb`
- `notebooks/lemma_proofs/L29_m365_outlook_exchange_expansion_v2.ipynb`

## Acceptance Evidence

- instruction-schema and supported-action inventory include the expanded messaging actions
- the shared Graph client covers the new mail, calendar, mailbox, and contact contracts
- capability-registry verification treats the expanded messaging aliases as implemented
- messaging aliases resolve to the `messaging` executor with `hybrid` auth
- read surfaces stay low-risk while routine mailbox mutations remain medium-operational
- the active plan and trackers advance from `E2B` to `E2C`

## Deterministic Surface

`OutlookExchangeExpansionV2(action) = InstructionContract(action) ∧ CapabilityRegistry(action) ∧ Route(action)=messaging ∧ Auth(action)=hybrid ∧ Approval(action)=expected_profile`

`E2B_GO = OutlookExchangeExpansionV2(all_supported_outlook_exchange_actions) ∧ TrackerAdvance(E2B, E2C)`
