# Execution Prompt — MATHS Workstream (Governance Locked)

Plan Reference: `plan:m365-ucp-standalone-pack-surface`
Parent Plan: `none`
North Star: `docs/NORTH_STAR.md` (M365 repo equivalent: `Operations/NORTHSTAR.md`)
Execution Plan: `docs/platform/EXECUTION_PLAN.md` (M365 repo equivalent: `Operations/EXECUTION_PLAN.md`)
MATHS Prompt Template: `agent_governance/master-maths-prompt-template.md` (M365 repo equivalent: `docs/governance/MATHS_PROMPT_TEMPLATE.md`)

**Mission:** Make the M365 repo the authoritative owner of the standalone UCP-facing `m365_pack` surface by adding the pack contracts and service-mode-only client here, with focused tests and truthful governance closure.

## Governance Lock (Mandatory)

Before any write, test, or command:

1. Read:
- `AGENTS.md`
- applicable `.cursor/rules/**/*.mdc`
- `Operations/NORTHSTAR.md`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`
- `plans/m365-ucp-standalone-pack-surface/m365-ucp-standalone-pack-surface.md`
- `plans/m365-ucp-standalone-pack-surface/m365-ucp-standalone-pack-surface.yaml`
- `../UCP/docs/platform/M365_SERVICE_MODE_ACCEPTANCE.md`
- `../UCP/docs/platform/M365_STANDALONE_PACK_EXTERNALIZATION_AND_MACOS_TRUTH.md`
- `docs/governance/MATHS_PROMPT_TEMPLATE.md`

2. Verify alignment + plan linkage:
- cite `plan:m365-ucp-standalone-pack-surface:R1` through `R5`
- cite `plan:m365-ucp-standalone-pack-surface:T1` through `T5`
- stop immediately if work escapes the allowlist or drifts into sibling UCP edits

3. Enforce approval protocol:
- this plan is approved for execution in the current session
- keep work bounded to the standalone pack surface in this repo
- call `validate_action` before mutating phases and create notebook evidence when governance admission requires it

## M

- lock this repo as the owner of the standalone UCP-facing `m365_pack` source

## Validator Compatibility Anchors

M:
A:
T:
H:
S:

## A

- create the standalone contracts package

## T

- create the standalone service-mode client package with no direct-import live fallback

## H

- add focused tests and a short commercialization/operator doc for the standalone surface

## S

- close governance truthfully and ship the repo clean
