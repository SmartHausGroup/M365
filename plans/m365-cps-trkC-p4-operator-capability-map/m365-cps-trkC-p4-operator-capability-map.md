# Parent Phase C4 — Operator Capability Map

## Section 1: Plan Header

- **Plan ID:** `plan:m365-cps-trkC-p4-operator-capability-map`
- **Parent Plan ID:** `plan:m365-cps-trkC-truth-in-advertising`
- **Title:** Parent Phase C4 — Operator Capability Map
- **Version:** 1.0
- **Status:** draft
- **Owner:** Phil Siniscalchi (Founder/Owner)
- **Date Created:** 2026-05-01
- **Date Updated:** 2026-05-01
- **North Star Ref:** `docs/NORTH_STAR.md`
- **Execution Plan Ref:** docs/platform/EXECUTION_PLAN.md - M365 CPS Track C P4
- **Domain:** framework
- **Math/Algorithm Scope:** false

## Section 2: North Star Alignment

- **Source:** `docs/NORTH_STAR.md` (UCP) / `Operations/NORTHSTAR.md` (M365)
- **Principles served:**
  - Gates-by-construction integrity (denials must be honest)
  - Tool-first determinism (capability surface must equal advertised surface)
  - Fail-closed semantics (unknown action != blocked write)
  - Operator observability (the system must explain its own state)
  - Plan-first execution with strict per-phase gates
- **Anti-alignment (preserved unchanged):**
  - Mutation fence on actual write actions stays on
  - Risk-tier classification per agent stays unchanged
  - Audit envelope format stays unchanged
  - Two-phase confirmation gate for high-risk mutations stays on

## Section 3: Intent Capture

- **User's stated requirements:**
  - Auto-generate operator-facing capability map doc from registry + agents.yaml. Mirror to UCP docs.
- **Intent doc ref:** captured in this plan
- **Intent verification:** Tasks T1..T5 together satisfy this parent phase's objective.

## Section 4: Objective

- **Objective:** Auto-generate operator-facing capability map doc from registry + agents.yaml. Mirror to UCP docs.
- **Current state:** Parent phase scope draft; no implementation yet.
- **Target state:** All child tasks complete; GATE green; commit + push to feat/m365-cps-trkC.

## Section 5: Scope

### In scope

- Generate capability map document
- Add capability map to M365 docs/
- Add operator-facing capability map to UCP docs
- Make regeneration a CI artifact
- Pre-commit + commit

### Out of scope

- Anything outside this parent's allowlist

### File allowlist

- `M365: scripts/generate_capability_map.py`
- `M365: docs/m365_capability_map.md`
- `M365: README.md`
- `M365: .pre-commit-config.yaml`
- `UCP: docs/platform/M365_CAPABILITY_MAP.md`

### File denylist

- `Files outside capability-map generation scope`
- `Any file not in allowlist of the active child-phase task`

### Scope fence rule

Agent must STOP and re-scope if any file outside the allowlist is needed. Emit BLOCKED.

## Section 6: Requirements

### R7

- **Ref:** `plan:m365-cps-trkC-p4-operator-capability-map:R7`
- **Description:** Carry-through of master R7; this parent phase contributes scoped behavior.
- **Acceptance criteria:** Per-task exit criteria; parent GATE passes.
- **Depends on:** none
- **User intent trace:** Master R7

### R8

- **Ref:** `plan:m365-cps-trkC-p4-operator-capability-map:R8`
- **Description:** Carry-through of master R8; this parent phase contributes scoped behavior.
- **Acceptance criteria:** Per-task exit criteria; parent GATE passes.
- **Depends on:** none
- **User intent trace:** Master R8

## Section 7: Execution Sequence

- **Ordering:** ['T1', 'T2', 'T3', 'T4', 'T5']
- **Stop on first failure:** true
- **Strict ordering rule:** Do not start task N+1 until task N exit criteria are met.
- **MATHS phase mapping:** N/A (non-math scope)

## Section 8: Task Breakdown

### T1 — Generate capability map document

- **Ref:** `plan:m365-cps-trkC-p4-operator-capability-map:T1`
- **Description:** scripts/generate_capability_map.py reads registry + alias table + agents.yaml and emits docs/m365_capability_map.md with: per-agent allowed actions, per-action coverage_status, per-action runtime endpoint and scopes.
- **Requirement refs:** R7
- **Depends on:** none
- **MATHS phase:** N/A
- **Deliverables:**
  - scripts/generate_capability_map.py
  - docs/m365_capability_map.md
- **Exit criteria:**
  - Doc generated; matches runtime state
- **Validation command:** `cd $M365_ROOT && .venv/bin/python scripts/generate_capability_map.py > docs/m365_capability_map.md`
- **Files to modify:**
  - M365: scripts/generate_capability_map.py
  - M365: docs/m365_capability_map.md

### T2 — Add capability map to M365 docs/

