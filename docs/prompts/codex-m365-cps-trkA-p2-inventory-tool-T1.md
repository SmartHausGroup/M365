# Codex Execution Prompt — plan:m365-cps-trkA-p2-inventory-tool:T1

## Governance Lock (Read FIRST)

- `AGENTS.md` / `CLAUDE.md` (M365 repo and UCP repo)
- `docs/NORTH_STAR.md` (UCP) / `Operations/NORTHSTAR.md` (M365)
- `plans/m365-cps-trkA-p2-inventory-tool/m365-cps-trkA-p2-inventory-tool.md` (parent phase plan)
- `plans/m365-capability-pack-surface-remediation/m365-capability-pack-surface-remediation.md` (master plan)
- `agent_governance/master-maths-prompt-template.md` (this template)

## Plan Reference

- **Plan:** `plan:m365-cps-trkA-p2-inventory-tool`
- **Parent track:** `plan:m365-cps-trkA-observability`
- **Master plan:** `plan:m365-capability-pack-surface-remediation`
- **Task:** `T1` — Define inventory contract schema
- **Branch:** `feat/m365-cps-trkA`

## Prompt Run Metadata

- Prompt version: v1.0
- Task ID: m365-cps-trkA-p2-inventory-tool-T1
- Run ID: <fill at runtime>
- Commit SHA: <fill at runtime>
- Owner: Phil Siniscalchi (Founder/Owner)

## Context

- **Task name:** Define inventory contract schema
- **Domain:** framework
- **Owner:** Phil Siniscalchi (Founder/Owner)
- **Dependencies:** none
- **Explicit file allowlist (may touch — narrowed from parent plan):**
  - (none — verification task)
- **Explicit file denylist (must not touch):**
  - Anything not in the allowlist above
  - Any file outside the parent plan's allowlist

## Developer Brief (Copy/Paste)

Define JSON schema for the inventory response: {implemented_actions, alias_map, advertised_only, auth_mode_capability}. Document each field semantically.

Plan reference: `plan:m365-cps-trkA-p2-inventory-tool:T1`. Branch: `feat/m365-cps-trkA`.

## M — Model

### Problem we are solving

Define JSON schema for the inventory response: {implemented_actions, alias_map, advertised_only, auth_mode_capability}. Document each field semantically.

### Who this is for

- M365 runtime maintainers
- UCP orchestrator maintainers
- Operators relying on the capability pack

### What success looks like

- Schema document committed; reviewed for completeness

### Constraints

- Touch only files in the allowlist above
- Do not skip pre-commit
- Do not push (commit only at this child-phase scope)
- `validate_action` MCP call before any write

### Out of scope

- Anything outside the parent plan's scope
- Cross-task changes (this prompt is scoped to T1 only)

`[PHASE M COMPLETE — all deliverables met]`

## A — Annotate

### Product rules

1. Per parent plan requirements: R2
2. Output must satisfy exit criteria below
3. Validation command must exit 0

### Assumptions

- Working directory is on branch `feat/m365-cps-trkA` in both repos
- Python venv (`.venv/bin/python`) available in both repos
- All dependencies in requirements.txt installed

### Files to read first

- (none — read parent plan only)

### Required deliverables

- docs/contracts/m365_inventory_schema.json or inline in code

`[PHASE A COMPLETE — all deliverables met]`

## T — Tie

### Decision policy

| Condition | Action |
|---|---|
| All exit criteria can be met within the allowlist | Proceed to H |
| A required file is outside allowlist | EMIT BLOCKED — request scope expansion |
| A precondition is not met (dependency task incomplete) | EMIT BLOCKED — wait for dependency |
| Validation command depends on missing fixture | EMIT BLOCKED — request fixture |

### Known failure modes

- Touching a file outside allowlist → mitigation: re-read allowlist before every write
- Skipping pre-commit → mitigation: run pre-commit before any commit
- Pushing instead of just committing → mitigation: this task does NOT push; only the parent GATE pushes

### go_no_go

GO — proceed to H if all decision-policy conditions are clear.

`[PHASE T COMPLETE — all deliverables met]`

## H — Harness

### Implementation plan

Schema can live inline in m365_runtime/graph/inventory.py or as a separate JSON file.

### Files to create or update

- (none — verification task)

### Expected command sequence

```bash
# 1. Read context


# 2. Make the edits per M+A above (use Read tool first per A1 of CLAUDE.md)

# 3. Validate
test -f $M365_ROOT/docs/contracts/m365_inventory_schema.json || echo 'inline-acceptable'

# 4. Pre-commit
pre-commit run --all-files

# 5. Commit (NO PUSH — that's the parent GATE's job)
git add <files>
git commit -m "plan:m365-cps-trkA-p2-inventory-tool:T1 — Define inventory contract schema"
```

`[PHASE H COMPLETE — all deliverables met]`

## S — Stress-test

### Functional tests

- Validation command exits 0: `test -f $M365_ROOT/docs/contracts/m365_inventory_schema.json || echo 'inline-acceptable'`

### Edge / adversarial tests

- Re-run validation command after a fresh git pull → still exit 0
- Touching any file outside allowlist → must be reverted before commit

### Acceptance gates

- [ ] All exit criteria met
- [ ] Validation command green
- [ ] Pre-commit green
- [ ] Commit message references `plan:m365-cps-trkA-p2-inventory-tool:T1`
- [ ] No push (parent GATE pushes)

`[PHASE S COMPLETE — all deliverables met]`
`FINAL_DECISION: GO`

## Output Contract

- **Deliverables:** see above
- **Artifacts:** N/A (non-math scope)
- **Validation result:** `test -f $M365_ROOT/docs/contracts/m365_inventory_schema.json || echo 'inline-acceptable'` exits 0
- **Residual risks:** none expected at child-phase scope
- **Evidence:** git diff of files in allowlist; commit hash
- **Follow-up:** next child-phase task in parent plan execution sequence

## Required Completion Block

- M complete? (yes/no) Evidence:
- A complete? (yes/no) Evidence:
- T complete? (yes/no) Evidence:
- H complete? (yes/no) Evidence:
- S complete? (yes/no) Evidence:
- Assure required? no
- Observe required? no
- Final Decision: GO | NO-GO
- Approved by:
- Timestamp (UTC):

## Agent Constraints (Re-check Before Every Write)

- Do not edit files outside the allowlist above
- Do not skip pre-commit
- Do not push (this task scope is commit-only)
- Reference `plan:m365-cps-trkA-p2-inventory-tool:T1` in commit message
- Call `validate_action` MCP before any write

<!-- Generated by scripts/generate_m365_cps_scaffold.py on 2026-05-01 -->
