# MATHS Prompt: P2E Activation Certification and Commercial Closeout

## Branch Note

- Execute this act only on `feature/m365_personas` unless an explicit merge step is later approved.
- Do not merge into `development` during this act.
- Do not touch `staging` or `main`.

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-post-expansion-promotion-and-persona-activation:P2E`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Execute only `P2E` on `feature/m365_personas`.
- Stop on first `FAIL` or `BLOCKED`.
- Do not merge into `development`.
- Do not touch `staging` or `main`.
- Do not start `P3A`, `P3B`, or `P3C`.
- Do not claim the 5 external-platform personas are active.
- Certify only the current M365-backed persona surface that has already passed the locked activation contract.

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-PERSONA-P2E`
- Run ID: `persona-activation-p2e-certification-closeout`
- Branch: `feature/m365_personas`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-post-expansion-promotion-and-persona-activation:R10`
  - `plan:m365-post-expansion-promotion-and-persona-activation:R11`
  - `plan:m365-post-expansion-promotion-and-persona-activation:P2A`
  - `plan:m365-post-expansion-promotion-and-persona-activation:P2B`
  - `plan:m365-post-expansion-promotion-and-persona-activation:P2C`
  - `plan:m365-post-expansion-promotion-and-persona-activation:P2D`
  - `plan:m365-post-expansion-promotion-and-persona-activation:P2E`

## Context

- Task name: `Certify the activated M365-backed persona surface and close the current activation track`
- Domain: `governance + certification`
- Branch model: `feature-branch first; development only after review-approved merge`
- Dependencies:
  - `P2A complete`
  - `P2B complete on feature/m365_personas`
  - `P2C complete on feature/m365_personas`
  - `P2D complete for the M365-backed specialist/regulatory scope`
  - `5 external-platform personas moved to P3 and remain contract-only`
- Current truthful activation boundary:
  - `34 registry-backed personas`
  - `5 external-platform personas not active`
- Allowlist:
  - `registry/*.yaml`
  - `docs/commercialization/*`
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
  - `P3 implementation`
  - `claiming 39/39 personas are active`
  - `claiming external-platform personas are part of the current M365-backed commercial surface`

## M - Model

- Problem: `The M365-backed persona waves are materially activated, but the activation track still needs formal certification and packaging closeout before those claims are commercially complete.`
- Goal: `Certify the currently activated M365-backed persona surface, update packaging/claim boundaries, and close P2 truthfully without over-claiming blocked external-platform personas.`
- Success criteria:
  - `the certified activation boundary is exactly 34 registry-backed personas`
  - `the 5 external-platform personas remain explicitly non-active and deferred to P3`
  - `packaging and commercialization text matches the true live surface`
  - `P2E is complete on feature/m365_personas and P3 has not started`
- Out of scope:
  - `activating any new personas`
  - `implementing external-platform adapters`
  - `merging into development`

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `a P2E contract/evidence chain exists and defines the current certified activation boundary`
  - `commercialization/package artifacts name the active M365-backed surface truthfully`
- Runtime/test evidence:
  - `the activated persona counts and blocked persona set are replayable from the registries`
  - `the certification verifier and targeted tests pass`
- Governance evidence:
  - `the follow-on plan, EXECUTION_PLAN, ACTION_LOG, and PROJECT_FILE_INDEX are synchronized on the feature branch`
- Determinism evidence:
  - `repeated reads on fixed repo state produce the same 34 active / 5 deferred partition`

## T - Tie

- Dependency ties:
  - `P2E depends on P2B, P2C, and the M365-backed portion of P2D being green`
  - `P3 cannot be claimed started as part of P2E`
- Known failure modes:
  - `accidentally certifying the blocked external-platform personas`
  - `drifting commercialization language ahead of runtime truth`
  - `treating deferred P3 personas as part of the current M365-backed release`
- GO criteria:
  - `the certified surface is bounded, truthful, and backed by notebooks, scorecards, tests, and governance sync`
- NO-GO criteria:
  - `any certification claim that exceeds the currently activated M365-backed persona surface`

## H - Harness (ordered checks)

`M365-PERSONA-P2E-C0` Preflight

- Confirm branch is `feature/m365_personas` and `P2E` is the scoped act.

`M365-PERSONA-P2E-C1` Surface readback

- Re-read the registries and confirm the exact active/deferred partition (`34/5`).

`M365-PERSONA-P2E-C2` Certification boundary

- Define the exact current certified activation boundary and the explicit exclusions.

`M365-PERSONA-P2E-C3` MA evidence chain

- Create the lemma, invariant, notebooks, and scorecard for the certification closeout.

`M365-PERSONA-P2E-C4` Packaging and commercial claim sync

- Update packaging/commercialization artifacts so the live surface claims match the certified boundary.

`M365-PERSONA-P2E-C5` Verification surface

- Add/update generated proof, verifier, and targeted tests.

`M365-PERSONA-P2E-C6` Governance sync

- Update the follow-on plan, ACTION_LOG, PROJECT_FILE_INDEX, and EXECUTION_PLAN truthfully on the feature branch.

`M365-PERSONA-P2E-C7` Validation

- Run YAML/JSON parse, targeted tests, CI verifier, `git diff --check`, and `pre-commit run --all-files`.

`M365-PERSONA-P2E-C8` Final decision

- If all checks pass, commit and push on `feature/m365_personas`, report SHA, and stop.

## S - Stress-test

- Adversarial checks:
  - `If any artifact tries to certify the 5 external-platform personas, fail closed.`
  - `If packaging language implies 39/39 active personas, fail closed.`
- Replay checks:
  - `Repeated reads of registry state must reproduce the same certified 34/5 partition for fixed repo state.`

## Output Contract

- Deliverables:
  - `bounded P2E certification contract for the current M365-backed persona surface`
  - `notebook-backed lemma and scorecard evidence`
  - `updated packaging/commercialization boundary`
  - `truthful governance sync on feature/m365_personas`
- Validation results:
  - `M365-PERSONA-P2E-C0..C8 statuses`
- Evidence links:
  - `file paths and commands only`
- Final decision lines:
  - `GATE:M365-PERSONA-P2E STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Any attempt to certify the deferred external-platform personas as active.
- Any missing notebook-backed evidence for the certification claim.
- Any attempt to start `P3` as part of the `P2E` run.
- Any attempt to merge into `development`, `staging`, or `main`.
