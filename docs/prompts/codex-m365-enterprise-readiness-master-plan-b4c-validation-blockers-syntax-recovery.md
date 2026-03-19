# MATHS Prompt: B4C Validation Blockers and Syntax Recovery

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-readiness-master-plan:B4C`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-READY-B4C-C0` -> `M365-READY-B4C-C7` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Final outputs exactly:
  - `GATE:M365-READY-B4C STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Task ID: `M365-READY-B4C`
- Run ID: `b4c-validation-blockers-syntax-recovery`
- Plan refs in scope:
  - `plan:m365-enterprise-readiness-master-plan:R5`
  - `plan:m365-enterprise-readiness-master-plan:B4C`

## Context

- Domain: `code`
- Dependencies: repo-wide pre-commit failure inventory
- Allowlist:
  - `scripts/generate-policies.py`
  - `governance/invariants/m365/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `plans/m365-enterprise-readiness-master-plan/*`
- Denylist:
  - unrelated repo-wide lint cleanup not needed for parse recovery

## M - Model

- Problem: Black and YAML validation cannot recover while hard parse and syntax blockers remain.
- Goal: remove the parse and schema blockers that prevent broader validation cleanup.
- Success criteria:
  - `scripts/generate-policies.py` parses
  - malformed YAML invariants parse cleanly
  - formatter or YAML checks no longer fail on those hard blockers

## H - Harness

- `M365-READY-B4C-C0` capture the exact baseline failure set for parse and YAML blockers.
- `M365-READY-B4C-C1` fix the Black parse blocker.
- `M365-READY-B4C-C2` fix malformed YAML invariants.
- `M365-READY-B4C-C3` run targeted Black validation.
- `M365-READY-B4C-C4` run targeted YAML validation.
- `M365-READY-B4C-C5` verify no new syntax regressions were introduced.
- `M365-READY-B4C-C6` sync plan and tracker artifacts.
- `M365-READY-B4C-C7` emit final gate and next-act state.

## Validation

1. `python -m py_compile scripts/generate-policies.py`
2. `python - <<'PY'\nimport yaml, pathlib\nfor p in pathlib.Path('governance/invariants/m365').glob('*.yaml'):\n    yaml.safe_load(p.read_text())\nprint('ok')\nPY`
3. `git diff --check`

## No-Go Triggers

- Black parse blocker remains
- any targeted YAML invariant still fails to parse
- changes widen scope into general lint cleanup before hard blockers are removed
