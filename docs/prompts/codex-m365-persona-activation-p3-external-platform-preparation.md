# MATHS Prompt: P3A External Platform Contract and Credentialless Preparation

## Branch Note

- Execute this act only on `feature/m365_personas` unless an explicit merge step is later approved.
- Do not merge into `development`.
- Do not touch `staging` or `main`.

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-post-expansion-promotion-and-persona-activation:P3A`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Execute only `P3A` on `feature/m365_personas`.
- Stop on first `FAIL` or `BLOCKED`.
- Do not merge into `development`.
- Do not touch `staging` or `main`.
- Do not start `P3B`, `P3C`, or any live credentialed activation work.
- Do not claim any external-platform persona is active.
- Use credentialless preparation only:
  - env-var contract definitions
  - adapter/runtime boundary definitions
  - fail-closed `not configured` behavior
- Never hardcode credentials, tokens, secrets, or fake live endpoints.

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-PERSONA-P3A`
- Run ID: `persona-activation-p3-external-platform-preparation`
- Branch: `feature/m365_personas`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-post-expansion-promotion-and-persona-activation:R9`
  - `plan:m365-post-expansion-promotion-and-persona-activation:R11`
  - `plan:m365-post-expansion-promotion-and-persona-activation:P3A`

## Context

- Task name: `Define the external-platform contract and credentialless preparation boundary`
- Domain: `governance + preparation`
- Branch model: `feature-branch first; development only after review-approved merge`
- Personas in scope:
  - `instagram-curator`
  - `tiktok-strategist`
  - `reddit-community-builder`
  - `twitter-engager`
  - `app-store-optimizer`
- Current truthful state:
  - `all 5 remain persona-contract-only`
  - `all 5 have allowed_actions: []`
  - `none are active`
- Goal boundary:
  - `prepare them without active credentials`
  - `do not activate them`
  - `do not broaden the current M365-backed commercial claim set`
- Allowlist:
  - `registry/*.yaml`
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
  - `live credential use`
  - `real external API calls`
  - `claiming any of the 5 personas are active`
  - `P3B/P3C implementation`
  - `development merge work`

## M - Model

- Problem: `Five personas have clear commercial value but depend on external-platform APIs that do not yet exist in this repo.`
- Goal: `Create a governed, credentialless preparation layer so these personas can be carried honestly as prepared-but-inactive until real adapters and credentials exist.`
- Success criteria:
  - `each persona has an explicit external-platform contract boundary`
  - `required credentials are represented only as env-var contracts or config placeholders`
  - `fail-closed not-configured behavior is defined and proven`
  - `no persona is claimed active`
- Out of scope:
  - `live external-platform activation`
  - `real secrets or real tenant/external credentials`
  - `commercial claims that these personas are available now`

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `contract/preparation artifacts exist for all 5 personas`
  - `credential requirements are expressed as environment or config contracts only`
- Runtime/test evidence:
  - `unsupported or unconfigured calls resolve to fail-closed behavior`
  - `tests and verifier prove prepared-but-inactive semantics`
- Governance evidence:
  - `plan, ACTION_LOG, PROJECT_FILE_INDEX, and EXECUTION_PLAN remain synchronized`
- Determinism evidence:
  - `fixed repo state reproduces the same 5-person deferred set and the same fail-closed preparation semantics`

## T - Tie

- Dependency ties:
  - `P3A must complete before any credential-gated runtime surface can begin in P3B`
  - `P3C cannot begin until real external adapters and credentials exist`
- Known failure modes:
  - `silently turning preparation into activation`
  - `hardcoding credentials or fake tokens`
  - `creating routes that imply live support when no runtime exists`
- GO criteria:
  - `all 5 personas are prepared with explicit contract boundaries and remain non-active`
- NO-GO criteria:
  - `any live external API dependency, credential leak, or activation claim`

## H - Harness (ordered checks)

`M365-PERSONA-P3A-C0` Preflight

- Confirm branch is `feature/m365_personas` and `P3A` is the scoped act.

`M365-PERSONA-P3A-C1` Persona inventory

- Re-read the 5 deferred personas and capture their current contract-only state.

`M365-PERSONA-P3A-C2` External-platform contract design

- Define platform boundaries, env-var names, adapter expectations, and fail-closed semantics.

`M365-PERSONA-P3A-C3` Registry and config preparation

- Add only the bounded preparation metadata needed for later activation; do not populate live actions or active status.

`M365-PERSONA-P3A-C4` MA evidence chain

- Create the lemma, invariant, notebooks, and scorecard for credentialless preparation.

`M365-PERSONA-P3A-C5` Verification surface

- Add/update generated proof, CI verifier, and targeted tests.

`M365-PERSONA-P3A-C6` Governance sync

- Update the follow-on plan, ACTION_LOG, PROJECT_FILE_INDEX, and EXECUTION_PLAN truthfully on the feature branch.

`M365-PERSONA-P3A-C7` Validation

- Run YAML/JSON parse, targeted tests, CI verifier, `git diff --check`, and `pre-commit run --all-files`.

`M365-PERSONA-P3A-C8` Final decision

- If all checks pass, commit and push on `feature/m365_personas`, report SHA, and stop.

## S - Stress-test

- Adversarial checks:
  - `If any change makes one of the 5 personas look active, fail closed.`
  - `If any adapter path can run without credentials, fail closed unless it deterministically returns a not-configured error.`
- Replay checks:
  - `Repeated reads must preserve the same 5-person prepared-but-inactive partition on fixed repo state.`

## Output Contract

- Deliverables:
  - `credentialless external-platform preparation contract for 5 deferred personas`
  - `env-var / config boundary definition`
  - `fail-closed not-configured runtime semantics`
  - `truthful governance sync on feature/m365_personas`
- Validation results:
  - `M365-PERSONA-P3A-C0..C8 statuses`
- Evidence links:
  - `file paths and commands only`
- Final decision lines:
  - `GATE:M365-PERSONA-P3A STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Any live credential, token, or secret in repo files.
- Any claim that one of the 5 external-platform personas is active.
- Any real external API execution during the preparation act.
- Any attempt to start `P3B` or `P3C` from this prompt.
