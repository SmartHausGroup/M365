# Parent Phase A4 — Track A End-to-End Integration

## Section 1: Plan Header

- **Plan ID:** `plan:m365-cps-trkA-p4-end-to-end`
- **Parent Plan ID:** `plan:m365-cps-trkA-observability`
- **Title:** Parent Phase A4 — Track A End-to-End Integration
- **Version:** 1.0
- **Status:** approved
- **Owner:** Phil Siniscalchi (Founder/Owner)
- **Date Created:** 2026-05-01
- **Date Updated:** 2026-05-01
- **North Star Ref:** `docs/NORTH_STAR.md`
- **Execution Plan Ref:** docs/platform/EXECUTION_PLAN.md - M365 CPS Track A P4
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
  - Live UCP+M365 e2e validation of Track A; governance closure; commit + push + merge.
- **Intent doc ref:** captured in this plan
- **Intent verification:** Tasks T1..T4 together satisfy this parent phase's objective.

## Section 4: Objective

- **Objective:** Live UCP+M365 e2e validation of Track A; governance closure; commit + push + merge.
- **Current state:** Parent phase scope draft; no implementation yet.
- **Target state:** All child tasks complete; GATE green; commit + push to feat/m365-cps-trkA.

## Section 5: Scope

### In scope

- Live UCP+M365 spin-up integration test
- Verify status semantics on real failed calls
- Verify pre-flight diagnostic against live tenant
- Update CHANGELOG / EXECUTION_PLAN / ACTION_LOG (both repos)

### Out of scope

- Anything outside this parent's allowlist

### File allowlist

- `UCP: tests/integration/m365_cps_trkA_e2e.py`
- `UCP: tests/integration/m365_unknown_action_live.py`
- `UCP: tests/integration/m365_preflight_live.py`
- `UCP: docs/platform/EXECUTION_PLAN.md`
- `UCP: docs/platform/CODDEX_ACTION_LOG.md`
- `M365: Operations/EXECUTION_PLAN.md`
- `M365: Operations/ACTION_LOG.md`
- `M365: CHANGELOG.md`

### File denylist

- `Source files (those are p1-p3)`
- `Any file not in allowlist of the active child-phase task`

### Scope fence rule

Agent must STOP and re-scope if any file outside the allowlist is needed. Emit BLOCKED.

## Section 6: Requirements

### R1

- **Ref:** `plan:m365-cps-trkA-p4-end-to-end:R1`
- **Description:** Carry-through of master R1; this parent phase contributes scoped behavior.
- **Acceptance criteria:** Per-task exit criteria; parent GATE passes.
- **Depends on:** none
- **User intent trace:** Master R1

### R2

- **Ref:** `plan:m365-cps-trkA-p4-end-to-end:R2`
- **Description:** Carry-through of master R2; this parent phase contributes scoped behavior.
- **Acceptance criteria:** Per-task exit criteria; parent GATE passes.
- **Depends on:** none
- **User intent trace:** Master R2

### R3

- **Ref:** `plan:m365-cps-trkA-p4-end-to-end:R3`
- **Description:** Carry-through of master R3; this parent phase contributes scoped behavior.
- **Acceptance criteria:** Per-task exit criteria; parent GATE passes.
- **Depends on:** none
- **User intent trace:** Master R3

### R8

- **Ref:** `plan:m365-cps-trkA-p4-end-to-end:R8`
- **Description:** Carry-through of master R8; this parent phase contributes scoped behavior.
- **Acceptance criteria:** Per-task exit criteria; parent GATE passes.
- **Depends on:** none
- **User intent trace:** Master R8

## Section 7: Execution Sequence

- **Ordering:** ['T1', 'T2', 'T3', 'T4']
- **Stop on first failure:** true
- **Strict ordering rule:** Do not start task N+1 until task N exit criteria are met.
- **MATHS phase mapping:** N/A (non-math scope)

## Section 8: Task Breakdown

### T1 — Live UCP+M365 spin-up integration test

- **Ref:** `plan:m365-cps-trkA-p4-end-to-end:T1`
- **Description:** Spin up UCP MCP server and M365 runtime locally. Authenticate via device-code. Run end-to-end: m365_inventory call, m365_auth_check call, unknown action call.
- **Requirement refs:** R1, R2, R3
- **Depends on:** none
- **MATHS phase:** N/A
- **Deliverables:**
  - Live integration evidence in artifacts/diagnostics/m365_cps_trkA_e2e.json
- **Exit criteria:**
  - All three calls return correct shapes; status codes honest
- **Validation command:** `cd $UCP_ROOT && .venv/bin/python tests/integration/m365_cps_trkA_e2e.py`
- **Files to modify:**
  - UCP: tests/integration/m365_cps_trkA_e2e.py (new)

