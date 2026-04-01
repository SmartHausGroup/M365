# Execution Prompt — MATHS Workstream (Governance Locked)

Plan Reference: `plan:m365-marketplace-bundle-packaging-conformance`
Parent Plan: `plan:m365-ucp-standalone-pack-surface`
North Star: `Operations/NORTHSTAR.md`
Execution Plan: `Operations/EXECUTION_PLAN.md`
Prompt Template: `../UCP/agent_governance/master-maths-prompt-template.md`
North Star Reference: `docs/NORTH_STAR.md` and `Operations/NORTHSTAR.md`
Execution Plan Reference: `docs/platform/EXECUTION_PLAN.md` and `Operations/EXECUTION_PLAN.md`

**Mission:** package the standalone `ucp_m365_pack` surface in this repo as a real marketplace bundle with manifest, payload, signatures, evidence, and one final distributable `.ucp.tar.gz` artifact, without drifting into sibling UCP consumption work.

This prompt uses the canonical master MATHS prompt template as the formal execution scaffold for the M365-side packaging and conformance workstream.

## Model Configuration (for prompt runner)

- Set temperature to `0`.
- Set `top_p` to `1.0`.
- Use precise or deterministic settings when available.

## Governance Lock (Mandatory)

Before any write, test, or command:

1. Read:
- `AGENTS.md`
- applicable `.cursor/rules/**/*.mdc`
- `Operations/NORTHSTAR.md`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`
- `plans/m365-marketplace-bundle-packaging-conformance/m365-marketplace-bundle-packaging-conformance.md`
- `plans/m365-marketplace-bundle-packaging-conformance/m365-marketplace-bundle-packaging-conformance.yaml`
- `../UCP/agent_governance/master-maths-prompt-template.md`
- `src/ucp_m365_pack/contracts.py`
- `src/ucp_m365_pack/client.py`
- `../UCP/docs/platform/PACK_BUNDLE_SPEC_V0_1.md`
- `../UCP/docs/platform/PACK_MANIFEST_SCHEMA_V0_1.md`

2. Verify alignment + plan linkage:
- cite `plan:m365-marketplace-bundle-packaging-conformance:R1` through `R7`
- cite `plan:m365-marketplace-bundle-packaging-conformance:T1` through `T6`
- stop immediately if the work escapes the allowlist or drifts into sibling UCP consumption/UI changes

3. Enforce approval protocol:
- this prompt executes the governed package only after explicit owner approval
- call `validate_action` before mutating phases and obey the verdict
- keep work bounded to M365-side bundle packaging and conformance

## Required Output Format (Before Approval)

Use this exact structure:

- `Decision Summary`
- `Options Considered`
- `Evaluation Criteria`
- `Why This Choice`
- `Risks`
- `Next Steps`

## Execution Order (After Approval Only)

1. Complete **M** (Model).
2. Complete **A** (Annotate).
3. Complete **T** (Tie).
4. Complete **H** (Harness).
5. Complete **S** (Stress-test).
6. Update `Operations/ACTION_LOG.md`, `Operations/EXECUTION_PLAN.md`, and `Operations/PROJECT_FILE_INDEX.md` only if the bounded phase actually executes and changes governance state.

## Validator Compatibility Anchors

M:
A:
T:
H:
S:

## M - Model

- Problem: `the standalone M365 pack source exists, but there is still no conformant marketplace bundle artifact`
- Goal: `produce one real manifest plus payload plus signatures plus evidence plus final .ucp.tar.gz bundle`
- Success criteria:
  - `the M365 pack can be described as a real marketplace bundle, not only as source code`
  - `the packaged artifact validates or fails closed explicitly`
  - `the workstream stays M365-local and does not drift into UCP-side consumption changes`

## A - Annotate

- define the bundle identity, manifest fields, payload contents, signatures, evidence set, and final artifact path
- define any remaining host dependencies explicitly if the standalone pack is not yet fully self-contained
- define the conformance gate and fail-closed outcomes

## T - Tie

- execute `T1` through `T6` in strict order
- treat `src/ucp_m365_pack/` as the authoritative runtime surface for the payload
- keep the final artifact aligned to the Pack Bundle Spec and Pack Manifest Schema references

## H - Harness

- before any write, summarize what is missing today: manifest, payload archive, signatures, evidence, and final bundle
- keep the workstream bounded to packaging/build/conformance in this repo
- do not treat source-tree ownership as a substitute for a real packaged bundle

## S - Stress-test

- validate the plan YAML against the canonical schema
- validate both prompt artifacts against the formal prompt contract
- validate project-file-index updates and `git diff --check`
- close only if the package truthfully defines the bundle/conformance workstream

## Stop Conditions

- any move to claim marketplace conformance without a real bundle artifact
- any move to solve this by changing UCP-side Marketplace/UI behavior in this repo
- any move to treat signatures or evidence as optional in the final model
