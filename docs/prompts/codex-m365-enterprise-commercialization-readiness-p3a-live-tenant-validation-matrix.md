# MATHS Prompt: P3A Live-Tenant Validation Matrix

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-commercialization-readiness:P3A`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-COMM-P3A-C0` -> `M365-COMM-P3A-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:M365-COMM-P3A STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-COMM-P3A`
- Run ID: `p3a-live-tenant-validation-matrix`
- Commit SHA: `<fill at execution time>`
- Plan refs in scope:
  - `plan:m365-enterprise-commercialization-readiness:R4`
  - `plan:m365-enterprise-commercialization-readiness:P3A`
- Invariant IDs in scope: `INV-CAIO-M365-001`, `INV-CAIO-M365-002`, `INV-CAIO-M365-003`, `INV-M365-AUDIT-001`
- Lemma IDs in scope: `L1`, `L2`, `L3`, `L4`
- Owners: `engineering`, `security`, `qa`

## Context

- Task name: `P3A Live-Tenant Validation Matrix`
- Domain: `docs`
- Dependencies: current generated verification artifacts and MA contract docs
- Allowlist:
  - `plans/m365-enterprise-commercialization-readiness/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `docs/contracts/**`
  - `docs/M365_MA_INDEX.md`
  - `configs/generated/*.json`
  - `docs/commercialization/m365-live-tenant-validation-matrix.md`
- Denylist:
  - `src/**`
  - `tests/**`
  - `docs/prompts/**`

## M - Model

- Problem: enterprise release claims are weak if mock validation and live-tenant validation are not separated.
- Goal: define the required live-tenant validation matrix and evidence expectations.
- Success criteria:
  - each enterprise-critical behavior is classified as mock-only, live-required, or both
  - prerequisites and evidence artifacts are explicit
  - unsupported live claims are blocked
- Out of scope:
  - running live validations
  - modifying verification scripts

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `docs/commercialization/m365-live-tenant-validation-matrix.md` with sections `Capability`, `Validation Mode`, `Prerequisites`, `Evidence Artifact`, and `Release Use`
- Runtime/test evidence:
  - `rg -n "mock pass|no BASE_URL|auth_pass|idempotency_pass|audit_pass" configs/generated/*.json`
- Governance evidence:
  - plan and log synchronization
- Determinism evidence:
  - repeated classification of artifact trust level yields the same matrix for fixed repository state

## T - Tie

- Dependency ties:
  - generated artifacts -> current validation signals
  - MA docs -> contract boundaries for auth, idempotency, audit, and postcondition
- Known failure modes:
  - mock-passing artifacts are treated as enterprise certification
  - prerequisites for live validation are omitted
- GO criteria:
  - matrix cleanly separates mock and live evidence requirements
- NO-GO criteria:
  - enterprise-critical behavior lacks a validation-mode classification

## H - Harness (ordered checks)

- `M365-COMM-P3A-C0` Preflight.
- `M365-COMM-P3A-C1` Baseline inventory of current verification artifacts.
- `M365-COMM-P3A-C2` Draft validation-mode and prerequisite sections.
- `M365-COMM-P3A-C3` Draft evidence-artifact and release-use sections.
- `M365-COMM-P3A-C4` Schema/artifact contract validation.
- `M365-COMM-P3A-C5` Gate logic hardening: ensure no mock-only artifact is listed as sufficient for enterprise release.
- `M365-COMM-P3A-C6` Execute targeted `rg` validations.
- `M365-COMM-P3A-C7` Strict artifact validation: fail if any enterprise-critical capability lacks live-evidence treatment.
- `M365-COMM-P3A-C8` Deterministic replay of validation-mode classification.
- `M365-COMM-P3A-C9` Hard gates (strict order):
  1. `rg -n "Capability|Validation Mode|Prerequisites|Evidence Artifact|Release Use" docs/commercialization/m365-live-tenant-validation-matrix.md`
  2. `rg -n "plan:m365-enterprise-commercialization-readiness:P3A" plans/m365-enterprise-commercialization-readiness docs/commercialization`
  3. `git diff --check`
- `M365-COMM-P3A-C10` Governance synchronization and final decision.

## S - Stress-test

- Adversarial checks:
  - mark a mock-only artifact as release sufficient
  - forget to state prerequisites for live tenant validation
- Replay checks:
  - validation-mode assignments must match across repeated runs

## Output Contract

- Deliverables:
  - `docs/commercialization/m365-live-tenant-validation-matrix.md`
- Validation results:
  - `M365-COMM-P3A-C0..C10`
- Evidence links:
  - file paths and commands only
- Residual risks:
  - actual live execution remains a separate approved activity
- Final decision lines:
  - `GATE:M365-COMM-P3A STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Any enterprise-critical capability lacks a live-evidence classification.
- Mock evidence is presented as enterprise acceptance.
- Scope drifts into test execution.
