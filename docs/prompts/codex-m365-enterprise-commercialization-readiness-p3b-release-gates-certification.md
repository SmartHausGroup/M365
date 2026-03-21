# MATHS Prompt: P3B Release Gates and Certification Decision Model

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-commercialization-readiness:P3B`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-COMM-P3B-C0` -> `M365-COMM-P3B-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:M365-COMM-P3B STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-COMM-P3B`
- Run ID: `p3b-release-gates-certification`
- Commit SHA: `<fill at execution time>`
- Plan refs in scope:
  - `plan:m365-enterprise-commercialization-readiness:R4`
  - `plan:m365-enterprise-commercialization-readiness:P3B`
- Invariant IDs in scope: `INV-CAIO-M365-001`, `INV-CAIO-M365-002`, `INV-CAIO-M365-003`, `INV-M365-AUDIT-001`
- Lemma IDs in scope: `L1`, `L2`, `L3`, `L4`
- Owners: `engineering`, `security`, `release`

## Context

- Task name: `P3B Release Gates and Certification Decision Model`
- Domain: `docs`
- Dependencies: P3A validation matrix
- Allowlist:
  - `plans/m365-enterprise-commercialization-readiness/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `docs/commercialization/m365-live-tenant-validation-matrix.md`
  - `docs/commercialization/m365-release-gates-and-certification.md`
- Denylist:
  - `src/**`
  - `tests/**`
  - `docs/prompts/**`

## M - Model

- Problem: even with a validation matrix, enterprise readiness needs explicit go / no-go release gates.
- Goal: define the release-gate and certification decision model.
- Success criteria:
  - release gates are explicit and ordered
  - go / no-go criteria are explicit
  - evidence retention requirements are explicit
- Out of scope:
  - performing a release
  - modifying runtime code

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `docs/commercialization/m365-release-gates-and-certification.md` with sections `Release Gates`, `GO Criteria`, `NO-GO Criteria`, and `Evidence Retention`
- Runtime/test evidence:
  - reference P3A matrix and current MA artifacts
- Governance evidence:
  - plan and log synchronization
- Determinism evidence:
  - repeated gate evaluation for a fixed evidence set yields the same release decision

## T - Tie

- Dependency ties:
  - P3A -> validation matrix feeds gate decisions
  - MA artifacts -> current evidence sources
- Known failure modes:
  - release decision relies on undefined evidence
  - evidence-retention expectations are omitted
- GO criteria:
  - gate sequence, go criteria, and no-go criteria are explicit and ordered
- NO-GO criteria:
  - any release gate depends on undefined evidence

## H - Harness (ordered checks)

- `M365-COMM-P3B-C0` Preflight.
- `M365-COMM-P3B-C1` Baseline inventory of current evidence types.
- `M365-COMM-P3B-C2` Draft release-gate sequence.
- `M365-COMM-P3B-C3` Draft go / no-go and evidence-retention sections.
- `M365-COMM-P3B-C4` Schema/artifact contract validation.
- `M365-COMM-P3B-C5` Gate logic hardening: ensure no release gate can pass with mock-only evidence where live evidence is required.
- `M365-COMM-P3B-C6` Execute targeted cross-checks against P3A.
- `M365-COMM-P3B-C7` Strict artifact validation.
- `M365-COMM-P3B-C8` Deterministic replay of release-decision logic.
- `M365-COMM-P3B-C9` Hard gates (strict order):
  1. `rg -n "Release Gates|GO Criteria|NO-GO Criteria|Evidence Retention" docs/commercialization/m365-release-gates-and-certification.md`
  2. `rg -n "plan:m365-enterprise-commercialization-readiness:P3B" plans/m365-enterprise-commercialization-readiness docs/commercialization`
  3. `git diff --check`
- `M365-COMM-P3B-C10` Governance synchronization and final decision.

## S - Stress-test

- Adversarial checks:
  - permit certification with incomplete live-evidence gates
  - define gates with no evidence-retention rule
- Replay checks:
  - gate ordering and decision criteria must match across repeated runs

## Output Contract

- Deliverables:
  - `docs/commercialization/m365-release-gates-and-certification.md`
- Validation results:
  - `M365-COMM-P3B-C0..C10`
- Evidence links:
  - file paths and commands only
- Residual risks:
  - actual certification execution remains separately approved work
- Final decision lines:
  - `GATE:M365-COMM-P3B STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Any gate is undefined or unordered.
- Mock evidence is accepted where live evidence is required.
- Scope drifts into release execution.
