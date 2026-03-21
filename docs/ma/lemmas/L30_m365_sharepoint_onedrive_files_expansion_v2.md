# L30 — M365 SharePoint / OneDrive / Files Expansion v2

## Claim

For `E2C` to be complete, SharePoint site content, SharePoint lists, OneDrive, and file operations must stop being split between hidden runtime handlers and a narrower public instruction surface.

`L30` holds only if:

1. the instruction API exposes the expanded SharePoint / OneDrive / files action set
2. the shared Graph client implements the required site, list, drive, and drive-item backing methods
3. the capability registry marks the expanded SharePoint / files aliases as implemented
4. executor routing, auth, and approval risk all project those actions into the `sharepoint` domain deterministically
5. the active workforce-expansion plan advances from `E2C` to `E2D`

## Existing Proof Sources

- `plans/m365-ai-workforce-expansion-master-plan/m365-ai-workforce-expansion-master-plan.md`
- `docs/commercialization/m365-sharepoint-onedrive-files-expansion-v2.md`
- `registry/sharepoint_onedrive_files_expansion_v2.yaml`
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
- `scripts/ci/verify_sharepoint_onedrive_files_expansion.py`
- `tests/test_sharepoint_onedrive_files_expansion_v2.py`
- `notebooks/m365/INV-M365-AF-sharepoint-onedrive-files-expansion-v2.ipynb`
- `notebooks/lemma_proofs/L30_m365_sharepoint_onedrive_files_expansion_v2.ipynb`

## Acceptance Evidence

- instruction-schema and supported-action inventory include the expanded SharePoint / files actions
- the shared Graph client covers the new site, list, drive, and drive-item contracts
- capability-registry verification treats the expanded SharePoint / files aliases as implemented
- SharePoint / files aliases resolve to the `sharepoint` executor with bounded auth expectations
- read surfaces stay low-risk while routine content mutations remain medium-operational
- the active plan and trackers advance from `E2C` to `E2D`

## Deterministic Surface

`SharePointOneDriveFilesExpansionV2(action) = InstructionContract(action) ∧ CapabilityRegistry(action) ∧ Route(action)=sharepoint ∧ Auth(action)=expected_auth(action) ∧ Approval(action)=expected_profile`

`E2C_GO = SharePointOneDriveFilesExpansionV2(all_supported_sharepoint_onedrive_files_actions) ∧ TrackerAdvance(E2C, E2D)`
