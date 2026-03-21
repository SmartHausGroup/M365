# MATHS Prompt: C2 Release Certification Packet and Decision

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:C2`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-C2-C0` -> `M365-READY-C2-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Final outputs:
  - `GATE:M365-READY-C2 STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-C2`
- Run ID: `c2-release-certification-packet-decision`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R5`
  - `plan:m365-enterprise-readiness-master-plan:C2`
- Owners: `operations`, `security`, `engineering`, `leadership`

## Context

- Domain: `docs`
- Dependency: `C1`
- Goal: convert live evidence into one explicit release decision packet.
- Allowlist:
  - `plans/m365-enterprise-readiness-master-plan/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `docs/commercialization/m365-release-gates-and-certification.md`
  - `docs/commercialization/*`
  - `configs/generated/*`
  - `artifacts/scorecards/*`
- Denylist:
  - `docs/prompts/**`

## M - Model

- Problem: live evidence alone is not sufficient unless it is assembled into one formal release decision.
- Success criteria:
  - one certification packet exists
  - evidence retention and blockers are indexed
  - final decision is explicit `GO` or `NO-GO`

## H - Harness

- `C0` confirm `C1` evidence completeness.
- `C1` assemble the certification packet structure.
- `C2` map each release gate to evidence.
- `C3` record unresolved blockers and residual risks.
- `C4` record the final `GO` or `NO-GO` decision.
- `C5` verify the decision aligns with the release-gate model.
- `C6` update tracker docs.
- `C7` run strict artifact validation.
- `C8` run `git diff --check`.
- `C9` sync plan and log.
- `C10` final gate decision.

## Validation

1. release packet covers every gate in `docs/commercialization/m365-release-gates-and-certification.md`
2. final decision is explicit and justified
3. `git diff --check`

## No-Go Triggers

- evidence is missing for a required gate
- the decision record is ambiguous
- packet and gate model disagree
