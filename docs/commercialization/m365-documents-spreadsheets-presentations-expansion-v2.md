# SMARTHAUS M365 Documents / Spreadsheets / Presentations Expansion v2

## Purpose

`E2E` turns Office productivity artifacts into a real instruction-api workload instead of leaving Word, Excel, and PowerPoint trapped behind raw file upload primitives.

## What E2E Closes

Before `E2E`, the M365 pack could upload arbitrary files into SharePoint or OneDrive drives, but it could not honestly claim a productivity workload. There was no deterministic document, workbook, or presentation contract on top of the v2 control plane.

`E2E` closes that gap by making the instruction API, shared Graph runtime, and the v2 registries agree on this bounded productivity surface:

- Documents
  - `create_document`
  - `update_document`
- Workbooks
  - `create_workbook`
  - `update_workbook`
- Presentations
  - `create_presentation`
  - `update_presentation`

## Deterministic Rule

`E2E_GO = InstructionApiExpanded ∧ OfficePayloadGenerationDeterministic ∧ GraphUploadBacked ∧ CapabilityRegistryImplemented ∧ SharePointRouteBounded ∧ AuthBounded ∧ ApprovalProfilesSynced`

## Auth Boundary

`E2E` keeps the bounded productivity surface on the existing `sharepoint` executor.

That is deliberate:

- Word, Excel, and PowerPoint artifacts are still file-backed in M365 drives
- it reuses the existing SharePoint / OneDrive executor split instead of inventing a premature `office` executor
- it allows delegated-self drive workflows when user context is implicit while preserving app-only site/group drive operation

## Runtime Projection

The expansion is projected through:

- instruction API surface
  - `src/provisioning_api/routers/m365.py`
- shared Graph runtime
  - `src/smarthaus_graph/client.py`
- deterministic Office payload generator
  - `src/smarthaus_common/office_generation.py`
- capability and workload authority
  - `registry/capability_registry.yaml`
  - `registry/documents_spreadsheets_presentations_expansion_v2.yaml`
- v2 control-plane alignment
  - `registry/executor_routing_v2.yaml`
  - `registry/auth_model_v2.yaml`
  - `registry/approval_risk_matrix_v2.yaml`
- contract and verification
  - `docs/CAIO_M365_CONTRACT.md`
  - `docs/contracts/caio-m365/ACTION_SPECIFICATION.md`
  - `scripts/ci/verify_caio_m365_contract.py`
  - `scripts/ci/verify_capability_registry.py`
  - `scripts/ci/verify_documents_spreadsheets_presentations_expansion.py`

## Result

After `E2E`, the M365 pack can honestly claim that the first productivity workflows are no longer just “upload a file.”

They are now:

- instruction-addressable
- deterministically generated
- graph-backed through the shared client
- capability-registered
- executor-routed to `sharepoint`
- auth-bounded to `hybrid`
- approval-profiled as medium-operational mutations

## Boundary

`E2E` is intentionally bounded:

- DOCX generation is text-first and deterministic
- XLSX generation is worksheet-and-cell focused
- PPTX generation is slide-title-and-bullet focused
- rich Office editing, comments, formulas, charts, collaborative cursors, and advanced formatting remain later acts

## Next Dependency

`E3A` is next. With the first productivity slice in place, the program can move into broader Power Platform expansion without pretending that document workflows are still missing from the M365 workload universe.
