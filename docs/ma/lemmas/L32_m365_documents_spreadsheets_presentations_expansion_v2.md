# L32 — M365 Documents / Spreadsheets / Presentations Expansion v2

## Claim

For `E2E` to be complete, the M365 pack must stop treating Word, Excel, and PowerPoint as generic uploads and instead expose a bounded, deterministic productivity workload through the v2 control plane.

`L32` holds only if:

1. the instruction API exposes the six document / workbook / presentation actions
2. the shared runtime can generate deterministic DOCX, XLSX, and PPTX payloads and upload them through Graph
3. the capability registry marks the six productivity aliases as implemented
4. executor routing, auth, and approval risk all project those actions into the `sharepoint` domain deterministically
5. the active workforce-expansion plan advances from `E2E` to `E3A`

## Existing Proof Sources

- `plans/m365-ai-workforce-expansion-master-plan/m365-ai-workforce-expansion-master-plan.md`
- `docs/commercialization/m365-documents-spreadsheets-presentations-expansion-v2.md`
- `registry/documents_spreadsheets_presentations_expansion_v2.yaml`
- `registry/capability_registry.yaml`
- `registry/executor_routing_v2.yaml`
- `registry/auth_model_v2.yaml`
- `registry/approval_risk_matrix_v2.yaml`
- `docs/CAIO_M365_CONTRACT.md`
- `docs/contracts/caio-m365/ACTION_SPECIFICATION.md`
- `src/provisioning_api/routers/m365.py`
- `src/smarthaus_common/office_generation.py`
- `src/smarthaus_graph/client.py`
- `scripts/ci/verify_caio_m365_contract.py`
- `scripts/ci/verify_capability_registry.py`
- `scripts/ci/verify_documents_spreadsheets_presentations_expansion.py`
- `tests/test_documents_spreadsheets_presentations_expansion_v2.py`
- `notebooks/m365/INV-M365-AH-documents-spreadsheets-presentations-expansion-v2.ipynb`
- `notebooks/lemma_proofs/L32_m365_documents_spreadsheets_presentations_expansion_v2.ipynb`

## Acceptance Evidence

- instruction-schema and supported-action inventory include the six productivity actions
- deterministic Office payload generation is replay-stable across repeated runs
- capability-registry verification treats the six productivity aliases as implemented
- productivity aliases resolve to the `sharepoint` executor with bounded hybrid auth expectations
- the approval matrix marks all six actions as medium-operational with no additional approval requirement
- the active plan and trackers advance from `E2E` to `E3A`

## Deterministic Surface

`DocumentsSpreadsheetsPresentationsExpansionV2(action) = InstructionContract(action) ∧ CapabilityRegistry(action) ∧ Route(action)=sharepoint ∧ Auth(action)=hybrid ∧ Approval(action)=medium-operational`

`E2E_GO = DocumentsSpreadsheetsPresentationsExpansionV2(all_supported_e2e_actions) ∧ TrackerAdvance(E2E, E3A)`
