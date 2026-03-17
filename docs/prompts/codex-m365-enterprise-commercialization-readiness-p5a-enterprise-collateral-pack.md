# MATHS Prompt: P5A Enterprise Collateral Pack

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-commercialization-readiness:P5A`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-COMM-P5A-C0` -> `M365-COMM-P5A-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:M365-COMM-P5A STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-COMM-P5A`
- Run ID: `p5a-enterprise-collateral-pack`
- Commit SHA: `<fill at execution time>`
- Plan refs in scope:
  - `plan:m365-enterprise-commercialization-readiness:R6`
  - `plan:m365-enterprise-commercialization-readiness:P5A`
- Invariant IDs in scope: `N/A unless an approved scope change introduces MA-governed runtime work`
- Lemma IDs in scope: `N/A unless an approved scope change introduces MA-governed runtime work`
- Owners: `product`, `engineering`, `commercialization`

## Context

- Task name: `P5A Enterprise Collateral Pack`
- Domain: `docs`
- Dependencies: P0 through P4 subphase outputs
- Allowlist:
  - `plans/m365-enterprise-commercialization-readiness/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `docs/commercialization/m365-enterprise-collateral-pack.md`
- Denylist:
  - `src/**`
  - `tests/**`
  - `docs/prompts/**`

## M - Model

- Problem: commercialization stalls if sales, security review, and delivery do not share one coherent collateral set.
- Goal: define the minimum enterprise collateral pack for the standalone M365 module.
- Success criteria:
  - product, security, and operating narrative are unified
  - collateral remains within P0 supported scope
  - delivery and sales use the same supported-action boundary
- Out of scope:
  - full marketing campaign creation
  - customer-specific customization

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `docs/commercialization/m365-enterprise-collateral-pack.md` with sections `Product Summary`, `Security and Compliance`, `Supported Action Matrix`, and `Operating Model`
- Runtime/test evidence:
  - cross-check against prior subphase outputs
- Governance evidence:
  - plan and log synchronization
- Determinism evidence:
  - repeated collateral synthesis yields the same supported boundary and posture statements

## T - Tie

- Dependency ties:
  - P0 -> supported scope
  - P1/P2/P3/P4 -> config, governance, evidence, and operations posture
- Known failure modes:
  - collateral claims exceed proven scope
  - product and security narratives diverge
- GO criteria:
  - one coherent collateral pack bounded by prior outputs
- NO-GO criteria:
  - collateral contradicts any accepted earlier subphase output

## H - Harness (ordered checks)

- `M365-COMM-P5A-C0` Preflight.
- `M365-COMM-P5A-C1` Baseline inventory of required collateral inputs from earlier subphases.
- `M365-COMM-P5A-C2` Draft product and security sections.
- `M365-COMM-P5A-C3` Draft supported-action and operating-model sections.
- `M365-COMM-P5A-C4` Schema/artifact contract validation.
- `M365-COMM-P5A-C5` Gate logic hardening: ensure collateral does not exceed earlier accepted scope.
- `M365-COMM-P5A-C6` Execute targeted cross-checks against earlier subphase artifacts.
- `M365-COMM-P5A-C7` Strict artifact validation.
- `M365-COMM-P5A-C8` Deterministic replay of collateral-scope mapping.
- `M365-COMM-P5A-C9` Hard gates (strict order):
  1. `rg -n "Product Summary|Security and Compliance|Supported Action Matrix|Operating Model" docs/commercialization/m365-enterprise-collateral-pack.md`
  2. `rg -n "plan:m365-enterprise-commercialization-readiness:P5A" plans/m365-enterprise-commercialization-readiness docs/commercialization`
  3. `git diff --check`
- `M365-COMM-P5A-C10` Governance synchronization and final decision.

## S - Stress-test

- Adversarial checks:
  - include roadmap breadth as if already supported
  - allow security narrative to ignore current audit gaps
- Replay checks:
  - supported-boundary and posture statements must match across repeated runs

## Output Contract

- Deliverables:
  - `docs/commercialization/m365-enterprise-collateral-pack.md`
- Validation results:
  - `M365-COMM-P5A-C0..C10`
- Evidence links:
  - file paths and commands only
- Residual risks:
  - customer-specific adaptation remains separate work
- Final decision lines:
  - `GATE:M365-COMM-P5A STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Collateral exceeds accepted supported scope.
- Product and security narratives conflict.
- Scope drifts into customer-specific sales customization.
