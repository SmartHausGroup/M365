# Plan: M365 Repo — Post-Expansion Promotion and Persona Activation

**Plan ID:** `m365-post-expansion-promotion-and-persona-activation`
**Status:** 🟢 Active (`P1` complete; `P2A` complete; `P2B` complete; `P2C` complete; `P2D` complete for the M365-backed specialist scope; `P2E` is next; `P3` is pending for external-platform preparation and later activation)
**Date:** 2026-03-21
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-post-expansion-promotion-and-persona-activation:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — promote the completed workforce program toward release branches and convert contract-only personas into real M365 workers without leaving the M365-only, policy-gated, auditable model.
**Historical lineage:** follows the closed `m365-ai-workforce-expansion-master-plan` after merge into `development` on 2026-03-21.

**Prompt discipline:** Maintain a formal prompt pair for the branch-promotion track and the persona-activation follow-on track under `docs/prompts/`, following the repo two-file prompt rule and the MATHS prompt template where execution details are delegated to Codex/Claude.

**Branch discipline:** All new persona-activation implementation work must execute on a dedicated future/feature branch first. `development` is the integration branch only after human review and explicit approval. Do not land persona-activation implementation directly on `development`, `staging`, or `main` unless the scoped act is explicitly a merge or promotion step.

## Objective

Move the completed workforce program from `development` into `staging` and then `main`, then execute a bounded follow-on program that turns selected contract-only personas into registry-backed, action-backed, commercially claimable digital employees.

## Decision Rule

`PromotionReady = DevelopmentMerged ∧ StagingAligned ∧ StagingValidated ∧ MainAligned`

`PersonaActivated = RegistryBacked ∧ ActionSurfaceImplemented ∧ AllowedDomainsBound ∧ ApprovalPolicyBound ∧ NotebookEvidenceGreen ∧ ScorecardGreen ∧ RuntimeRoutingGreen`

`CommercialActivationReady = PromotionReady ∧ Wave1ActivationGreen`

If any term is false, the next release or persona-activation claim remains `NO-GO`.

## Plain-English Follow-On Plan

### What “activate the personas” actually means

Activating a persona does **not** mean just listing it in the registry. It means all of the following are true for that persona:

- the persona is moved from `persona-contract-only` to `registry-backed`
- the persona has explicit allowed actions in `registry/agents.yaml`
- the persona has bounded executor domains and auth mode bindings
- the persona has approval and audit posture wired through the runtime
- the persona has notebook-backed evidence, validations, and green scorecards
- the persona can be delegated to honestly through Claude -> UCP -> M365

### Which personas should be activated first

Recommended first-wave personas beyond the existing active four:

1. `backend-architect`
2. `devops-automator`
3. `api-tester`
4. `analytics-reporter`
5. `project-shipper`
6. `support-responder`

Why these first:

- they strengthen delivery, release, QA, reporting, and customer operations immediately
- they make the rest of the workforce easier to activate safely
- they unlock the most credible commercial story fastest: not just “AI personas exist,” but “the platform can ship, certify, report, and support real customers”

### What order we should do it in

1. `P1` — Branch promotion
   - promote `development` to `staging`
   - validate the staging candidate
   - promote `staging` to `main`

2. `P2B` — Foundation operators
   - `backend-architect`
   - `devops-automator`
   - `api-tester`
   - `analytics-reporter`
   - `project-shipper`
   - `support-responder`

3. `P2C` — Commercial growth and experience personas
   - `content-creator`
   - `growth-hacker`
   - `ui-designer`
   - `brand-guardian`
   - `feedback-synthesizer`
   - `sprint-prioritizer`
   - `ux-researcher`
   - `studio-producer`

4. `P2D` — M365-backed specialist and regulated personas
   - the remaining engineering, testing, studio-operations, finance, legal, product, project-management, and creative-specialist personas whose action surfaces stay inside the current M365-backed runtime

5. `P2E` — Activation certification and commercial packaging closeout

6. `P3` — External-platform persona preparation and later activation
   - the blocked external-channel personas move here for credentialless preparation, credential-gated runtime surfaces, and later certification

### What that would unlock commercially

- `P1` unlocks governed release promotion from `development` into customer-facing branches
- `P2B` unlocks a credible “build, ship, validate, report, support” workforce core
- `P2C` unlocks stronger product, design, and growth packages that customers can buy and understand
- `P2D` unlocks the higher-value specialist M365 workforce story once the safer and more commercially urgent layers are live
- `P2E` unlocks honest claims that the workforce is not just packaged and certified, but materially activated across the M365-backed persona surface
- `P3` unlocks future external-channel persona expansion only after adapter contracts, credentials, and runtime proof exist; it is not part of the current M365-only commercial claim set