- **Ref:** `plan:m365-cps-trkC-p4-operator-capability-map:T2`
- **Description:** docs/m365_capability_map.md committed; README links to it.
- **Requirement refs:** R7
- **Depends on:** T1
- **MATHS phase:** N/A
- **Deliverables:**
  - Doc committed; README updated
- **Exit criteria:**
  - File exists at docs/m365_capability_map.md
- **Validation command:** `test -f $M365_ROOT/docs/m365_capability_map.md`
- **Files to modify:**
  - M365: docs/m365_capability_map.md
  - M365: README.md

### T3 — Add operator-facing capability map to UCP docs

- **Ref:** `plan:m365-cps-trkC-p4-operator-capability-map:T3`
- **Description:** Mirror in UCP docs/platform/M365_CAPABILITY_MAP.md generated from same source.
- **Requirement refs:** R7
- **Depends on:** T2
- **MATHS phase:** N/A
- **Deliverables:**
  - docs/platform/M365_CAPABILITY_MAP.md
- **Exit criteria:**
  - File exists; matches M365 source
- **Validation command:** `test -f $UCP_ROOT/docs/platform/M365_CAPABILITY_MAP.md`
- **Files to modify:**
  - UCP: docs/platform/M365_CAPABILITY_MAP.md

### T4 — Make regeneration a CI artifact

- **Ref:** `plan:m365-cps-trkC-p4-operator-capability-map:T4`
- **Description:** Pre-commit hook regenerates the doc on registry/agents.yaml changes; fails if doc out-of-date.
- **Requirement refs:** R7
- **Depends on:** T3
- **MATHS phase:** N/A
- **Deliverables:**
  - .pre-commit-config.yaml updated
- **Exit criteria:**
  - Pre-commit hook runs
- **Validation command:** `cd $M365_ROOT && pre-commit run generate-capability-map`
- **Files to modify:**
  - M365: .pre-commit-config.yaml

### T5 — Pre-commit + commit

- **Ref:** `plan:m365-cps-trkC-p4-operator-capability-map:T5`
- **Description:** Standard validation + commit.
- **Requirement refs:** R8
- **Depends on:** T4
- **MATHS phase:** N/A
- **Deliverables:**
  - Commit in both repos
- **Exit criteria:**
  - git log shows commit
- **Validation command:** `cd $M365_ROOT && pre-commit run --all-files && make test && cd $UCP_ROOT && pre-commit run --all-files && make test && git log --oneline -1 | grep 'plan:m365-cps-trkC-p4'`

## Section 9: Gate Checks

### CHECK:C0 — Parent phase C4 integration

- **Description:** All child tasks T1..T5 green; integration test pass
- **Task ref:** T1..T5
- **Validation command:** `test -f $M365_ROOT/docs/m365_capability_map.md && test -f $UCP_ROOT/docs/platform/M365_CAPABILITY_MAP.md`
- **Pass criteria:** Integration test exit code 0
- **Fail action:** block

### Decision rule

- **GO:** All gates pass.
- **NO-GO:** Any gate fails.

### No-go triggers

- Any child task fails its validation_command
- Parent GATE integration test fails
- File outside parent allowlist touched

## Section 10: Determinism Requirements

N/A — non-math scope. Tests must be hermetic; live tenant only in GATE smoke tests.

## Section 11: Artifacts

| Path | Format | Producer | Schema ref | Validation |
|------|--------|----------|------------|------------|
| scripts/generate_capability_map.py | Python | T1 | per-task | see Section 8 / T1 |
| docs/m365_capability_map.md | Markdown | T1 | per-task | see Section 8 / T1 |
| Doc committed; README updated | varies | T2 | per-task | see Section 8 / T2 |
| docs/platform/M365_CAPABILITY_MAP.md | Markdown | T3 | per-task | see Section 8 / T3 |
| .pre-commit-config.yaml updated | varies | T4 | per-task | see Section 8 / T4 |
| Commit in both repos | varies | T5 | per-task | see Section 8 / T5 |

## Section 12: Environment Prerequisites

- **Python version:** >=3.11
- **Virtual environment:** `.venv/bin/python`
- **Dependencies:** as in requirements.txt of each repo
- **Hardware:** standard CI; live tenant for GATE smoke tests
- **External data:** live M365 tenant (smarthausgroup.com) for GATE smoke tests
- **Pre-notebook check:** N/A

## Section 13: Implementation Approach

- **Options considered:**
  - Option A: All-at-once monolithic change → rejected: too coarse, drift risk
  - Option B: Per-track / per-parent / per-child phase hierarchy → CHOSEN
- **Chosen approach:** Option B. Granular commits enforce cadence; per-task MATHS prompts give executor zero drift opportunity.
- **Rejected approaches:** Option A (above)
- **ADR ref:** N/A

## Section 14: Risks and Mitigations

| Risk | Impact | Mitigation | Status |
|------|--------|------------|--------|
| Cross-repo drift during edits | medium | Per-task allowlist explicit per repo | mitigated |

### Hard blockers

- (none)

## Section 15: Rollback

