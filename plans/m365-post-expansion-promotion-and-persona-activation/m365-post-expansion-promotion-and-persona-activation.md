# Plan: M365 Repo — Post-Expansion Promotion and Persona Activation

**Plan ID:** `m365-post-expansion-promotion-and-persona-activation`
**Status:** 🟢 Active (`P1` is complete; `P2A` is next; persona-activation track is now the active critical path)
**Date:** 2026-03-21
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-post-expansion-promotion-and-persona-activation:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — promote the completed workforce program toward release branches and convert contract-only personas into real M365 workers without leaving the M365-only, policy-gated, auditable model.
**Historical lineage:** follows the closed `m365-ai-workforce-expansion-master-plan` after merge into `development` on 2026-03-21.

**Prompt discipline:** Maintain a formal prompt pair for the branch-promotion track and the persona-activation follow-on track under `docs/prompts/`, following the repo two-file prompt rule and the MATHS prompt template where execution details are delegated to Codex/Claude.

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

4. `P2D` — Specialist and regulated personas
   - the remaining engineering, testing, studio-operations, marketing-channel, finance, legal, and creative-specialist personas

5. `P2E` — Activation certification and commercial packaging closeout

### What that would unlock commercially

- `P1` unlocks governed release promotion from `development` into customer-facing branches
- `P2B` unlocks a credible “build, ship, validate, report, support” workforce core
- `P2C` unlocks stronger product, design, and growth packages that customers can buy and understand
- `P2D` unlocks the higher-value specialized workforce story, but only after the safer and more commercially urgent layers are live
- `P2E` unlocks honest claims that the workforce is not just packaged and certified, but materially activated beyond the initial four personas

## Execution Status

- `P1A` is complete.
- `P1B` is complete.
- `P1C` is complete.
- Branch promotion is complete: `development`, `staging`, and `main` all resolve to commit `f967ef6`.
- `P2A` is complete: activation definition locked, first-wave roster locked (backend-architect, devops-automator, api-tester, analytics-reporter, project-shipper, support-responder), wave order locked (P2B → P2C → P2D → P2E, fail-closed), commercial unlock mapping locked.
- `P2B` is the active next act.
- `P2C` through `P2E` remain blocked by `P2B`.

## Scope

### In scope

- define the governed promotion path from `development` to `staging` and `main`
- define the next bounded persona-activation program
- lock the first activation wave and its commercial rationale
- create prompt pairs for promotion and persona activation
- synchronize `Operations/EXECUTION_PLAN.md`, `Operations/ACTION_LOG.md`, and `Operations/PROJECT_FILE_INDEX.md`

### Out of scope

- directly activating personas in this planning step
- inventing capabilities outside the current M365-only North Star
- claiming all 39 personas are already live
- promoting to `staging` or `main` in this plan-creation step

## Requirements

- **R1 — Governed post-closeout promotion path**
- **R2 — Plain-language persona activation definition**
- **R3 — First-wave persona roster and rationale**
- **R4 — Activation order and dependency model**
- **R5 — Commercial unlock mapping**
- **R6 — Prompt-pair coverage for promotion and activation**
- **R7 — Governance synchronization**

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

**Status:** 🟢 Active

**Goal:** Activate the build, release, QA, reporting, and support personas that make the rest of the workforce operable.

#### P2C — Commercial Growth and Experience Activation

**Status:** ⏳ Pending

**Goal:** Activate the next wave of product, design, and growth personas that strengthen the external commercial story.

#### P2D — Specialist and Regulated Persona Activation

**Status:** ⏳ Pending

**Goal:** Activate the higher-risk, long-tail, and specialist personas only after the first two waves are proven.

#### P2E — Activation Certification and Commercial Closeout

**Status:** ⏳ Pending

**Goal:** Certify the activated persona waves and update the product packaging to match the new live surface.
