# MATHS Prompt: P4B Operator Onboarding, Runbooks, and Support Boundary

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-commercialization-readiness:P4B`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-COMM-P4B-C0` -> `M365-COMM-P4B-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:M365-COMM-P4B STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-COMM-P4B`
- Run ID: `p4b-onboarding-runbooks-support-boundary`
- Commit SHA: `<fill at execution time>`
- Plan refs in scope:
  - `plan:m365-enterprise-commercialization-readiness:R5`
  - `plan:m365-enterprise-commercialization-readiness:P4B`
- Invariant IDs in scope: `N/A unless an approved scope change introduces MA-governed runtime work`
- Lemma IDs in scope: `N/A unless an approved scope change introduces MA-governed runtime work`
- Owners: `operations`, `engineering`, `support`

## Context

- Task name: `P4B Operator Onboarding, Runbooks, and Support Boundary`
- Domain: `docs`
- Dependencies: P4A install/bootstrap path
- Allowlist:
  - `plans/m365-enterprise-commercialization-readiness/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `docs/commercialization/m365-operator-onboarding-and-support-boundary.md`
- Denylist:
  - `src/**`
  - `tests/**`
  - `docs/prompts/**`

## M - Model

- Problem: after installation, operators still need deterministic onboarding, runbooks, and support boundaries.
- Goal: define the day-0/day-1 operator experience and ownership model.
- Success criteria:
  - onboarding checklist is explicit
  - runbooks are explicit
  - support boundary and escalation path are explicit
- Out of scope:
  - creating support tooling
  - operational staffing decisions beyond ownership boundaries

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `docs/commercialization/m365-operator-onboarding-and-support-boundary.md` with sections `Onboarding Checklist`, `Runbooks`, `Support Boundary`, `Escalation Path`, and `Ownership Matrix`
- Runtime/test evidence:
  - reference P4A install and bootstrap outputs
- Governance evidence:
  - plan and log synchronization
- Determinism evidence:
  - repeated ownership and escalation classification yields the same boundary model

## T - Tie

- Dependency ties:
  - P4A -> install/bootstrap preconditions for operator onboarding
- Known failure modes:
  - onboarding assumes undocumented prior knowledge
  - support boundary is vague, causing SmartHaus service bleed
- GO criteria:
  - operator path is explicit and support ownership is bounded
- NO-GO criteria:
  - ownership or escalation remains ambiguous

## H - Harness (ordered checks)

- `M365-COMM-P4B-C0` Preflight.
- `M365-COMM-P4B-C1` Baseline inventory of operator tasks implied by the current install path.
- `M365-COMM-P4B-C2` Draft onboarding and runbook sections.
- `M365-COMM-P4B-C3` Draft support-boundary and escalation sections.
- `M365-COMM-P4B-C4` Schema/artifact contract validation.
- `M365-COMM-P4B-C5` Gate logic hardening: ensure every operator duty has an owner.
- `M365-COMM-P4B-C6` Execute targeted cross-checks against P4A outputs.
- `M365-COMM-P4B-C7` Strict artifact validation.
- `M365-COMM-P4B-C8` Deterministic replay of the ownership matrix.
- `M365-COMM-P4B-C9` Hard gates (strict order):
  1. `rg -n "Onboarding Checklist|Runbooks|Support Boundary|Escalation Path|Ownership Matrix" docs/commercialization/m365-operator-onboarding-and-support-boundary.md`
  2. `rg -n "plan:m365-enterprise-commercialization-readiness:P4B" plans/m365-enterprise-commercialization-readiness docs/commercialization`
  3. `git diff --check`
- `M365-COMM-P4B-C10` Governance synchronization and final decision.

## S - Stress-test

- Adversarial checks:
  - leave one operator responsibility without an owner
  - define support boundaries in vague sales language
- Replay checks:
  - ownership matrix and escalation path must match across repeated runs

## Output Contract

- Deliverables:
  - `docs/commercialization/m365-operator-onboarding-and-support-boundary.md`
- Validation results:
  - `M365-COMM-P4B-C0..C10`
- Evidence links:
  - file paths and commands only
- Residual risks:
  - support staffing still requires business approval outside this repo
- Final decision lines:
  - `GATE:M365-COMM-P4B STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Any operator duty lacks an owner.
- Support boundary is vague or open-ended.
- Scope drifts into non-documented operational execution.
