# Plan: M365 marketplace bundle packaging and conformance

## Section 1: Plan Header

- **Plan ID:** `plan:m365-marketplace-bundle-packaging-conformance`
- **Parent Plan ID:** `plan:m365-ucp-standalone-pack-surface`
- **Title:** `Package the M365 standalone pack as a conformant marketplace bundle`
- **Version:** `1.0`
- **Status:** `complete`
- **Owner:** `SMARTHAUS`
- **Date Created:** `2026-04-01`
- **Date Updated:** `2026-04-01`
- **North Star Ref:** `Operations/NORTHSTAR.md`
- **Execution Plan Ref:** `Operations/EXECUTION_PLAN.md § Initiative: M365 marketplace bundle packaging and conformance`
- **Domain:** `infrastructure`
- **Math/Algorithm Scope:** `false`

## Section 2: North Star Alignment

- **Source:** `Operations/NORTHSTAR.md`
- **Principles served:**
  - `truthful M365-owned pack distribution and release artifact boundaries`
  - `fail-closed marketplace trust, signature, and conformance posture`
  - `self-service packaging that does not require UCP repo authority drift`
- **Anti-alignment:**
  - `Does NOT redesign UCP-side Marketplace UI or lifecycle gating`
  - `Does NOT weaken service-mode auth or actor-identity rules`
  - `Does NOT claim bundle packaging is complete without a real bundle artifact`

## Section 3: Intent Capture

- **User's stated requirements:**
  - `real marketplace-installed M365 pack model`
  - `first do the formal plan per AGENTS.md rules process and governance`
  - `the M365 integration pack should be correctly packaged for the marketplace`
  - `ensure all prompts for the plans are following our formal prompt template`
- **Intent doc ref:** `captured in this plan`
- **Intent verification:** `R1` through `R7` capture the pack-side work required so M365 can emit a real marketplace bundle instead of only a runtime-owned source tree.

## Section 4: Objective

- **Objective:** package the standalone `ucp_m365_pack` surface in this repo as a conformant marketplace bundle that UCP can later consume as a real marketplace artifact.
- **Current state:** this repo owns the authoritative standalone UCP-facing pack source in `src/ucp_m365_pack/`, but there is no `manifest.json`, `payload.tar.gz`, signatures, evidence folder, or final `.ucp.tar.gz` bundle artifact.
- **Target state:** this repo produces a conformant marketplace bundle with manifest, payload, signatures, evidence, and one final bundle artifact that validates against the pack manifest and bundle specs.

## Section 5: Scope

### In scope (conceptual)

- define the canonical M365 marketplace bundle packaging contract
- build the concrete bundle structure for `ucp_m365_pack`
- emit manifest, payload, signatures, and evidence artifacts
- run conformance validation over the packaged artifact
- update commercialization and governance surfaces to truthfully describe the packaged bundle

### Out of scope (conceptual)

- sibling UCP repo install/UI consumption changes
- Microsoft tenant permission changes
- new M365 persona or Graph capability work
- commercial pricing or payout flows

### File allowlist (agent MAY touch these)

- `plans/m365-marketplace-bundle-packaging-conformance/**`
- `docs/prompts/codex-m365-marketplace-bundle-packaging-conformance.md`
- `docs/prompts/codex-m365-marketplace-bundle-packaging-conformance-prompt.txt`
- `notebooks/m365/INV-M365-BW-marketplace-bundle-packaging-governance-alignment.ipynb`
- `configs/generated/m365_marketplace_bundle_packaging_governance_alignment_verification.json`
- `src/ucp_m365_pack/**`
- `docs/commercialization/m365-marketplace-bundle-packaging.md`
- `docs/commercialization/USER_MANUAL_M365.md`
- `artifacts/diagnostics/m365_marketplace_bundle_packaging_conformance.json`
- `dist/m365_pack/**`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist (agent MUST NOT touch these)

- `../UCP/**`
- `registry/**` except read-only inspection
- `Any path not listed in the allowlist`

### Scope fence rule

Agent must STOP and re-scope if the packaging work requires UCP-side Marketplace/UI changes or files outside the allowlist.

## Section 6: Requirements

- **R1 — Canonical packaging contract**
  - One governed package must define the M365 bundle structure, pack identity, compatibility, entitlement, and evidence expectations.
- **R2 — Concrete manifest**
  - A real `manifest.json` conforming to the pack manifest schema must exist for the M365 pack bundle.
- **R3 — Self-contained payload**
  - A real `payload.tar.gz` must contain the standalone `ucp_m365_pack` runtime surface and required setup assets.