### T2 — Verify status semantics on real failed calls

- **Ref:** `plan:m365-cps-trkA-p4-end-to-end:T2`
- **Description:** Trigger known unknown actions against the live runtime. Verify response status_class == 'unknown_action'.
- **Requirement refs:** R1
- **Depends on:** T1
- **MATHS phase:** N/A
- **Deliverables:**
  - Diagnostic evidence captured
- **Exit criteria:**
  - unknown_action observed for sites.list, calendar.list, mail.folders, etc.
- **Validation command:** `cd $UCP_ROOT && .venv/bin/python tests/integration/m365_unknown_action_live.py`

### T3 — Verify pre-flight diagnostic against live tenant

- **Ref:** `plan:m365-cps-trkA-p4-end-to-end:T3`
- **Description:** Call m365_auth_check after sign-in. Validate preflight.invokable_actions matches device-code-compatible actions and blocked_by_auth_mode shows the rest.
- **Requirement refs:** R3
- **Depends on:** T2
- **MATHS phase:** N/A
- **Deliverables:**
  - Diagnostic evidence captured
- **Exit criteria:**
  - preflight intersection accurate vs. registry auth_modes
- **Validation command:** `cd $UCP_ROOT && .venv/bin/python tests/integration/m365_preflight_live.py`

### T4 — Update CHANGELOG / EXECUTION_PLAN / ACTION_LOG (both repos)

- **Ref:** `plan:m365-cps-trkA-p4-end-to-end:T4`
- **Description:** Add Track A complete entries to CHANGELOG (M365), EXECUTION_PLAN.md (UCP and M365), and ACTION_LOG (both).
- **Requirement refs:** R8
- **Depends on:** T3
- **MATHS phase:** N/A
- **Deliverables:**
  - CHANGELOG entry
  - EXECUTION_PLAN entries
  - ACTION_LOG entries
- **Exit criteria:**
  - All four governance docs updated
- **Validation command:** `cd $UCP_ROOT && git diff --stat docs/platform/EXECUTION_PLAN.md docs/platform/CODDEX_ACTION_LOG.md && cd $M365_ROOT && git diff --stat Operations/EXECUTION_PLAN.md Operations/ACTION_LOG.md CHANGELOG.md`
- **Files to modify:**
  - UCP: docs/platform/EXECUTION_PLAN.md
  - UCP: docs/platform/CODDEX_ACTION_LOG.md
  - M365: Operations/EXECUTION_PLAN.md
  - M365: Operations/ACTION_LOG.md
  - M365: CHANGELOG.md

## Section 9: Gate Checks

### CHECK:C0 — Parent phase A4 integration

- **Description:** All child tasks T1..T4 green; integration test pass
- **Task ref:** T1..T4
- **Validation command:** `cd $UCP_ROOT && .venv/bin/python tests/integration/m365_cps_trkA_e2e.py`
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
| Live integration evidence in artifacts/diagnostics/m365_cps_trkA_e2e.json | JSON | T1 | per-task | see Section 8 / T1 |
| Diagnostic evidence captured | varies | T2 | per-task | see Section 8 / T2 |
| Diagnostic evidence captured | varies | T3 | per-task | see Section 8 / T3 |
| CHANGELOG entry | varies | T4 | per-task | see Section 8 / T4 |
| EXECUTION_PLAN entries | varies | T4 | per-task | see Section 8 / T4 |
| ACTION_LOG entries | varies | T4 | per-task | see Section 8 / T4 |

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
  - `docs/prompts/codex-m365-cps-trkA-p4-end-to-end-T1.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkA-p4-end-to-end-T1-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkA-p4-end-to-end-T2.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkA-p4-end-to-end-T2-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkA-p4-end-to-end-T3.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkA-p4-end-to-end-T3-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkA-p4-end-to-end-T4.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkA-p4-end-to-end-T4-prompt.txt` (kickoff)

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

- [ ] T1 — Live UCP+M365 spin-up integration test — Evidence:
- [ ] T2 — Verify status semantics on real failed calls — Evidence:
- [ ] T3 — Verify pre-flight diagnostic against live tenant — Evidence:
- [ ] T4 — Update CHANGELOG / EXECUTION_PLAN / ACTION_LOG (both repos) — Evidence:

### Gate checklist

- [ ] CHECK:C0 — Parent phase A4 integration — Result:

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
- **Parent plan:** `plan:m365-cps-trkA-observability`
- **Master plan:** `plan:m365-capability-pack-surface-remediation`
- **MATHS prompt template:** `agent_governance/master-maths-prompt-template.md`
- **Plan template:** `agent_governance/PLAN_TEMPLATE.md`

---
<!-- Generated by scripts/generate_m365_cps_scaffold.py on 2026-05-01 -->
