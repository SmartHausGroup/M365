# MATHS Prompt: P2B Permission, Approval, and Fail-Closed Hardening

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-commercialization-readiness:P2B`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-COMM-P2B-C0` -> `M365-COMM-P2B-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:M365-COMM-P2B STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-COMM-P2B`
- Run ID: `p2b-approval-fail-closed-hardening`
- Commit SHA: `<fill at execution time>`
- Plan refs in scope:
  - `plan:m365-enterprise-commercialization-readiness:R3`
  - `plan:m365-enterprise-commercialization-readiness:P2B`
- Invariant IDs in scope: `N/A unless an approved scope change introduces MA-governed runtime work`
- Lemma IDs in scope: `N/A unless an approved scope change introduces MA-governed runtime work`
- Owners: `engineering`, `security`, `governance`

## Context

- Task name: `P2B Permission, Approval, and Fail-Closed Hardening`
- Domain: `docs`
- Dependencies: permission-tier registry, approvals, mutation gates, governance expectations
- Allowlist:
  - `plans/m365-enterprise-commercialization-readiness/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `registry/permission_tiers.yaml`
  - `src/smarthaus_common/permission_enforcer.py`
  - `src/ops_adapter/approvals.py`
  - `src/provisioning_api/routers/m365.py`
  - `docs/commercialization/m365-permission-approval-fail-closed-hardening.md`
- Denylist:
  - `tests/**`
  - `configs/generated/**`
  - `docs/prompts/**`

## M - Model

- Problem: enterprise buyers need explicit permission, approval, and fail-closed posture, not inferred behavior.
- Goal: define the hardening checklist and decision rules for permissions, approvals, and fail-closed operation.
- Success criteria:
  - permission and approval boundaries are explicit
  - fail-closed expectations are explicit
  - exception handling is governed rather than implied
- Out of scope:
  - implementing enforcement changes
  - changing tenant permissions

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `docs/commercialization/m365-permission-approval-fail-closed-hardening.md` with sections `Permission Tiers`, `Approval Boundaries`, `Fail-Closed Rules`, and `Exceptions and Escalations`
- Runtime/test evidence:
  - `rg -n "permission|approval|ALLOW_M365_MUTATIONS|fail" registry src`
- Governance evidence:
  - plan and log synchronization
- Determinism evidence:
  - repeated classification of each high-risk action yields the same approval and fail-closed expectation

## T - Tie

- Dependency ties:
  - permission tiers -> action eligibility model
  - approvals and mutation gates -> high-risk control path
- Known failure modes:
  - high-risk actions lack explicit approval ownership
  - fail-open cases remain undocumented
- GO criteria:
  - permission, approval, and fail-closed expectations are explicit and internally consistent
- NO-GO criteria:
  - any high-risk path lacks a documented control boundary

## H - Harness (ordered checks)

- `M365-COMM-P2B-C0` Preflight.
- `M365-COMM-P2B-C1` Baseline inventory of permission, approval, and mutation controls.
- `M365-COMM-P2B-C2` Draft permission-tier and approval-boundary sections.
- `M365-COMM-P2B-C3` Draft fail-closed rules and exception path.
- `M365-COMM-P2B-C4` Schema/artifact contract validation.
- `M365-COMM-P2B-C5` Gate logic hardening: ensure no high-risk action is left without a control boundary.
- `M365-COMM-P2B-C6` Execute targeted `rg` validations.
- `M365-COMM-P2B-C7` Strict artifact validation: fail if any exception path is undocumented.
- `M365-COMM-P2B-C8` Deterministic replay of the control-boundary classification.
- `M365-COMM-P2B-C9` Hard gates (strict order):
  1. `rg -n "Permission Tiers|Approval Boundaries|Fail-Closed Rules|Exceptions and Escalations" docs/commercialization/m365-permission-approval-fail-closed-hardening.md`
  2. `rg -n "plan:m365-enterprise-commercialization-readiness:P2B" plans/m365-enterprise-commercialization-readiness docs/commercialization`
  3. `git diff --check`
- `M365-COMM-P2B-C10` Governance synchronization and final decision.

## S - Stress-test

- Adversarial checks:
  - leave a critical action outside explicit approval scope
  - describe a failure case without defining whether it fails open or closed
- Replay checks:
  - control-boundary classifications must match across repeated runs

## Output Contract

- Deliverables:
  - `docs/commercialization/m365-permission-approval-fail-closed-hardening.md`
- Validation results:
  - `M365-COMM-P2B-C0..C10`
- Evidence links:
  - file paths and commands only
- Residual risks:
  - runtime remediation work remains separate from this documentation pass
- Final decision lines:
  - `GATE:M365-COMM-P2B STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Any high-risk action lacks a defined permission or approval boundary.
- Fail-closed behavior remains ambiguous.
- Scope drifts into implementation.