- **R4 — Trust material**
  - The bundle must include signatures and evidence artifacts required by the bundle spec.
- **R5 — Final distributable bundle**
  - One final `.ucp.tar.gz` artifact must be produced for the M365 pack.
- **R6 — Conformance proof**
  - The packaged artifact must validate against the declared contract and fail closed when incomplete.
- **R7 — Clean governance closure**
  - Plan, prompt, action log, execution plan, and project file index must be synchronized truthfully.

## Section 7: Execution Sequence

- `T1 -> T2 -> T3 -> T4 -> T5 -> T6`
- Stop on first red.

## Section 8: Tasks

- **T1 — Lock the packaging contract**
  - Publish the governed package, prompt pair, notebook evidence, and commercialization note for the bundle boundary.
- **T2 — Build manifest and payload**
  - Create the concrete `manifest.json`, `payload.tar.gz`, and bundle-layout source tree for `ucp_m365_pack`.
- **T3 — Add signatures and evidence**
  - Create `signatures/` and `evidence/` artifacts required by the spec.
- **T4 — Assemble the final `.ucp.tar.gz`**
  - Produce the final distributable marketplace bundle artifact.
- **T5 — Run conformance validation**
  - Validate the packaged artifact and capture diagnostic proof.
- **T6 — Close governance truthfully**
  - Synchronize `Operations/ACTION_LOG.md`, `Operations/EXECUTION_PLAN.md`, and `Operations/PROJECT_FILE_INDEX.md`.

## Section 9: Gates

- **CHECK:C0 — Packaging contract explicit**
  - The package must explicitly define manifest, payload, signatures, evidence, and final bundle identity.
- **CHECK:C1 — Concrete artifact surfaces exist**
  - `manifest.json`, `payload.tar.gz`, and the final bundle path must exist when executed.
- **CHECK:C2 — Trust and evidence material present**
  - signatures and evidence artifacts exist and are referenced truthfully.
- **CHECK:C3 — Conformance validation green**
  - the packaged artifact validates or the phase fails closed with explicit reasons.
- **CHECK:C4 — Diff hygiene**
  - `git diff --check` must pass.

## Section 10: Determinism Requirements

- `N/A — this phase is packaging/conformance work, not math/algorithm work. Determinism is enforced through fixed artifact generation, declared digests, and conformance validation.`

## Section 11: Artifacts

- `plans/m365-marketplace-bundle-packaging-conformance/m365-marketplace-bundle-packaging-conformance.md`
- `plans/m365-marketplace-bundle-packaging-conformance/m365-marketplace-bundle-packaging-conformance.yaml`
- `plans/m365-marketplace-bundle-packaging-conformance/m365-marketplace-bundle-packaging-conformance.json`
- `docs/prompts/codex-m365-marketplace-bundle-packaging-conformance.md`
- `docs/prompts/codex-m365-marketplace-bundle-packaging-conformance-prompt.txt`
- `notebooks/m365/INV-M365-BW-marketplace-bundle-packaging-governance-alignment.ipynb`
- `configs/generated/m365_marketplace_bundle_packaging_governance_alignment_verification.json`

## Section 12: Environment

- **Python version:** `3.14.3`
- **Venv:** `.venv/bin/python`
- **Additional dependencies:**
  - `pyyaml`
  - `jsonschema`
- **Hardware:** `N/A — local developer workstation`
- **External data:**
  - `none required for draft planning`
- **Pre-notebook check:** `Notebook evidence is governance-only for this draft slice.`

## Section 13: Implementation Approach

- **Option A:** keep the standalone source tree and let UCP continue installing from transitional owner-repo seed materialization.
  - **Pros:** no pack-side packaging work
  - **Cons:** not a conformant marketplace bundle; cannot honestly satisfy the spec-defined install model
- **Option B:** package the standalone M365 pack as a real marketplace bundle with manifest, payload, signatures, evidence, and final distributable artifact.
  - **Pros:** matches the declared bundle/manifest specs and becomes the correct source-of-truth for UCP consumption
  - **Cons:** requires real packaging and conformance work
- **Chosen:** `Option B`
- **Rationale:** the runtime source surface already exists; the missing boundary is the distributable bundle artifact, not another runtime refactor.
- **Rejected rationale:** `Option A` preserves the wrong distribution model.
- **ADR ref:** `N/A`

## Section 14: Risks and Mitigations

