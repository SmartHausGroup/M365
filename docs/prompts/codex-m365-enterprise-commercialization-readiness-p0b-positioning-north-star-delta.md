# MATHS Prompt: P0B Buyer and Operator Positioning and North Star Delta

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-commercialization-readiness:P0B`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-COMM-P0B-C0` -> `M365-COMM-P0B-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:M365-COMM-P0B STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-COMM-P0B`
- Run ID: `p0b-positioning-north-star-delta`
- Commit SHA: `<fill at execution time>`
- Plan refs in scope:
  - `plan:m365-enterprise-commercialization-readiness:R6`
  - `plan:m365-enterprise-commercialization-readiness:P0B`
- Invariant IDs in scope: `N/A unless an approved scope change introduces MA-governed runtime work`
- Lemma IDs in scope: `N/A unless an approved scope change introduces MA-governed runtime work`
- Owners: `product`, `engineering`, `commercialization`

## Context

- Task name: `P0B Buyer and Operator Positioning and North Star Delta`
- Domain: `docs`
- Dependencies: P0A supported surface lock, current North Star, licensed-module model
- Allowlist:
  - `plans/m365-enterprise-commercialization-readiness/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/NORTHSTAR.md`
  - `docs/TAI_LICENSED_MODULE_MODEL.md`
  - `docs/commercialization/m365-v1-positioning-and-north-star-delta.md`
- Denylist:
  - `src/**`
  - `tests/**`
  - `configs/generated/**`
  - `docs/prompts/**`

## M - Model

- Problem: the standalone M365 module does not yet have a locked buyer, operator, or North Star sync rule.
- Goal: define who buys it, who runs it, how it is positioned, and whether North Star must change.
- Success criteria:
  - target buyer and operator are explicit
  - standalone positioning is consistent with the supported v1 surface
  - a clear North Star update decision is documented
- Out of scope:
  - changing runtime code
  - broad GTM strategy beyond the standalone module

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `docs/commercialization/m365-v1-positioning-and-north-star-delta.md` with sections `Target Buyer`, `Target Operator`, `Positioning`, `Deployment Model`, and `North Star Delta`
- Runtime/test evidence:
  - `rg -n "self-service|maintenance-only|production-ready|zero extra software cost" Operations/NORTHSTAR.md`
- Governance evidence:
  - if North Star requires change, list the required edits explicitly before execution
- Determinism evidence:
  - repeated evaluation yields the same update/no-update decision for fixed repository state and supported surface

## T - Tie

- Dependency ties:
  - `P0A` -> supported surface constrains positioning
  - `Operations/NORTHSTAR.md` -> governing product definition
  - `docs/TAI_LICENSED_MODULE_MODEL.md` -> module packaging language
- Known failure modes:
  - positioning assumes unsupported capabilities
  - North Star drift is identified but not synchronized
- GO criteria:
  - positioning is narrow, evidence-backed, and North Star impact is explicit
- NO-GO criteria:
  - unresolved contradiction between positioning and current North Star

## H - Harness (ordered checks)

- `M365-COMM-P0B-C0` Preflight.
- `M365-COMM-P0B-C1` Baseline inventory of current North Star and product-positioning language.
- `M365-COMM-P0B-C2` Draft buyer and operator definition.
- `M365-COMM-P0B-C3` Draft positioning and deployment-model statement.
- `M365-COMM-P0B-C4` Schema/artifact contract: verify required document sections.
- `M365-COMM-P0B-C5` Gate logic hardening: ensure positioning does not exceed P0A supported surface.
- `M365-COMM-P0B-C6` Execute targeted validations with `rg` against North Star and module-model docs.
- `M365-COMM-P0B-C7` Strict artifact validation: fail if North Star delta is ambiguous.
- `M365-COMM-P0B-C8` Deterministic replay of the update/no-update decision.
- `M365-COMM-P0B-C9` Hard gates (strict order):
  1. `rg -n "Target Buyer|Target Operator|Positioning|Deployment Model|North Star Delta" docs/commercialization/m365-v1-positioning-and-north-star-delta.md`
  2. `rg -n "plan:m365-enterprise-commercialization-readiness:P0B" plans/m365-enterprise-commercialization-readiness docs/commercialization`
  3. `git diff --check`
- `M365-COMM-P0B-C10` Governance synchronization and final decision.

## S - Stress-test

- Adversarial checks:
  - position the module as broader than P0A allows
  - identify a North Star delta but fail to specify what changes
- Replay checks:
  - the buyer/operator definition and North Star update decision must match across repeated runs

## Output Contract

- Deliverables:
  - `docs/commercialization/m365-v1-positioning-and-north-star-delta.md`
- Validation results:
  - `M365-COMM-P0B-C0..C10`
- Evidence links:
  - file paths and commands only
- Residual risks:
  - future feature expansion may require another North Star sync pass
- Final decision lines:
  - `GATE:M365-COMM-P0B STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Buyer or operator definition depends on unsupported capabilities.
- North Star delta is detected but not made explicit.
- Scope drifts into runtime or sales-operations implementation.