## Execution Status

- `P1A` is complete.
- `P1B` is complete.
- `P1C` is complete.
- Branch promotion completed on 2026-03-21: `development`, `staging`, and `main` were aligned at commit `f967ef6` at P1 closeout. P2A closeout advanced `development` to `20b366a`; P2B, P2C, and P2D implementation work lives on `feature/m365_personas` pending review-approved merge.
- `P2A` is complete: activation definition locked, first-wave roster locked (backend-architect, devops-automator, api-tester, analytics-reporter, project-shipper, support-responder), wave order locked and later refined into the current fail-closed sequence (P2B → P2C → P2D for M365-backed specialist personas → P2E → P3 for external-platform preparation and later activation), commercial unlock mapping locked.
- `P2B` is complete: 6 foundation operators activated (backend-architect 13 actions, devops-automator 10, api-tester 8, analytics-reporter 9, project-shipper 9, support-responder 8 = 57 total new actions). All pass the 6-point activation test. Total registry-backed personas: 10.
- `P2C` is complete: 8 commercial growth and experience personas activated (content-creator 8 actions, growth-hacker 10, ui-designer 7, brand-guardian 8, feedback-synthesizer 7, sprint-prioritizer 8, ux-researcher 7, studio-producer 9 = 64 total new actions). All pass the 6-point activation test. L74 lemma/invariant, scorecard green. 7 tests passed, CI verifier passed. Total registry-backed personas: 18/39.
- `P2D` is complete for the M365-backed specialist and regulated scope: 16 personas activated (122 total new actions). The 5 external-platform personas (`instagram-curator`, `tiktok-strategist`, `reddit-community-builder`, `twitter-engager`, `app-store-optimizer`) are formally descoped from `P2D` and moved into `P3` because they require external APIs not implemented in this repo. L75 lemma/invariant, scorecard green. 8 tests passed, CI verifier passed. Total registry-backed personas: 34/39.
- `P2E` is next and has NOT been started.
- `P3` is pending: it will carry credentialless preparation, credential-gated runtime work, and later certification for the 5 external-platform personas that are not part of the current M365-backed activation claim set.

## Scope

### In scope

- define the governed promotion path from `development` to `staging` and `main`
- define the next bounded persona-activation program
- lock the first activation wave and its commercial rationale
- create prompt pairs for promotion and persona activation
- define the later external-platform preparation and activation phase for personas that do not fit the current M365-backed surface
- synchronize `Operations/EXECUTION_PLAN.md`, `Operations/ACTION_LOG.md`, and `Operations/PROJECT_FILE_INDEX.md`

### Out of scope

- directly activating personas in this planning step
- inventing capabilities outside the current M365-only North Star
- claiming all 39 personas are already live
- promoting to `staging` or `main` in this plan-creation step
- claiming unsupported external-platform personas are active before credential-gated runtime surfaces exist

## Requirements

- **R1 — Governed post-closeout promotion path**
- **R2 — Plain-language persona activation definition**
- **R3 — First-wave persona roster and rationale**
- **R4 — Activation order and dependency model**
- **R5 — Commercial unlock mapping**
- **R6 — Prompt-pair coverage for promotion and activation**
- **R7 — Governance synchronization**
- **R8 — Re-scope P2D to the M365-backed specialist surface**
- **R9 — Create the later external-platform preparation and activation track**
- **R10 — Advance P2E without over-claiming blocked external-platform personas**
- **R11 — Create formal prompt pairs for P2E and P3**

## Execution Stack

### P1 — Branch Promotion

**Status:** ✅ Complete

**Goal:** Promote the completed workforce program from `development` into `staging` and then `main` through a deterministic, governed branch path.

**Outputs:**

- staging promotion prompt pair
- explicit `development -> staging -> main` sequence
- promotion gate and blocker rules

**Child Acts:**

#### P1A — Promote `development` to `staging`

**Status:** ✅ Complete

**Goal:** Create or align `staging` from the merged `development` tip and push it as the release-candidate branch.

#### P1B — Validate Staging Candidate

**Status:** ✅ Complete

**Goal:** Confirm `staging` is aligned, replay-safe, and ready for production promotion.

#### P1C — Promote `staging` to `main`

**Status:** ✅ Complete

**Goal:** Advance the validated release candidate from `staging` into `main` and close the promotion track.

### P2 — Persona Activation Follow-On

**Status:** 🟢 Active

