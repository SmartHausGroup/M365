# MATHS Prompt: P2A Audit and Governance Evidence Model

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-commercialization-readiness:P2A`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-COMM-P2A-C0` -> `M365-COMM-P2A-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:M365-COMM-P2A STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-COMM-P2A`
- Run ID: `p2a-audit-governance-evidence-model`
- Commit SHA: `<fill at execution time>`
- Plan refs in scope:
  - `plan:m365-enterprise-commercialization-readiness:R3`
  - `plan:m365-enterprise-commercialization-readiness:P2A`
- Invariant IDs in scope: `N/A unless an approved scope change introduces MA-governed runtime work`
- Lemma IDs in scope: `N/A unless an approved scope change introduces MA-governed runtime work`
- Owners: `engineering`, `security`, `governance`

## Context

- Task name: `P2A Audit and Governance Evidence Model`
- Domain: `docs`
- Dependencies: current audit surfaces, approval flows, and admin inspection behavior
- Allowlist:
  - `plans/m365-enterprise-commercialization-readiness/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `src/ops_adapter/actions.py`
  - `src/ops_adapter/audit.py`
  - `src/provisioning_api/audit.py`
  - `docs/contracts/**`
  - `docs/commercialization/m365-audit-and-governance-evidence-model.md`
- Denylist:
  - `tests/**`
  - `configs/generated/**`
  - `docs/prompts/**`

## M - Model

- Problem: enterprise commercialization requires explicit audit and governance evidence expectations, not partial or implied behavior.
- Goal: define the audit-event and governance-evidence model the M365 runtime must satisfy.
- Success criteria:
  - required audit events are named
  - governance evidence expectations are explicit
  - current snapshot or partial surfaces are identified as gaps
- Out of scope:
  - implementing audit persistence
  - changing runtime code

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `docs/commercialization/m365-audit-and-governance-evidence-model.md` with sections `Required Audit Events`, `Governance Evidence`, `Current Gaps`, and `Enterprise Acceptance Expectations`
- Runtime/test evidence:
  - `rg -n "audit|snapshot_mode|approval|trace" src/ops_adapter src/provisioning_api docs/contracts`
- Governance evidence:
  - plan and log synchronization
- Determinism evidence:
  - repeated gap classification produces the same required-event set for fixed repository state

## T - Tie

- Dependency ties:
  - audit code paths -> current evidence sources
  - contract docs -> formal current guarantees
- Known failure modes:
  - snapshot inspection is treated as full audit
  - enterprise acceptance does not state minimum evidence
- GO criteria:
  - audit-event model and governance-evidence model are explicit and gap-aware
- NO-GO criteria:
  - enterprise audit posture remains implied rather than documented

## H - Harness (ordered checks)

- `M365-COMM-P2A-C0` Preflight.
- `M365-COMM-P2A-C1` Baseline inventory of audit and governance surfaces.
- `M365-COMM-P2A-C2` Draft required audit-events section.
- `M365-COMM-P2A-C3` Draft governance-evidence and current-gaps sections.
- `M365-COMM-P2A-C4` Schema/artifact contract validation.
- `M365-COMM-P2A-C5` Gate logic hardening: ensure current-state gaps are not hidden inside acceptance language.
- `M365-COMM-P2A-C6` Execute targeted `rg` validations.
- `M365-COMM-P2A-C7` Strict artifact validation: fail if a required enterprise audit expectation has no mapped source or explicit gap.
- `M365-COMM-P2A-C8` Deterministic replay of gap classification.
- `M365-COMM-P2A-C9` Hard gates (strict order):
  1. `rg -n "Required Audit Events|Governance Evidence|Current Gaps|Enterprise Acceptance Expectations" docs/commercialization/m365-audit-and-governance-evidence-model.md`
  2. `rg -n "plan:m365-enterprise-commercialization-readiness:P2A" plans/m365-enterprise-commercialization-readiness docs/commercialization`
  3. `git diff --check`
- `M365-COMM-P2A-C10` Governance synchronization and final decision.

## S - Stress-test

- Adversarial checks:
  - classify snapshot mode as enterprise-ready audit
  - omit a governance-evidence gap because it is commercially inconvenient
- Replay checks:
  - required-event and gap lists must match across repeated runs

## Output Contract

- Deliverables:
  - `docs/commercialization/m365-audit-and-governance-evidence-model.md`
- Validation results:
  - `M365-COMM-P2A-C0..C10`
- Evidence links:
  - file paths and commands only
- Residual risks:
  - implementation hardening is deferred to later approved work
- Final decision lines:
  - `GATE:M365-COMM-P2A STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Snapshot or partial audit surfaces are presented as sufficient without qualification.
- Required enterprise evidence remains undefined.
- Scope drifts into implementation or remediation.
