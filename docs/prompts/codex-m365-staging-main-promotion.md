# MATHS Prompt: P1 Branch Promotion to Staging and Main

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-post-expansion-promotion-and-persona-activation:P1A`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-PROMOTION-P1-C0` -> `M365-PROMOTION-P1-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:M365-PROMOTION-P1 STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-PROMOTION-P1`
- Run ID: `staging-main-promotion`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-post-expansion-promotion-and-persona-activation:R1`
  - `plan:m365-post-expansion-promotion-and-persona-activation:R6`
  - `plan:m365-post-expansion-promotion-and-persona-activation:P1A`
  - `plan:m365-post-expansion-promotion-and-persona-activation:P1B`
  - `plan:m365-post-expansion-promotion-and-persona-activation:P1C`
- Invariant IDs in scope: `none`
- Lemma IDs in scope: `none`
- Owners: `product`, `engineering`, `MA`

## Context

- Task name: `Promote development to staging and then main`
- Domain: `governance`
- Dependencies: `m365-ai-workforce-expansion-master-plan is closed and merged into development`
- Allowlist:
  - `git branch topology and branch promotion commands`
  - `plans/m365-post-expansion-promotion-and-persona-activation/*`
  - `Operations/NORTHSTAR.md`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
- Denylist:
  - `runtime file edits`
  - `tenant mutations`
  - `post-promotion persona activation work`

## M - Model

- Problem: `The completed workforce program is merged into development, but there is no governed branch-promotion path yet for staging and main.`
- Goal: `Promote the exact completed development state to staging, validate it, then promote the same validated state to main.`
- Success criteria:
  - `staging exists and is aligned to the intended development commit`
  - `main exists and is aligned to the intended staging commit`
  - `no unrelated repo content changes are introduced during promotion`
- Out of scope:
  - `starting persona activation`
  - `editing runtime, registry, or commercialization contracts`

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `Plan refs remain valid and the promotion path matches the active plan.`
- Runtime/test evidence:
  - `git branch, git log, and branch-alignment evidence are captured exactly.`
- Governance evidence:
  - `validate_action is used before mutating git commands.`
- Determinism evidence:
  - `Repeated branch-state inspection yields the same target SHAs once promotion completes.`

## T - Tie

- Dependency ties:
  - `P1A must close before P1B can claim staging readiness.`
  - `P1B must close before P1C can promote to main.`
- Known failure modes:
  - `staging or main have diverged unexpectedly`
  - `governance gate rejects command_exec or push`
  - `branch delete or promotion order is wrong`
- GO criteria:
  - `All promotion checks pass and staging/main align to the intended closed-program commit chain.`
- NO-GO criteria:
  - `Any divergence, missing branch, rejected governance gate, or inconsistent branch state.`

## H - Harness (ordered checks)

`M365-PROMOTION-P1-C0` Preflight

- Read governance docs and confirm `P1A` is the active next act.

`M365-PROMOTION-P1-C1` Baseline inventory

- Capture local and remote branch topology for `development`, `staging`, and `main`.

`M365-PROMOTION-P1-C2` Governance gate

- Run `validate_action` for every mutating `command_exec` and `push` step with explicit root-cause metadata.

`M365-PROMOTION-P1-C3` Stage promotion

- Create or align `staging` from `development`, then push `staging`.

`M365-PROMOTION-P1-C4` Staging validation

- Confirm `staging` commit parity, clean branch state, and replay-safe branch inspection.

`M365-PROMOTION-P1-C5` Main promotion

- Create or align `main` from the validated `staging` state, then push `main`.

`M365-PROMOTION-P1-C6` Post-promotion verification

- Re-run branch topology checks and confirm the final SHAs for `development`, `staging`, and `main`.

`M365-PROMOTION-P1-C7` Hard-fail divergence guard

- Stop if `staging` or `main` contain unexpected extra commits that require human review.

`M365-PROMOTION-P1-C8` Deterministic replay

- Repeat branch inspection and require the same final branch-tip SHAs.

`M365-PROMOTION-P1-C9` Hard gates (strict order)

1. `git branch --all --verbose --no-abbrev`
2. `git log --oneline --decorate --graph --max-count=12 --all --simplify-by-decoration`
3. `git diff --check`

`M365-PROMOTION-P1-C10` Final decision

- Emit GO/NO-GO, list the final branch SHAs, and stop. Do not start persona activation.

## S - Stress-test

- Adversarial checks:
  - `If staging or main are missing, create them only from the intended source branch.`
  - `If staging or main have diverged, STOP and report rather than forcing a merge.`
- Replay checks:
  - `Final branch-tip SHAs for development, staging, and main must remain stable across repeated inspection.`

## Output Contract

- Deliverables:
  - `staging promotion result`
  - `main promotion result`
- Validation results:
  - `M365-PROMOTION-P1-C0..C10 statuses`
- Evidence links:
  - `git commands and exact branch SHAs only`
- Residual risks:
  - `state any divergence or use none`
- Final decision lines:
  - `GATE:M365-PROMOTION-P1 STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Missing plan ref or governance approval.
- Any branch divergence that requires human judgment.
- Any failed git promotion command.
- Any mismatch between intended and actual promoted SHAs.