- **Risk:** the standalone runtime surface may still depend on UCP-internal assumptions that are not captured in a self-contained payload.
  - **Impact:** `high`
  - **Mitigation:** make bundle conformance fail closed and inventory any remaining host dependencies explicitly.
  - **Status:** `open`
- **Risk:** packaging work could stop at documentation instead of producing a real bundle artifact.
  - **Impact:** `high`
  - **Mitigation:** require concrete manifest/payload/signatures/evidence/final bundle outputs in the requirements and gates.
  - **Status:** `open`
- **Risk:** trust material could be implied rather than generated.
  - **Impact:** `high`
  - **Mitigation:** require concrete signatures and evidence artifacts in the bundle structure.
  - **Status:** `open`
- **Hard blockers:** `none currently`

## Section 15: Rollback

- **Procedure:**
  - revert only the bounded packaging/conformance files in the allowlist
  - remove the generated bundle artifacts if the slice is withdrawn
  - update governance trackers to remove the draft workstream truthfully
- **Files to revert:**
  - `plans/m365-marketplace-bundle-packaging-conformance/m365-marketplace-bundle-packaging-conformance.md`
  - `plans/m365-marketplace-bundle-packaging-conformance/m365-marketplace-bundle-packaging-conformance.yaml`
  - `plans/m365-marketplace-bundle-packaging-conformance/m365-marketplace-bundle-packaging-conformance.json`
  - `docs/prompts/codex-m365-marketplace-bundle-packaging-conformance.md`
  - `docs/prompts/codex-m365-marketplace-bundle-packaging-conformance-prompt.txt`
  - `notebooks/m365/INV-M365-BW-marketplace-bundle-packaging-governance-alignment.ipynb`
  - `configs/generated/m365_marketplace_bundle_packaging_governance_alignment_verification.json`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
- **Artifacts to delete:**
  - `configs/generated/m365_marketplace_bundle_packaging_governance_alignment_verification.json`
- **Governance updates on rollback:**
  - `Operations/ACTION_LOG.md`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/PROJECT_FILE_INDEX.md`

## Section 16: Prompt References

- **MATHS template:** `../UCP/agent_governance/master-maths-prompt-template.md`
- **Prompt doc:** `docs/prompts/codex-m365-marketplace-bundle-packaging-conformance.md`
- **Prompt kickoff:** `docs/prompts/codex-m365-marketplace-bundle-packaging-conformance-prompt.txt`
- **Per-task prompts:** `N/A`

## Section 17: Traceability

- `plan:m365-marketplace-bundle-packaging-conformance:R1` -> governed packaging contract
- `plan:m365-marketplace-bundle-packaging-conformance:R2` -> concrete manifest surface
- `plan:m365-marketplace-bundle-packaging-conformance:R3` -> self-contained payload archive
- `plan:m365-marketplace-bundle-packaging-conformance:R4` -> signatures and evidence material
- `plan:m365-marketplace-bundle-packaging-conformance:R5` -> final distributable bundle
- `plan:m365-marketplace-bundle-packaging-conformance:R6` -> conformance proof
- `plan:m365-marketplace-bundle-packaging-conformance:R7` -> governance synchronization

## Section 18: Governance Closure

- [x] `Operations/ACTION_LOG.md` updated
- [x] `Operations/EXECUTION_PLAN.md` updated
- [x] `Operations/PROJECT_FILE_INDEX.md` updated
- [x] Plan artifacts synchronized (`.md/.yaml/.json`)
- [x] Phase status updated truthfully

## Section 19: Execution Outcome

- **Task checklist:**
  - `T1 complete` — governed plan/prompt package, notebook-backed governance evidence, and commercialization boundary docs published.
  - `T2 complete` — concrete `manifest.json`, `payload.tar.gz`, and bundled setup/runtime payload created under `dist/m365_pack/`.
  - `T3 complete` — signature metadata and evidence artifacts created under `dist/m365_pack/signatures/` and `dist/m365_pack/evidence/`.
  - `T4 complete` — final distributable `com.smarthaus.m365-1.0.0.ucp.tar.gz` assembled.
  - `T5 complete` — conformance proof captured in `artifacts/diagnostics/m365_marketplace_bundle_packaging_conformance.json`.
  - `T6 complete` — governance trackers and project file index synchronized truthfully.
- **Gate checklist:**
  - `CHECK:C0 pass`
  - `CHECK:C1 pass`
  - `CHECK:C2 pass`
  - `CHECK:C3 pass`
  - `CHECK:C4 pass`
- **Final decision:** `GO`
- **Completion timestamp:** `2026-04-01 13:34:53 EDT`
