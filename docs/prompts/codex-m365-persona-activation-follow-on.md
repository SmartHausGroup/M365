# MATHS Prompt: P2 Persona Activation Follow-On

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-post-expansion-promotion-and-persona-activation:P2A`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-PERSONA-P2-C0` -> `M365-PERSONA-P2-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:M365-PERSONA-P2 STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-PERSONA-P2`
- Run ID: `persona-activation-follow-on`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-post-expansion-promotion-and-persona-activation:R1`
  - `plan:m365-post-expansion-promotion-and-persona-activation:R2`
  - `plan:m365-post-expansion-promotion-and-persona-activation:R3`
  - `plan:m365-post-expansion-promotion-and-persona-activation:R4`
  - `plan:m365-post-expansion-promotion-and-persona-activation:R5`
  - `plan:m365-post-expansion-promotion-and-persona-activation:P2A`
  - `plan:m365-post-expansion-promotion-and-persona-activation:P2B`
- Invariant IDs in scope: `<define during execution>`
- Lemma IDs in scope: `<define during execution>`
- Owners: `product`, `engineering`, `MA`

## Context

- Task name: `Define and begin the next persona-activation program`
- Domain: `governance`
- Dependencies: `the workforce expansion master plan is closed; branch-promotion track should be completed or explicitly deferred by approval`
- Allowlist:
  - `plans/m365-post-expansion-promotion-and-persona-activation/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
  - `docs/prompts/codex-m365-persona-activation-follow-on*`
  - `registry/persona_registry_v2.yaml`
  - `registry/persona_capability_map.yaml`
  - `registry/agents.yaml`
  - `docs/commercialization/*persona*`
- Denylist:
  - `branch-promotion work unless explicitly in scope`
  - `claims that all 39 personas are already live`
  - `any non-M365 external-channel expansion`

## M - Model

- Problem: `The workforce platform is structurally complete, but 35 personas remain contract-only and cannot yet be honestly sold or delegated to as active workers.`
- Goal: `Lock the activation contract, first-wave roster, execution order, and commercial unlock path for turning selected personas into live workers.`
- Success criteria:
  - `activation is defined as a concrete runtime state change, not a vague label`
  - `the first activation wave names exact personas from the authoritative roster`
  - `the wave order is commercially justified and fail-closed`
- Out of scope:
  - `claiming late-wave marketing-channel personas are live before their bounded action surfaces exist`
  - `executing unrelated branch promotion or tenant changes`

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `The follow-on plan and prompt pair explicitly cover activation meaning, first personas, order, and commercial unlocks.`
- Runtime/test evidence:
  - `Any activation recommendation references current registry-backed vs contract-only state truthfully.`
- Governance evidence:
  - `EXECUTION_PLAN, ACTION_LOG, and PROJECT_FILE_INDEX remain synchronized if state changes.`
- Determinism evidence:
  - `Repeated reads of the persona registry and persona-capability map produce the same first-wave roster recommendation for fixed repo state.`

## T - Tie

- Dependency ties:
  - `P2A must lock the activation contract before any wave claim can proceed.`
  - `P2B should activate the personas that make P2C and P2D safer and faster.`
- Known failure modes:
  - `selecting flashy but commercially weak personas first`
  - `recommending personas whose value depends on non-M365 external APIs`
  - `treating contract-only personas as already active`
- GO criteria:
  - `All checks pass and the first-wave roster is clearly tied to commercial unlocks and current repo truth.`
- NO-GO criteria:
  - `Any mismatch with the authoritative roster, capability map, or North Star constraints.`

## H - Harness (ordered checks)

`M365-PERSONA-P2-C0` Preflight

- Confirm the closed workforce-expansion state and the active follow-on plan refs.

`M365-PERSONA-P2-C1` Baseline inventory

- Read the authoritative persona registry and capability map and capture the current active vs contract-only counts.

`M365-PERSONA-P2-C2` Activation definition lock

- Define activation as registry-backed, action-backed, routed, approved, audited, notebook-backed runtime reality.

`M365-PERSONA-P2-C3` First-wave selection

- Select the first personas that unlock delivery, release, QA, reporting, and support.

`M365-PERSONA-P2-C4` Ordering rule

- Define the bounded wave order for foundation operators, commercial growth/experience, and specialist/regulatory personas.

`M365-PERSONA-P2-C5` Commercial unlock map

- Tie each wave to clear commercial outcomes instead of generic capability breadth.

`M365-PERSONA-P2-C6` Scope-hardening

- Explicitly exclude claims that depend on non-M365 external channels or unimplemented action surfaces.

`M365-PERSONA-P2-C7` Strict artifact validation

- Verify the plan and prompt files contain the required four simple-format sections.

`M365-PERSONA-P2-C8` Deterministic replay

- Re-read the authoritative roster and confirm the first-wave roster remains the same for fixed repo state.

`M365-PERSONA-P2-C9` Hard gates (strict order)

1. `registry/persona_registry_v2.yaml readback`
2. `registry/persona_capability_map.yaml readback`
3. `git diff --check or approved equivalent`

`M365-PERSONA-P2-C10` Final decision

- Emit GO/NO-GO and stop at the activation-plan boundary.

## S - Stress-test

- Adversarial checks:
  - `If a recommended persona depends mainly on external social platforms, push it to a later wave.`
  - `If a persona lacks a commercial unlock or operational leverage story, exclude it from wave 1.`
- Replay checks:
  - `The first-wave roster and commercial unlock summary must remain stable across repeated reads on fixed repo state.`

## Output Contract

- Deliverables:
  - `plain-language activation definition`
  - `first-wave persona roster`
  - `activation wave order`
  - `commercial unlock summary`
- Validation results:
  - `M365-PERSONA-P2-C0..C10 statuses`
- Evidence links:
  - `file paths and commands only`
- Residual risks:
  - `state any remaining blockers explicitly or use none`
- Final decision lines:
  - `GATE:M365-PERSONA-P2 STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Any recommendation that contradicts the authoritative roster or capability map.
- Any claim that a contract-only persona is already active.
- Any wave ordering that depends on non-M365 external integrations as a first-wave prerequisite.
- Any missing plan or governance synchronization.