**Goal:** Turn selected contract-only personas into action-backed, commercially claimable digital employees in bounded waves.

**Outputs:**

- activation-definition contract
- first-wave activation roster
- activation-wave order
- commercial unlock map

**Child Acts:**

#### P2A — Activation Contract and First-Wave Lock

**Status:** ✅ Complete

**Goal:** Define activation entry criteria and lock the first-wave roster against the current authoritative persona registry.

**Completion summary:** Activation defined as a 6-point runtime state change (registry-backed, action-surfaced, domain-bound, approval-wired, notebook-evidenced, runtime-routed). First-wave roster locked: `backend-architect`, `devops-automator`, `api-tester`, `analytics-reporter`, `project-shipper`, `support-responder`. Wave order locked: P2B (foundation) → P2C (growth/experience) → P2D (specialist/regulated) → P2E (certification). Commercial unlock mapping locked per wave. All 11 MATHS checks passed (C0–C10). Gate: GO.

#### P2B — Foundation Operators Activation

**Status:** ✅ Complete

**Goal:** Activate the build, release, QA, reporting, and support personas that make the rest of the workforce operable.

**Completion summary:** 6 foundation operators activated across 4 departments: backend-architect (13 actions, engineering), devops-automator (10 actions, engineering), api-tester (8 actions, testing), analytics-reporter (9 actions, studio-operations), project-shipper (9 actions, project-management), support-responder (8 actions, studio-operations). Total: 57 new actions. All pass the 6-point activation test. L73 lemma/invariant, scorecard green. CI verifiers and tests updated and passing (25 passed). Total registry-backed personas: 10/39.

#### P2C — Commercial Growth and Experience Activation

**Status:** ✅ Complete

**Goal:** Activate the next wave of product, design, and growth personas that strengthen the external commercial story.

**Completion summary:** 8 commercial growth and experience personas activated across 4 departments: content-creator (8 actions, marketing), growth-hacker (10 actions, marketing), ui-designer (7 actions, design), brand-guardian (8 actions, design), feedback-synthesizer (7 actions, product), sprint-prioritizer (8 actions, product), ux-researcher (7 actions, design), studio-producer (9 actions, project-management). Total: 64 new actions. All pass the 6-point activation test. L74 lemma/invariant, scorecard green. CI verifier and tests passing (7 passed). Total registry-backed personas: 18/39.

#### P2D — Specialist and Regulated Persona Activation

**Status:** ✅ Complete (M365-backed specialist scope)

**Goal:** Activate the higher-risk, long-tail, and specialist personas that can be truthfully supported inside the current M365-backed runtime after the first two waves are proven.

**Completion summary:** 16 M365-backed specialist and regulated personas activated across 6 departments with 122 new actions. High-risk personas (finance-tracker, infrastructure-maintainer, legal-compliance-checker) have explicit approval rules. L75 lemma/invariant, scorecard green. CI verifier and tests passing (8 passed). Total registry-backed personas: 34/39.

**Descoped to P3 (5):** `instagram-curator`, `tiktok-strategist`, `reddit-community-builder`, `twitter-engager`, `app-store-optimizer` — all require non-M365 external-platform APIs (Instagram/Meta, TikTok, Reddit, Twitter/X, App Store Connect/Google Play) that are not implemented in this repo. They are not counted as active in the current M365-backed persona claim set and move into the later `P3` preparation/activation track.

#### P2E — Activation Certification and Commercial Closeout

**Status:** ⏳ Pending

**Goal:** Certify the activated M365-backed persona waves and update the product packaging to match the current live surface truthfully.

### P3 — External Platform Persona Preparation and Later Activation

**Status:** ⏳ Pending

**Goal:** Prepare and later activate the external-platform personas without violating the current M365-only runtime and commercial claim boundaries.

**Outputs:**

- credentialless external-platform preparation contract
- credential-gated runtime implementation plan
- later activation certification and packaging path

**Child Acts:**

#### P3A — External Platform Contract and Credentialless Preparation

**Status:** ⏳ Pending

**Goal:** Define the external-platform persona contract, env-var credential boundary, adapter surfaces, and fail-closed `not configured` behavior without claiming any persona is active.

#### P3B — Credential-Gated Runtime Surface Implementation

**Status:** ⏳ Pending

**Goal:** Implement the external-platform runtime surfaces only after bounded credentials, adapters, approvals, and routing exist.

#### P3C — External Platform Activation Certification and Packaging

**Status:** ⏳ Pending

**Goal:** Certify and package the external-platform personas only after their runtime surfaces are live, validated, and commercially truthful.
