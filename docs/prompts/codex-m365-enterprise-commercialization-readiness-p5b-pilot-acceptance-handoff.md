# MATHS Prompt: P5B Pilot Acceptance and Customer Handoff

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-commercialization-readiness:P5B`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-COMM-P5B-C0` -> `M365-COMM-P5B-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:M365-COMM-P5B STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-COMM-P5B`
- Run ID: `p5b-pilot-acceptance-handoff`
- Commit SHA: `<fill at execution time>`
- Plan refs in scope:
  - `plan:m365-enterprise-commercialization-readiness:R6`
  - `plan:m365-enterprise-commercialization-readiness:P5B`
- Invariant IDs in scope: `N/A unless an approved scope change introduces MA-governed runtime work`
- Lemma IDs in scope: `N/A unless an approved scope change introduces MA-governed runtime work`
- Owners: `product`, `delivery`, `operations`

## Context

- Task name: `P5B Pilot Acceptance and Customer Handoff`
- Domain: `docs`
- Dependencies: P5A enterprise collateral and all prior accepted subphase outputs
- Allowlist:
  - `plans/m365-enterprise-commercialization-readiness/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `docs/commercialization/m365-pilot-acceptance-and-customer-handoff.md`
- Denylist:
  - `src/**`
  - `tests/**`
  - `docs/prompts/**`

## M - Model

- Problem: the product is not pilot-ready unless success criteria, responsibilities, and handoff boundaries are explicit.
- Goal: define pilot acceptance and customer handoff for the standalone M365 module.
- Success criteria:
  - pilot success criteria are explicit
  - customer and SmartHaus responsibilities are explicit
  - sign-off and handoff conditions are explicit
- Out of scope:
  - negotiating a live customer contract
  - customer-specific custom deployment design

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `docs/commercialization/m365-pilot-acceptance-and-customer-handoff.md` with sections `Pilot Success Criteria`, `Acceptance Checklist`, `Responsibility Matrix`, `Handoff Checklist`, and `Sign-Off Model`
- Runtime/test evidence:
  - cross-check against P5A collateral and earlier accepted subphase outputs
- Governance evidence:
  - plan and log synchronization
- Determinism evidence:
  - repeated pilot-acceptance classification yields the same success and handoff rules

## T - Tie

- Dependency ties:
  - P5A -> collateral and supported scope feed pilot expectations
  - earlier subphases -> governance, validation, and operations prerequisites
- Known failure modes:
  - pilot success criteria are vague
  - responsibilities are left implicit
- GO criteria:
  - acceptance, responsibility, and handoff boundaries are explicit and coherent
- NO-GO criteria:
  - pilot success depends on undefined scope or undocumented behavior

## H - Harness (ordered checks)

- `M365-COMM-P5B-C0` Preflight.
- `M365-COMM-P5B-C1` Baseline inventory of pilot and handoff prerequisites from prior outputs.
- `M365-COMM-P5B-C2` Draft pilot-success and acceptance-checklist sections.
- `M365-COMM-P5B-C3` Draft responsibility, handoff, and sign-off sections.
- `M365-COMM-P5B-C4` Schema/artifact contract validation.
- `M365-COMM-P5B-C5` Gate logic hardening: ensure pilot criteria do not require unsupported capabilities.
- `M365-COMM-P5B-C6` Execute targeted cross-checks against prior accepted outputs.
- `M365-COMM-P5B-C7` Strict artifact validation.
- `M365-COMM-P5B-C8` Deterministic replay of acceptance and responsibility rules.
- `M365-COMM-P5B-C9` Hard gates (strict order):
  1. `rg -n "Pilot Success Criteria|Acceptance Checklist|Responsibility Matrix|Handoff Checklist|Sign-Off Model" docs/commercialization/m365-pilot-acceptance-and-customer-handoff.md`
  2. `rg -n "plan:m365-enterprise-commercialization-readiness:P5B" plans/m365-enterprise-commercialization-readiness docs/commercialization`
  3. `git diff --check`
- `M365-COMM-P5B-C10` Governance synchronization and final decision.

## S - Stress-test

- Adversarial checks:
  - define pilot success using unsupported roadmap functionality
  - leave customer responsibilities implicit
- Replay checks:
  - success criteria and responsibility matrix must match across repeated runs

## Output Contract

- Deliverables:
  - `docs/commercialization/m365-pilot-acceptance-and-customer-handoff.md`
- Validation results:
  - `M365-COMM-P5B-C0..C10`
- Evidence links:
  - file paths and commands only
- Residual risks:
  - commercial negotiation and contracting remain outside repo scope
- Final decision lines:
  - `GATE:M365-COMM-P5B STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Pilot success criteria exceed supported scope.
- Responsibility or sign-off boundaries remain vague.
- Scope drifts into customer-specific implementation planning.
