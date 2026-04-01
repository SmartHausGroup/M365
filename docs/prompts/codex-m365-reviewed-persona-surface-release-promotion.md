# MATHS Prompt: P4 Reviewed Persona Surface Release Promotion

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-post-expansion-promotion-and-persona-activation:P4A`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-PROMOTION-P4-C0` -> `M365-PROMOTION-P4-C12` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:M365-PROMOTION-P4 STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-PROMOTION-P4`
- Run ID: `reviewed-persona-surface-release-promotion`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-post-expansion-promotion-and-persona-activation:R12`
  - `plan:m365-post-expansion-promotion-and-persona-activation:R13`
  - `plan:m365-post-expansion-promotion-and-persona-activation:R14`
  - `plan:m365-post-expansion-promotion-and-persona-activation:P4A`
  - `plan:m365-post-expansion-promotion-and-persona-activation:P4B`
  - `plan:m365-post-expansion-promotion-and-persona-activation:P4C`
  - `plan:m365-post-expansion-promotion-and-persona-activation:P4D`
- Invariant IDs in scope: `none`
- Lemma IDs in scope: `none`
- Owners: `product`, `engineering`, `MA`

## Context

- Task name: `Merge reviewed persona surface into development, version it, and promote it to staging and main`
- Domain: `governance`
- Dependencies: `P2E is complete on feature/m365_personas and the reviewed persona surface is ready for governed integration`
- Allowlist:
  - `git merge, checkout, branch, tag, and push commands`
  - `pyproject.toml`
  - `src/ops_adapter/app.py`
  - `src/ops_adapter/main.py`
  - `plans/m365-post-expansion-promotion-and-persona-activation/*`
  - `Operations/NORTHSTAR.md`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
- Denylist:
  - `starting P3 external-platform preparation`
  - `editing persona registries or activation surfaces unrelated to release versioning`
  - `touching tenant state`

## M - Model

- Problem: `The reviewed persona activation surface is complete on feature/m365_personas but is not yet integrated into development or promoted as a versioned release to staging and main.`
- Goal: `Integrate the reviewed feature branch into development, stamp version 0.2.0 on the core Python/API runtime surfaces, promote the exact validated commit to staging and main, and publish m365-workforce-v0.2.0.`
- Success criteria:
  - `feature/m365_personas is merged into development`
  - `pyproject.toml, src/ops_adapter/app.py, and src/ops_adapter/main.py all read 0.2.0`
  - `development, staging, and main all resolve to the same final release-closeout commit`
  - `annotated tag m365-workforce-v0.2.0 exists on that final commit`
- Out of scope:
  - `starting P3A`
  - `new persona activation work`
  - `changing the deferred 5 external-platform personas`

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `The active plan triplet and ops trackers reflect P4A-P4D, then restore P3A as next when promotion closes.`
- Runtime/test evidence:
  - `pre-commit is green on the versioned development commit.`
- Governance evidence:
  - `validate_action is used before mutating file-edit, command_exec, commit, push, and tag steps.`
- Determinism evidence:
  - `Repeated branch inspection yields the same final development, staging, and main SHAs.`

## T - Tie

- Dependency ties:
  - `P4A must close before P4B.`
  - `P4B must close before P4C.`
  - `P4C must close before P4D.`
- Known failure modes:
  - `merge conflicts spill outside the approved reviewed-surface file set`
  - `development, staging, or main diverge unexpectedly`
  - `version surfaces disagree`
  - `governance gate rejects command_exec, commit, push, or tag publication`
- GO criteria:
  - `The reviewed persona surface is merged, versioned to 0.2.0, promoted to development/staging/main, tagged, and P3A is restored as next.`
- NO-GO criteria:
  - `Any merge divergence requiring human judgment, failed version sync, failed pre-commit, or branch mismatch after promotion.`

## H - Harness (ordered checks)

`M365-PROMOTION-P4-C0` Preflight

- Read governance docs and confirm `P4A` is the active next act.

`M365-PROMOTION-P4-C1` Branch inventory

- Capture local and remote branch topology for `feature/m365_personas`, `development`, `staging`, and `main`.

`M365-PROMOTION-P4-C2` Governance gate

- Run `validate_action` for every mutating file-edit, `command_exec`, `commit`, `push`, and tag step with explicit metadata.

`M365-PROMOTION-P4-C3` Merge reviewed surface into development

- Integrate `feature/m365_personas` into `development` by the cleanest governed path and stop on unbounded conflicts.

`M365-PROMOTION-P4-C4` Version stamp

- Update `pyproject.toml`, `src/ops_adapter/app.py`, and `src/ops_adapter/main.py` to version `0.2.0`.

`M365-PROMOTION-P4-C5` Validation on development

- Run `pre-commit run --all-files` and branch-state checks on the versioned development commit.

`M365-PROMOTION-P4-C6` Promote to staging

- Advance `staging` to the exact validated versioned development commit.

`M365-PROMOTION-P4-C7` Validate staging parity

- Confirm `staging` matches `development` exactly.

`M365-PROMOTION-P4-C8` Promote to main

- Advance `main` to the same validated staging commit.

`M365-PROMOTION-P4-C9` Release tag

- Create and push annotated tag `m365-workforce-v0.2.0` on the final aligned release commit.

`M365-PROMOTION-P4-C10` Governance closeout sync

- Update the plan triplet and ops trackers so `P4A-P4D` are complete and `P3A` is next.

`M365-PROMOTION-P4-C11` Final branch alignment replay

- Re-run branch inspection and require the same final SHAs for `development`, `staging`, and `main`.

`M365-PROMOTION-P4-C12` Final decision

- Emit GO/NO-GO, list final branch SHAs and release tag, and stop. Do not start `P3A`.

## S - Stress-test

- Adversarial checks:
  - `If merge conflicts extend beyond the reviewed-surface and tracker/version files, STOP and report.`
  - `If staging or main contain unexpected extra commits, STOP rather than force-resetting history.`
- Replay checks:
  - `The final development, staging, and main SHAs plus the release tag target must remain stable across repeated inspection.`

## Output Contract

- Deliverables:
  - `development merge result`
  - `version 0.2.0 result`
  - `staging promotion result`
  - `main promotion result`
  - `annotated tag publication result`
- Validation results:
  - `M365-PROMOTION-P4-C0..C12 statuses`
- Evidence links:
  - `git commands and exact branch/tag SHAs only`
- Residual risks:
  - `state any divergence or use none`
- Final decision lines:
  - `GATE:M365-PROMOTION-P4 STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Missing plan ref or governance approval.
- Any merge divergence that requires human judgment.
- Any failed version stamp or failed pre-commit run.
- Any mismatch between intended and actual promoted SHAs.
- Any tag publication mismatch or branch drift after promotion.
