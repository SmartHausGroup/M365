# Codex Execution Prompt — plan:m365-cps-trkB-p1-sharepoint-reads:T7

## Governance Lock (Read FIRST)

- `AGENTS.md` / `CLAUDE.md` (M365 repo and UCP repo)
- `docs/NORTH_STAR.md` (UCP) / `Operations/NORTHSTAR.md` (M365)
- `plans/m365-cps-trkB-p1-sharepoint-reads/m365-cps-trkB-p1-sharepoint-reads.md` (parent phase plan)
- `plans/m365-capability-pack-surface-remediation/m365-capability-pack-surface-remediation.md` (master plan)
- `agent_governance/master-maths-prompt-template.md` (this template)

## Plan Reference

- **Plan:** `plan:m365-cps-trkB-p1-sharepoint-reads`
- **Parent track:** `plan:m365-cps-trkB-coverage`
- **Master plan:** `plan:m365-capability-pack-surface-remediation`
- **Task:** `T7` — Add graph.drives.children registry entry
- **Branch:** `feat/m365-cps-trkB`

## Prompt Run Metadata

- Prompt version: v1.0
- Task ID: m365-cps-trkB-p1-sharepoint-reads-T7
- Run ID: <fill at runtime>
- Commit SHA: <fill at runtime>
- Owner: Phil Siniscalchi (Founder/Owner)

## Context

- **Task name:** Add graph.drives.children registry entry
- **Domain:** framework
- **Owner:** Phil Siniscalchi (Founder/Owner)
- **Dependencies:** T6
- **Explicit file allowlist (may touch — narrowed from parent plan):**
  - M365: src/m365_runtime/graph/registry.py
- **Explicit file denylist (must not touch):**
  - Anything not in the allowlist above
  - Any file outside the parent plan's allowlist

## Developer Brief (Copy/Paste)

Add ActionSpec for graph.drives.children (workload sharepoint; auth_modes ['auth_code_pkce', 'app_only_secret', 'app_only_certificate']; scopes ['Files.Read.All']; risk low; rw read) to READ_ONLY_REGISTRY in src/m365_runtime/graph/registry.py. Endpoint per parent plan B-action spec table.

Plan reference: `plan:m365-cps-trkB-p1-sharepoint-reads:T7`. Branch: `feat/m365-cps-trkB`.

## M — Model

### Problem we are solving

Add ActionSpec for graph.drives.children (workload sharepoint; auth_modes ['auth_code_pkce', 'app_only_secret', 'app_only_certificate']; scopes ['Files.Read.All']; risk low; rw read) to READ_ONLY_REGISTRY in src/m365_runtime/graph/registry.py. Endpoint per parent plan B-action spec table.

### Who this is for

- M365 runtime maintainers
- UCP orchestrator maintainers
- Operators relying on the capability pack

### What success looks like

- get_action('graph.drives.children') returns the spec; admit() works

### Constraints

- Touch only files in the allowlist above
- Do not skip pre-commit
- Do not push (commit only at this child-phase scope)
- `validate_action` MCP call before any write

### Out of scope

- Anything outside the parent plan's scope
- Cross-task changes (this prompt is scoped to T7 only)

`[PHASE M COMPLETE — all deliverables met]`

## A — Annotate

### Product rules

1. Per parent plan requirements: R4
2. Output must satisfy exit criteria below
3. Validation command must exit 0

### Assumptions

- Working directory is on branch `feat/m365-cps-trkB` in both repos
- Python venv (`.venv/bin/python`) available in both repos
- All dependencies in requirements.txt installed

### Files to read first

- (none — read parent plan only)

### Required deliverables

- src/m365_runtime/graph/registry.py with graph.drives.children ActionSpec

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

See M and A phases above for the work to perform.

### Files to create or update

- M365: src/m365_runtime/graph/registry.py

### Expected command sequence

```bash
# 1. Read context


# 2. Make the edits per M+A above (use Read tool first per A1 of CLAUDE.md)

# 3. Validate
cd $M365_ROOT && .venv/bin/python -c "from m365_runtime.graph.registry import get_action; spec = get_action('graph.drives.children'); assert spec.workload == 'sharepoint'; print('OK')"

# 4. Pre-commit
pre-commit run --all-files

# 5. Commit (NO PUSH — that's the parent GATE's job)
git add <files>
git commit -m "plan:m365-cps-trkB-p1-sharepoint-reads:T7 — Add graph.drives.children registry entry"
```

`[PHASE H COMPLETE — all deliverables met]`

## S — Stress-test

### Functional tests

- Validation command exits 0: `cd $M365_ROOT && .venv/bin/python -c "from m365_runtime.graph.registry import get_action; spec = get_action('graph.drives.children'); assert spec.workload == 'sharepoint'; print('OK')"`

### Edge / adversarial tests

- Re-run validation command after a fresh git pull → still exit 0
- Touching any file outside allowlist → must be reverted before commit

### Acceptance gates

- [ ] All exit criteria met
- [ ] Validation command green
- [ ] Pre-commit green
- [ ] Commit message references `plan:m365-cps-trkB-p1-sharepoint-reads:T7`
- [ ] No push (parent GATE pushes)

`[PHASE S COMPLETE — all deliverables met]`
`FINAL_DECISION: GO`

## Output Contract

- **Deliverables:** see above
- **Artifacts:** N/A (non-math scope)
- **Validation result:** `cd $M365_ROOT && .venv/bin/python -c "from m365_runtime.graph.registry import get_action; spec = get_action('graph.drives.children'); assert spec.workload == 'sharepoint'; print('OK')"` exits 0
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
- Reference `plan:m365-cps-trkB-p1-sharepoint-reads:T7` in commit message
- Call `validate_action` MCP before any write

<!-- Generated by scripts/generate_m365_cps_scaffold.py on 2026-05-01 -->
