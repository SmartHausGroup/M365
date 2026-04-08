# MATHS Prompt: M365 Power Platform and Team Status Merge to Development

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-power-platform-and-team-status-merge-to-development:R1`
- `PARENT_PLAN_ACK: plan:m365-team-status-workflow-enablement`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Approval and Governance Gates

1. Run MCP `validate_action` before every mutating action.
2. Use an explicit merge commit.
3. Stop on first red gate or out-of-scope conflict.
4. End after validated push to `development`.

## Execution Rules

- Run checks `M1-POWERPLATFORM-TEAMSTATUS-MERGE-C0` -> `M1-POWERPLATFORM-TEAMSTATUS-MERGE-C9` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:M1-POWERPLATFORM-TEAMSTATUS-MERGE STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Context

- Source branch: `codex/m365-power-platform-executor-auth-remediation @ 5b4efb6`
- Target branch at package creation: `development @ 541c00e`
- Merge scope: only the bounded source diff plus merge package and governance trackers
- Preserve:
  - tenant-generic Power Platform credential model
  - public SharePoint list creation surface
  - bounded team-status workflow provisioning path
  - successful live workflow reference result

## Harness

`M1-POWERPLATFORM-TEAMSTATUS-MERGE-C0` Preflight
- confirm this merge package is the active next act

`M1-POWERPLATFORM-TEAMSTATUS-MERGE-C1` Branch inventory
- fetch and capture source/development SHAs

`M1-POWERPLATFORM-TEAMSTATUS-MERGE-C2` Governance gate
- run `validate_action` before every mutating step

`M1-POWERPLATFORM-TEAMSTATUS-MERGE-C3` Target preparation
- checkout `development`, refresh from `origin/development`, require clean tree

`M1-POWERPLATFORM-TEAMSTATUS-MERGE-C4` Merge execution
- merge `codex/m365-power-platform-executor-auth-remediation` into `development` with explicit merge commit

`M1-POWERPLATFORM-TEAMSTATUS-MERGE-C5` Conflict discipline
- resolve only bounded conflicts inside the governed source diff or trackers

`M1-POWERPLATFORM-TEAMSTATUS-MERGE-C6` Merge-state validation
- run:
  - `python3 -m py_compile src/provisioning_api/routers/m365.py src/smarthaus_common/tenant_config.py src/smarthaus_common/power_apps_client.py src/smarthaus_common/power_automate_client.py src/smarthaus_common/team_status_workflow.py scripts/ops/provision_team_status_workflow.py`
  - `PYTHONPATH=src .venv/bin/python scripts/ci/verify_sharepoint_onedrive_files_expansion.py`
  - `PYTHONPATH=src .venv/bin/python scripts/ci/verify_power_automate_expansion.py`
  - `PYTHONPATH=src .venv/bin/python scripts/ci/verify_capability_registry.py`
  - `PYTHONPATH=src .venv/bin/python scripts/ci/verify_caio_m365_contract.py`
  - `PYTHONPATH=src .venv/bin/pytest -q tests/test_tenant_config_powerplatform.py tests/test_sharepoint_onedrive_files_expansion_v2.py tests/test_power_automate_expansion_v2.py tests/test_team_status_workflow.py`
  - `pre-commit run --all-files`
  - `git diff --check`

`M1-POWERPLATFORM-TEAMSTATUS-MERGE-C7` Governance synchronization
- update merge package and trackers truthfully

`M1-POWERPLATFORM-TEAMSTATUS-MERGE-C8` Push development
- push only if validation is fully green

`M1-POWERPLATFORM-TEAMSTATUS-MERGE-C9` Final replay and decision
- require local and remote `development` SHAs to match, then emit GO or NO-GO
