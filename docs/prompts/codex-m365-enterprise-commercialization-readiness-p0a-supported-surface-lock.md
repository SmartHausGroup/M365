# MATHS Prompt: P0A Supported Surface and Non-Goals Lock

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-commercialization-readiness:P0A`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-COMM-P0A-C0` -> `M365-COMM-P0A-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:M365-COMM-P0A STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-COMM-P0A`
- Run ID: `p0a-supported-surface-lock`
- Commit SHA: `<fill at execution time>`
- Plan refs in scope:
  - `plan:m365-enterprise-commercialization-readiness:R1`
  - `plan:m365-enterprise-commercialization-readiness:P0A`
- Invariant IDs in scope: `N/A unless an approved scope change introduces MA-governed runtime work`
- Lemma IDs in scope: `N/A unless an approved scope change introduces MA-governed runtime work`
- Owners: `product`, `engineering`, `commercialization`

## Context

- Task name: `P0A Supported Surface and Non-Goals Lock`
- Domain: `docs`
- Dependencies: current M365 MA surface, capability registry, licensed-module model, execution plan
- Allowlist:
  - `plans/m365-enterprise-commercialization-readiness/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/NORTHSTAR.md`
  - `docs/M365_MA_INDEX.md`
  - `docs/contracts/**`
  - `registry/capability_registry.yaml`
  - `docs/TAI_LICENSED_MODULE_MODEL.md`
  - `docs/commercialization/m365-v1-supported-surface.md`
- Denylist:
  - `src/**`
  - `tests/**`
  - `configs/generated/**`
  - `docs/prompts/**`

## M - Model

- Problem: product claims can drift beyond the currently proven M365 v1 surface.
- Goal: define the exact supported and unsupported action boundary for standalone M365 v1.
- Success criteria:
  - supported actions are explicitly listed and tied to evidence
  - unsupported actions are explicitly listed with non-goal language
  - product-claim language does not exceed current proof and implementation scope
- Out of scope:
  - adding new actions
  - changing runtime behavior

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `docs/commercialization/m365-v1-supported-surface.md` with sections `Supported Actions`, `Unsupported Actions`, `Evidence Sources`, and `Product Claim Boundary`
- Runtime/test evidence:
  - `rg -n "implemented|planned|260|9 implemented" docs/M365_MA_INDEX.md registry/capability_registry.yaml`
- Governance evidence:
  - updated plan artifacts and action-log entry
- Determinism evidence:
  - repeated read of the supported-action matrix yields the same action set for the same repository state

## T - Tie

- Dependency ties:
  - `docs/M365_MA_INDEX.md` -> implemented versus planned action count
  - `registry/capability_registry.yaml` -> canonical action universe status
  - `docs/contracts/**` -> formal proof boundary for currently supported behavior
- Known failure modes:
  - marketing language exceeds proven scope
  - unsupported actions remain implied by omission
- GO criteria:
  - supported and unsupported boundaries are explicit and evidence-backed
- NO-GO criteria:
  - any claimed supported action lacks a current evidence path

## H - Harness (ordered checks)

- `M365-COMM-P0A-C0` Preflight: verify governance docs, plan refs, and current phase status.
- `M365-COMM-P0A-C1` Baseline inventory: capture the current supported/proven surface from repo artifacts.
- `M365-COMM-P0A-C2` Draft supported-actions section.
- `M365-COMM-P0A-C3` Draft unsupported-actions and non-goals section.
- `M365-COMM-P0A-C4` Schema/artifact contract: verify required document sections exist.
- `M365-COMM-P0A-C5` Gate logic hardening: ensure every supported action maps to a proof or implementation source.
- `M365-COMM-P0A-C6` Execute targeted validations: run `rg` consistency checks against source artifacts.
- `M365-COMM-P0A-C7` Strict artifact validation: fail if any supported action is unsupported by evidence.
- `M365-COMM-P0A-C8` Deterministic replay: repeat the action-set extraction and require identical output.
- `M365-COMM-P0A-C9` Hard gates (strict order):
  1. `rg -n "plan:m365-enterprise-commercialization-readiness:P0A" plans/m365-enterprise-commercialization-readiness docs/commercialization`
  2. `rg -n "Supported Actions|Unsupported Actions|Evidence Sources|Product Claim Boundary" docs/commercialization/m365-v1-supported-surface.md`
  3. `git diff --check`
- `M365-COMM-P0A-C10` Governance synchronization and final decision.

## S - Stress-test

- Adversarial checks:
  - include an action present in the universe but not implemented
  - omit a non-goal and see whether the product claim becomes ambiguous
- Replay checks:
  - the supported-action matrix and evidence-source mapping must match across two runs on fixed repository state

## Output Contract

- Deliverables:
  - `docs/commercialization/m365-v1-supported-surface.md`
- Validation results:
  - `M365-COMM-P0A-C0..C10`
- Evidence links:
  - file paths and commands only
- Residual risks:
  - unsupported breadth remains roadmap, not launch scope
- Final decision lines:
  - `GATE:M365-COMM-P0A STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Any supported action lacks repository evidence.
- Any unsupported action remains ambiguously implied.
- Missing plan ref or governance synchronization.
- Scope drift into runtime implementation.
