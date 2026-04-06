# MATHS Prompt: M365 Authoritative Persona Humanization Merge Replay to Development

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-authoritative-persona-humanization-merge-replay-to-development:R1`
- `PARENT_PLAN_ACK: plan:m365-authoritative-persona-humanization-merge-to-development`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Approval and Governance Gates

1. **Present the approval packet first** — summarize the corrected source branch head `2a13c5c`, the target branch head, the preserved blocked local replay branches, the explicit merge-only scope, and the validation slice.
2. **Wait for explicit `go`** — do not begin replay-merge execution until the operator confirms with `go`.
3. **Call MCP `validate_action` before every mutating action** — this includes `command_exec`, `file_edit`, `commit`, and `push`.
4. **Use an explicit merge commit** — merge `codex/m365-authoritative-persona-post-h5-parity-correction` into `development`; do not silently fast-forward or rewrite history.
5. **Stop before any further promotion** — this package ends after a validated push to `development`.

## Execution Rules

- Run checks `M1-MERGE-REPLAY-TO-DEVELOPMENT-C0` -> `M1-MERGE-REPLAY-TO-DEVELOPMENT-C9` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:M1-MERGE-REPLAY-TO-DEVELOPMENT STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M1-MERGE-REPLAY-TO-DEVELOPMENT`
- Run ID: `m365-authoritative-persona-humanization-merge-replay-to-development`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-authoritative-persona-humanization-merge-replay-to-development:R1`
  - `plan:m365-authoritative-persona-humanization-merge-replay-to-development:R2`
  - `plan:m365-authoritative-persona-humanization-merge-replay-to-development:R3`
  - `plan:m365-authoritative-persona-humanization-merge-replay-to-development:R4`
  - `plan:m365-authoritative-persona-humanization-merge-replay-to-development:R5`
  - `plan:m365-authoritative-persona-humanization-merge-replay-to-development:R6`
- Invariant IDs in scope: `none`
- Lemma IDs in scope: `none`
- Owners: `product`, `engineering`, `governance`

## Context

- Task name: `Replay the corrected authoritative persona humanization merge into development`
- Domain: `governance`
- Dependencies:
  - `plans/m365-authoritative-persona-humanization-merge-to-development/m365-authoritative-persona-humanization-merge-to-development.md`
  - `plans/m365-authoritative-persona-post-h5-certification-parity-scope-correction/m365-authoritative-persona-post-h5-certification-parity-scope-correction.md`
  - `plans/m365-authoritative-persona-post-h5-department-pack-coverage-parity-correction/m365-authoritative-persona-post-h5-department-pack-coverage-parity-correction.md`
  - `codex/m365-authoritative-persona-post-h5-parity-correction @ 2a13c5c`
  - `development @ 4c997ea at replay-package creation`
- Allowlist:
  - `git fetch, checkout, merge, commit, push, and branch-inspection commands`
  - `plans/m365-authoritative-persona-humanization-merge-replay-to-development/**`
  - `docs/prompts/codex-m365-authoritative-persona-humanization-merge-replay-to-development.md`
  - `docs/prompts/codex-m365-authoritative-persona-humanization-merge-replay-to-development-prompt.txt`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
  - `the already governed replay surface from 4c997ea..2a13c5c, but only for bounded conflict resolution that preserves the proven semantics`
- Denylist:
  - `staging promotion`
  - `main promotion`
  - `release tagging`
  - `editing registry/agents.yaml`
  - `editing registry/ai_team.json`
  - `new implementation unrelated to bounded conflict resolution`

## M - Model

- Problem: `The corrected authoritative persona humanization surface is ready for replay merge, but the historical merge package still points at the pre-correction source branch and cannot truthfully authorize the next M1 run.`
- Goal: `Replay the corrected review branch into development through a bounded, validated, fail-closed integration step.`
- Success criteria:
  - `development contains an explicit merge result for codex/m365-authoritative-persona-post-h5-parity-correction`
  - `the merged development state preserves the governed 59 total / 54 active / 5 planned / 430 action truth`
  - `origin/development matches the validated local development merge result`
- Out of scope:
  - `staging or main promotion`
  - `release-tag publication`
  - `new persona or department-model changes`

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `the replay package and ops trackers reflect replay readiness before execution and replay outcome after execution`
- Runtime/test evidence:
  - `the final builder, verifiers, focused pytest slice, pre-commit, and git diff --check are green on merged development`
- Governance evidence:
  - `validate_action is used before every mutating command or file edit`
- Determinism evidence:
  - `repeated branch inspection yields the same final local and origin development SHAs`

## T - Tie

- Dependency ties:
  - `L83 and L84 blocker corrections must remain green before replay execution begins`
  - `preflight must pass before merge`
  - `merge must pass before validation`
  - `validation must pass before push`
- Known failure modes:
  - `origin/development drift changes the bounded replay surface materially`
  - `merge conflicts require semantic edits outside the governed replay surface or tracker files`
  - `final validation fails on merged development`
- GO criteria:
  - `development contains the governed replay merge result and all required validations are green`
- NO-GO criteria:
  - `any out-of-scope conflict, failed validation, or unintended branch promotion`

## H - Harness (ordered checks)

`M1-MERGE-REPLAY-TO-DEVELOPMENT-C0` Preflight

- Read governance docs and confirm this replay package is the active next act.

`M1-MERGE-REPLAY-TO-DEVELOPMENT-C1` Branch inventory

- Fetch and capture local plus remote SHAs for the corrected source branch and `development`.

`M1-MERGE-REPLAY-TO-DEVELOPMENT-C2` Governance gate

- Run `validate_action` before every mutating action and stop on red.

`M1-MERGE-REPLAY-TO-DEVELOPMENT-C3` Target branch preparation

- Checkout `development`, update it from `origin/development`, and require a clean working tree.

`M1-MERGE-REPLAY-TO-DEVELOPMENT-C4` Merge execution

- Merge `codex/m365-authoritative-persona-post-h5-parity-correction` into `development` with an explicit merge commit.

`M1-MERGE-REPLAY-TO-DEVELOPMENT-C5` Bounded conflict resolution

- Resolve only bounded conflicts inside the governed replay surface or tracker files; otherwise stop.

`M1-MERGE-REPLAY-TO-DEVELOPMENT-C6` Merge-state validation

- Run:
  - `PYTHONPATH=src python3 scripts/ci/build_persona_registry_v2.py`
  - `python3 scripts/ci/verify_authoritative_digital_employee_records_v1.py`
  - `PYTHONPATH=src python3 scripts/ci/verify_persona_registry_v2.py`
  - `python3 scripts/ci/verify_persona_certification_v1.py`
  - `python3 scripts/ci/verify_department_certification_v1.py`
  - `python3 scripts/ci/verify_enterprise_release_gate_v2.py`
  - `python3 scripts/ci/verify_activated_persona_surface_v1.py`
  - `python3 scripts/ci/verify_workforce_packaging_v1.py`
  - `python3 scripts/ci/verify_*_department_pack_v1.py`
  - `PYTHONPATH=src .venv/bin/pytest -q tests/test_authoritative_digital_employee_records_v1.py tests/test_authoritative_persona_registry_rebase_v1.py tests/test_persona_registry_v2.py tests/test_persona_certification_v1.py tests/test_department_certification_v1.py tests/test_activated_persona_surface_v1.py tests/test_workforce_packaging_v1.py tests/test_*_department_pack_v1.py`
  - `pre-commit run --all-files`
  - `git diff --check`

`M1-MERGE-REPLAY-TO-DEVELOPMENT-C7` Governance synchronization

- Update the replay package and trackers to reflect the real merge outcome and next act.

`M1-MERGE-REPLAY-TO-DEVELOPMENT-C8` Push development

- Push `development` only if the merge-state validation slice is green.

`M1-MERGE-REPLAY-TO-DEVELOPMENT-C9` Final replay and decision

- Re-run branch inspection, require local `development` and `origin/development` to match, then emit GO or NO-GO and stop.

## Output Contract

- Deliverables:
  - `development replay merge result`
  - `validation outcome`
  - `tracker synchronization result`
- Validation results:
  - `M1-MERGE-REPLAY-TO-DEVELOPMENT-C0..C9 statuses`
- Evidence links:
  - `file paths and commands only`
- Final decision lines:
  - `GATE:M1-MERGE-REPLAY-TO-DEVELOPMENT STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Missing approval packet or explicit `go`.
- Any governance rejection for mutating actions.
- Any merge conflict requiring edits outside the bounded corrected source-branch diff or tracker files.
- Any failed builder, verifier, pytest, pre-commit, or `git diff --check` gate.
- Any attempt to touch `staging`, `main`, or release tags during this package.
