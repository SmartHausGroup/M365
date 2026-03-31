# MATHS Prompt: M365 Service-Mode Token Acquisition Remediation

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-service-mode-token-acquisition-remediation:R1`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Approval and Governance Gates

1. **Present the approval packet first** — before executing any check, summarize the current next act, the cross-repo dependency boundary, and the intended action surface.
2. **Wait for explicit "go"** — do not begin execution until the operator confirms with "go".
3. **Call MCP `validate_action` before any mutating action** — before writing, editing, or creating any file, call `validate_action` and obey the verdict. If the verdict is not `allowed`, stop immediately.
4. **Stop on first red** — if any check emits `FAIL` or `BLOCKED`, stop the entire phase. Do not continue to subsequent checks.
5. **Do not auto-advance to the next phase** — even if a child phase emits GO, the next child phase requires its own approval packet and "go" confirmation.

## Parent Coordination Rule

This prompt is the parent coordination surface for the remaining M365-side service-mode initiative.

- It may identify the current next act and the correct dependency order.
- It may restate which remaining work belongs to M365 versus UCP.
- It must hand execution to exactly one approved child phase prompt.
- It must not claim ownership of the sibling UCP consumer-side validation or acceptance acts.

## Cross-Repo Boundary

- M365 owns service-runtime readiness/health, token-provider diagnosis, token-provider repair, live token-acquisition classification, and M365-local acceptance under `plan:m365-service-mode-token-acquisition-remediation`.
- UCP owns the consumer-side `plan:ucp-m365-token-acquisition-validation` and `plan:ucp-m365-service-mode-end-to-end-acceptance` acts after the M365-side runtime path is green in the intended launch posture.
- Neither repo may silently absorb the other repo's remaining authority.

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-SERVICE-MODE-PARENT`
- Run ID: `m365-service-mode-token-acquisition-remediation`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-service-mode-token-acquisition-remediation:R1`
  - `plan:m365-service-mode-token-acquisition-remediation:R8`
  - `plan:m365-service-mode-token-acquisition-remediation:R9`
  - `plan:m365-service-mode-token-acquisition-remediation:R10`

## Context

- Task name: `Coordinate the remaining M365-side service-mode runtime/token initiative without repo-authority drift`
- Domain: `governance`
- Dependencies:
  - `AGENTS.md`
  - `Operations/NORTHSTAR.md`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
  - `plans/m365-service-mode-token-acquisition-remediation/m365-service-mode-token-acquisition-remediation.md`
  - `plans/m365-service-runtime-readiness-and-health/m365-service-runtime-readiness-and-health.md`
  - `plans/m365-token-provider-path-diagnosis/m365-token-provider-path-diagnosis.md`
  - `plans/m365-token-provider-runtime-repair/m365-token-provider-runtime-repair.md`
  - `plans/m365-live-token-acquisition-classification/m365-live-token-acquisition-classification.md`
  - `plans/m365-service-mode-end-to-end-acceptance/m365-service-mode-end-to-end-acceptance.md`
  - `../UCP/docs/platform/EXECUTION_PLAN.md`
  - `../UCP/plans/ucp-m365-service-mode-runtime-remediation/ucp-m365-service-mode-runtime-remediation.md`
- Allowlist:
  - `plans/m365-service-mode-token-acquisition-remediation/**`
  - `docs/prompts/codex-m365-service-mode-token-acquisition-remediation.md`
  - `docs/prompts/codex-m365-service-mode-token-acquisition-remediation-prompt.txt`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
- Denylist:
  - `src/**`
  - `tests/**`
  - `../UCP/src/**`
  - `../UCP/tests/**`

## M - Model

- Problem: `The remaining M365-side service-mode runtime work must stay governed in this repo while the sibling UCP repo keeps only the consumer-side validation and acceptance acts.`
- Goal: `Keep the current next act, the cross-repo dependency order, and the repo-authority split explicit and fail-closed.`
- Success criteria:
  - `Current next act is explicit.`
  - `Cross-repo boundary is explicit.`
  - `The parent prompt does not skip child-phase gates.`

## A - Annotate

- Artifact/schema evidence:
  - `parent initiative plan plus child-phase plans`
- Governance evidence:
  - `execution plan, action log, and project file index`
- Cross-repo evidence:
  - `sibling UCP parent plan and Track R execution-plan text`
- Determinism evidence:
  - `for fixed governance state, the same next act and authority split are reported`

## T - Tie

- Dependency ties:
  - `M365-side runtime path must be green before UCP-side consumer validation can be truthfully advanced.`
- Known failure modes:
  - `repo-authority drift`
  - `parent prompt claiming child execution authority`
  - `UCP-side consumer validation being treated as M365-owned`
- GO criteria:
  - `the current next act and repo-authority split are explicit and truthful`
- NO-GO criteria:
  - `the boundary is still ambiguous or the prompt attempts to auto-advance`

## H - Harness (ordered checks)

`M365-SERVICE-MODE-PARENT-C0` Governance readback
- Read the parent plan, execution plan, action log, project file index, and sibling UCP Track R surfaces.

`M365-SERVICE-MODE-PARENT-C1` Current-next-act confirmation
- Identify the current next M365 child act from governance state.

`M365-SERVICE-MODE-PARENT-C2` Cross-repo dependency confirmation
- Restate which remaining acts belong to M365 and which belong to UCP.

`M365-SERVICE-MODE-PARENT-C3` Approval packet
- Present the approval packet for the correct child prompt only.

`M365-SERVICE-MODE-PARENT-C4` Stop condition
- Stop after the coordination response unless the operator explicitly approves the child phase.

## S - Stress-test

- Adversarial checks:
  - `If the parent prompt tries to execute runtime repair directly, fail.`
  - `If the parent prompt claims UCP-side consumer validation is M365-owned, fail.`
- Replay checks:
  - `Repeated governance readback must identify the same next act and authority split.`

## Output Contract

- Deliverables:
  - `current next act`
  - `cross-repo boundary statement`
  - `approved child-phase handoff only`
- Final decision lines:
  - `GATE:M365-SERVICE-MODE-PARENT STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Current next act is ambiguous.
- Cross-repo ownership is ambiguous.
- The response skips directly into child execution without a new approval packet.
