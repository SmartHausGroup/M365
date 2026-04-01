# MATHS Prompt: P2C Commercial Growth and Experience Activation

## Branch Note

- I previously told you to land persona-activation work on `development`.
- That was my mistake.
- The correct workflow for this repo is feature-branch first, review, then explicit merge approval.
- Execute this act only on `feature/m365_personas` unless an explicit merge step is later approved.

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-post-expansion-promotion-and-persona-activation:P2C`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Execute only `P2C` on `feature/m365_personas`.
- Stop on first `FAIL` or `BLOCKED`.
- Do not merge into `development`.
- Do not touch `staging` or `main`.
- Do not start `P2D` or `P2E`.
- Do not claim any persona is active until it satisfies the locked 6-point activation definition from `P2A`.

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-PERSONA-P2C`
- Run ID: `persona-activation-p2c-growth-experience`
- Branch: `feature/m365_personas`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-post-expansion-promotion-and-persona-activation:R1`
  - `plan:m365-post-expansion-promotion-and-persona-activation:R6`
  - `plan:m365-post-expansion-promotion-and-persona-activation:R7`
  - `plan:m365-post-expansion-promotion-and-persona-activation:P2A`
  - `plan:m365-post-expansion-promotion-and-persona-activation:P2B`
  - `plan:m365-post-expansion-promotion-and-persona-activation:P2C`

## Context

- Task name: `Activate the commercial growth and experience persona wave`
- Domain: `governance + implementation`
- Branch model: `feature-branch first; development only after review-approved merge`
- Dependencies:
  - `P2A complete`
  - `P2B complete on feature/m365_personas`
  - `P2C has not been started`
- Personas in scope:
  - `content-creator`
  - `growth-hacker`
  - `ui-designer`
  - `brand-guardian`
  - `feedback-synthesizer`
  - `sprint-prioritizer`
  - `ux-researcher`
  - `studio-producer`
- Allowlist:
  - `registry/agents.yaml`
  - `registry/persona_registry_v2.yaml`
  - `registry/persona_capability_map.yaml`
  - `registry/executor_routing_v2.yaml`
  - `registry/department_pack_marketing_v1.yaml`
  - `registry/department_pack_design_v1.yaml`
  - `registry/department_pack_product_v1.yaml`
  - `registry/department_pack_studio_operations_v1.yaml`
  - `docs/ma/lemmas/*`
  - `invariants/lemmas/*`
  - `notebooks/m365/*`
  - `notebooks/lemma_proofs/*`
  - `artifacts/scorecards/*`
  - `configs/generated/*`
  - `tests/*`
  - `scripts/ci/*`
  - `plans/m365-post-expansion-promotion-and-persona-activation/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
- Denylist:
  - `development merge work`
  - `staging/main promotion`
  - `P2D/P2E implementation`
  - `non-M365 external-channel API expansion`

## M - Model

- Problem: `P2B established the credible workforce core, but the customer-facing product, design, and growth persona wave remains contract-only.`
- Goal: `Activate the 8 P2C personas as real, bounded, reviewable M365 workers on the feature branch.`
- Success criteria:
  - `all 8 P2C personas become registry-backed on the feature branch`
  - `each persona gets explicit allowed actions, domains, approval posture, routing coverage, and notebook-backed evidence`
  - `department packs, tests, verifiers, scorecards, and generated proofs are synchronized`
  - `P2C is complete on the feature branch and P2D remains not started`
- Out of scope:
  - `merging to development`
  - `making claims about production/integration branches`
  - `marketing personas that require non-M365 external channel APIs`

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `all 8 P2C personas move from persona-contract-only to registry-backed on the feature branch`
  - `department packs reflect partial or expanded activation truthfully`
- Runtime/test evidence:
  - `all new actions route through existing executor domains or explicit bounded overrides`
  - `targeted test suites and CI verifiers pass`
- Governance evidence:
  - `ACTION_LOG, PROJECT_FILE_INDEX, and the follow-on plan are synchronized on the feature branch`
- Determinism evidence:
  - `scorecards and notebooks prove fixed-action activation for fixed repo state`

## T - Tie

- Dependency ties:
  - `P2C depends on the locked P2A activation definition and the completed P2B foundation wave`
  - `P2D cannot start until P2C is green`
- Known failure modes:
  - `landing work on development again`
  - `claiming personas are active without notebook-backed evidence`
  - `activating personas that depend on non-M365 external channels`
- GO criteria:
  - `all 8 personas satisfy the 6-point activation test on feature/m365_personas`
- NO-GO criteria:
  - `any missing notebook evidence, routing gap, approval mismatch, or governance desync`

## H - Harness (ordered checks)

`M365-PERSONA-P2C-C0` Preflight

- Confirm branch is `feature/m365_personas` and `P2C` is the scoped act.

`M365-PERSONA-P2C-C1` Persona inventory

- Read the authoritative persona registry, capability map, and department packs for the 8 P2C personas.

`M365-PERSONA-P2C-C2` Action-surface design

- Define bounded M365-only action surfaces for all 8 personas.

`M365-PERSONA-P2C-C3` Registry and routing implementation

- Update persona registry, agents, capability map, routing, and department packs.

`M365-PERSONA-P2C-C4` MA evidence chain

- Create the new lemma, invariant, primary notebook, lemma-proof notebook, and scorecard for P2C.

`M365-PERSONA-P2C-C5` Verification surface

- Add/update generated proofs, CI verifiers, and targeted tests.

`M365-PERSONA-P2C-C6` Governance sync

- Update the follow-on plan, ACTION_LOG, PROJECT_FILE_INDEX, and EXECUTION_PLAN truthfully on the feature branch.

`M365-PERSONA-P2C-C7` Validation

- Run YAML/JSON parse, targeted tests, CI verifiers, `git diff --check`, and `pre-commit run --all-files`.

`M365-PERSONA-P2C-C8` Final decision

- If all checks pass, commit and push on `feature/m365_personas`, report SHA, and stop.

## S - Stress-test

- Adversarial checks:
  - `If a proposed P2C persona requires a non-M365 external platform, block it and escalate instead of silently broadening scope.`
  - `If any new action cannot be routed or approved deterministically, fail closed.`
- Replay checks:
  - `Repeated reads of the feature-branch registry state must produce the same activation counts and roster.`

## Output Contract

- Deliverables:
  - `bounded activation surface for 8 P2C personas`
  - `notebook-backed lemma and scorecard evidence`
  - `updated tests, verifiers, and generated proofs`
  - `truthful governance sync on feature/m365_personas`
- Validation results:
  - `M365-PERSONA-P2C-C0..C8 statuses`
- Evidence links:
  - `file paths and commands only`
- Final decision lines:
  - `GATE:M365-PERSONA-P2C STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Any attempt to land implementation on `development`, `staging`, or `main`.
- Any missing notebook-backed evidence for the claimed activation.
- Any claim that `P2D` or `P2E` started.
- Any dependency on non-M365 external-channel action surfaces.