- **Rollback procedure:**
  1. Revert commits on the feature branch.
  2. If parent phase pushed: revert push via new revert commits.
  3. Update ACTION_LOG with rollback entry.
  4. Set this plan status → cancelled.
- **Files to revert:** all files in this plan's allowlist that were modified
- **Artifacts to delete:** any generated artifact files for this plan
- **Governance updates on rollback:**
  - ACTION_LOG entry with rollback reason
  - EXECUTION_PLAN: revert progress
  - This plan: status → cancelled

## Section 16: Prompt References

- **MATHS prompt template:** `agent_governance/master-maths-prompt-template.md`
- **Per-task prompts:**
  - `docs/prompts/codex-m365-cps-trkC-p4-operator-capability-map-T1.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkC-p4-operator-capability-map-T1-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkC-p4-operator-capability-map-T2.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkC-p4-operator-capability-map-T2-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkC-p4-operator-capability-map-T3.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkC-p4-operator-capability-map-T3-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkC-p4-operator-capability-map-T4.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkC-p4-operator-capability-map-T4-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkC-p4-operator-capability-map-T5.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkC-p4-operator-capability-map-T5-prompt.txt` (kickoff)

## Section 17: Traceability

### Files created by this plan

- **Notebooks:** N/A (non-math scope)
- **Invariants:** N/A
- **Lemmas:** N/A
- **Code files:** see Section 5 allowlist
- **Config/artifact files:** see per-task deliverables

### Index updates required

- **Traceability index:** N/A
- **Invariant index:** N/A
- **Math README:** N/A
- **Lemmas appendix:** N/A
- **EXECUTION_PLAN:** add this plan as authorized work (both repos)
- **ACTION_LOG:** entry per task

## Section 18: Governance Closure

On plan completion, update:

- [ ] `docs/platform/CODDEX_ACTION_LOG.md` (UCP) — entry with plan ref, alignment, timestamp
- [ ] `Operations/ACTION_LOG.md` (M365) — mirror entry
- [ ] `docs/platform/EXECUTION_PLAN.md` (UCP) — mark complete
- [ ] `Operations/EXECUTION_PLAN.md` (M365) — mark complete
- [ ] `docs/platform/PROJECT_STATUS.md` (UCP) — update if milestone
- [ ] This plan: status → complete; date_updated → today

## Section 19: Execution Outcome

_Filled during/after execution. Do not pre-fill._

### Task checklist

- [ ] T1 — Generate capability map document — Evidence:
- [ ] T2 — Add capability map to M365 docs/ — Evidence:
- [ ] T3 — Add operator-facing capability map to UCP docs — Evidence:
- [ ] T4 — Make regeneration a CI artifact — Evidence:
- [ ] T5 — Pre-commit + commit — Evidence:

### Gate checklist

- [ ] CHECK:C0 — Parent phase C4 integration — Result:

### Final decision

- **Decision:** _(GO | NO-GO)_
- **Approved by:** _(name + role)_
- **Completion timestamp:** _(YYYY-MM-DD HH:MM:SS TZ)_

## Section 20: When Blocked

```
STATUS: BLOCKED
TASK: <task-id or gate-id>
REASON: <description>
MISSING: <list of what is needed>
NEXT ALLOWED ACTION: <resolution path>
```

### Escalation path

- **Primary:** Phil Siniscalchi (Founder/Owner)
- **Secondary:** Engineering lead

## Section 21: Agent Constraints

- Do not touch files outside Section 5 file allowlist.
- Do not skip or reorder tasks (Section 7 strict ordering).
- Do not modify thresholds or invariants to make gates green without owner approval.
- Do not execute until plan status is approved.
- Reference plan:{plan-id}:{task-id} in all action log entries and commits.
- Do not add tasks, gates, or deliverables not in this plan without owner approval.
- Use .venv/bin/python for all Python commands.
- Call validate_action MCP tool before any write operation (UCP server).
- Each child phase commits locally; no push until parent-phase GATE is green.
- Each parent-phase GATE pushes to feat/m365-cps-trk{X} branch only.
- Each track GATE merges to development (UCP) and main (M365) only after live tenant smoke green.

## Section 22: References

- **North Star:** `docs/NORTH_STAR.md` (UCP) / `Operations/NORTHSTAR.md` (M365)
- **Execution Plan:** `docs/platform/EXECUTION_PLAN.md` (UCP) / `Operations/EXECUTION_PLAN.md` (M365)
- **Action Log:** `docs/platform/CODDEX_ACTION_LOG.md` (UCP) / `Operations/ACTION_LOG.md` (M365)
- **Parent plan:** `plan:m365-cps-trkC-truth-in-advertising`
- **Master plan:** `plan:m365-capability-pack-surface-remediation`
- **MATHS prompt template:** `agent_governance/master-maths-prompt-template.md`
- **Plan template:** `agent_governance/PLAN_TEMPLATE.md`

---
<!-- Generated by scripts/generate_m365_cps_scaffold.py on 2026-05-01 -->
