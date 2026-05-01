# Track B — Coverage Build-Out

## Section 1: Plan Header

- **Plan ID:** `plan:m365-cps-trkB-coverage`
- **Parent Plan ID:** `plan:m365-capability-pack-surface-remediation`
- **Title:** Track B — Coverage Build-Out
- **Version:** 1.0
- **Status:** draft
- **Owner:** Phil Siniscalchi (Founder/Owner)
- **Date Created:** 2026-05-01
- **Date Updated:** 2026-05-01
- **North Star Ref:** `docs/NORTH_STAR.md`
- **Execution Plan Ref:** docs/platform/EXECUTION_PLAN.md - M365 CPS Track B
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
  - Execute Track B per master plan.
- **Intent doc ref:** captured in this plan
- **Intent verification:** Tasks T1..T7 drive each parent-phase plan to completion.

## Section 4: Objective

- **Objective:** Track B — Coverage Build-Out
- **Current state:** Track B parent-phase plans defined; status draft; no execution started.
- **Target state:** All Track B parent-phase plans status: complete; branch feat/m365-cps-trkB merged.

## Section 5: Scope

### In scope

- plan:m365-cps-trkB-p1-sharepoint-reads
- plan:m365-cps-trkB-p2-calendar-reads
- plan:m365-cps-trkB-p3-mail-reads
- plan:m365-cps-trkB-p4-health-and-reports
- plan:m365-cps-trkB-p5-directory-and-teams
- plan:m365-cps-trkB-p6-auth-mode-tiers
- plan:m365-cps-trkB-p7-end-to-end-and-repackage

### Out of scope

- Anything covered by sibling tracks

### File allowlist

- `src/ucp/m365_tools.py`
- `src/ucp/runtime/release_artifacts.py`
- `src/ucp/runtime/m365_runtime_health.py`
- `tests/test_m365_*.py`
- `configs/mcp_packs.yaml`
- `docs/platform/CODDEX_ACTION_LOG.md`
- `docs/platform/EXECUTION_PLAN.md`
- `docs/platform/PROJECT_STATUS.md`
- `plans/m365-capability-pack-surface-remediation/**`
- `plans/m365-cps-*/**`
- `docs/prompts/codex-m365-cps-*.md`
- `docs/prompts/codex-m365-cps-*.txt`
- `src/m365_runtime/graph/registry.py`
- `src/m365_runtime/graph/actions.py`
- `src/m365_runtime/graph/client.py`
- `src/ucp_m365_pack/client.py`
- `src/ucp_m365_pack/contracts.py`
- `registry/action_registry.yaml`
- `registry/agents.yaml`
- `tests/**`
- `Operations/ACTION_LOG.md`
- `Operations/EXECUTION_PLAN.md`
- `plans/m365-capability-pack-surface-remediation/**`
- `plans/m365-cps-*/**`
- `docs/prompts/codex-m365-cps-*.md`
- `docs/prompts/codex-m365-cps-*.txt`
- `CHANGELOG.md`

### File denylist

- `apps/desktop/**`
- `src/ucp/runtime/pack_registry.py`
- `Power Platform executor sources`
- `archived/**`
- `Any file not in allowlist of the active child-phase plan`

### Scope fence rule

Agent must STOP and re-scope if any file outside the allowlist is needed. Emit BLOCKED.

## Section 6: Requirements

### R4

- **Ref:** `plan:m365-cps-trkB-coverage:R4`
- **Description:** Track B requirement carry-through from master plan R4.
- **Acceptance criteria:** All parent phases satisfying master R4 are complete.
- **Depends on:** none
- **User intent trace:** Master R4

### R5

- **Ref:** `plan:m365-cps-trkB-coverage:R5`
- **Description:** Track B requirement carry-through from master plan R5.
- **Acceptance criteria:** All parent phases satisfying master R5 are complete.
- **Depends on:** none
- **User intent trace:** Master R5

### R8

- **Ref:** `plan:m365-cps-trkB-coverage:R8`
- **Description:** Track B requirement carry-through from master plan R8.
- **Acceptance criteria:** All parent phases satisfying master R8 are complete.
- **Depends on:** none
- **User intent trace:** Master R8

## Section 7: Execution Sequence

- **Ordering:** ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']
- **Stop on first failure:** true
- **Strict ordering rule:** Do not start task N+1 until task N exit criteria are met.
- **MATHS phase mapping:** N/A (non-math scope)

## Section 8: Task Breakdown

### T1 — SharePoint Reads

- **Ref:** `plan:m365-cps-trkB-coverage:T1`
- **Description:** Add sites.list, sites.get, lists.list, lists.get, lists.items, drives.children to runtime registry + alias table + YAML mirror. Coverage gap closure for SharePoint.
- **Requirement refs:** R4, R5, R8
- **Depends on:** none
- **MATHS phase:** N/A
- **Deliverables:**
  - plan:m365-cps-trkB-p1-sharepoint-reads status: complete
- **Exit criteria:**
  - plan:m365-cps-trkB-p1-sharepoint-reads GATE green; commit + push to feat/m365-cps-trkB
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkB-p1-sharepoint-reads`
- **Implementation notes:** Sub-plan: plan:m365-cps-trkB-p1-sharepoint-reads

### T2 — Calendar Reads

- **Ref:** `plan:m365-cps-trkB-coverage:T2`
- **Description:** Add calendar.list, calendar.get, events.list, calendar.availability to runtime + alias + YAML.
- **Requirement refs:** R4, R5, R8
- **Depends on:** T1
- **MATHS phase:** N/A
- **Deliverables:**
  - plan:m365-cps-trkB-p2-calendar-reads status: complete
- **Exit criteria:**
  - plan:m365-cps-trkB-p2-calendar-reads GATE green; commit + push to feat/m365-cps-trkB
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkB-p2-calendar-reads`
- **Implementation notes:** Sub-plan: plan:m365-cps-trkB-p2-calendar-reads

### T3 — Mail Reads

- **Ref:** `plan:m365-cps-trkB-coverage:T3`
- **Description:** Add mail.list, mail.message_get, mail.attachments to runtime + alias + YAML.
- **Requirement refs:** R4, R5, R8
- **Depends on:** T2
- **MATHS phase:** N/A
- **Deliverables:**
  - plan:m365-cps-trkB-p3-mail-reads status: complete
- **Exit criteria:**
  - plan:m365-cps-trkB-p3-mail-reads GATE green; commit + push to feat/m365-cps-trkB
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkB-p3-mail-reads`
- **Implementation notes:** Sub-plan: plan:m365-cps-trkB-p3-mail-reads

### T4 — Service Health & Reports

- **Ref:** `plan:m365-cps-trkB-coverage:T4`
- **Description:** Add health.overview, health.issues, health.messages, reports.users_active, reports.email_activity, reports.teams_activity, reports.sharepoint_usage, reports.onedrive_usage.
- **Requirement refs:** R4, R5, R8
- **Depends on:** T3
- **MATHS phase:** N/A
- **Deliverables:**
  - plan:m365-cps-trkB-p4-health-and-reports status: complete
- **Exit criteria:**
  - plan:m365-cps-trkB-p4-health-and-reports GATE green; commit + push to feat/m365-cps-trkB
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkB-p4-health-and-reports`
- **Implementation notes:** Sub-plan: plan:m365-cps-trkB-p4-health-and-reports

### T5 — Directory & Teams Reads

- **Ref:** `plan:m365-cps-trkB-coverage:T5`
- **Description:** Add directory.domains, directory.roles, teams.get, channels.list, channels.get.
- **Requirement refs:** R4, R5, R8
- **Depends on:** T4
- **MATHS phase:** N/A
- **Deliverables:**
  - plan:m365-cps-trkB-p5-directory-and-teams status: complete
- **Exit criteria:**
  - plan:m365-cps-trkB-p5-directory-and-teams GATE green; commit + push to feat/m365-cps-trkB
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkB-p5-directory-and-teams`
- **Implementation notes:** Sub-plan: plan:m365-cps-trkB-p5-directory-and-teams

### T6 — Auth-Mode Tier System

- **Ref:** `plan:m365-cps-trkB-coverage:T6`
- **Description:** Introduce read-only / standard / admin tiers at m365_auth_start. Token store records tier; registry actions declare min_tier; admit() enforces.
- **Requirement refs:** R4, R5, R8
- **Depends on:** T5
- **MATHS phase:** N/A
- **Deliverables:**
  - plan:m365-cps-trkB-p6-auth-mode-tiers status: complete
- **Exit criteria:**
  - plan:m365-cps-trkB-p6-auth-mode-tiers GATE green; commit + push to feat/m365-cps-trkB
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkB-p6-auth-mode-tiers`
- **Implementation notes:** Sub-plan: plan:m365-cps-trkB-p6-auth-mode-tiers

### T7 — Track B End-to-End & Repackage

- **Ref:** `plan:m365-cps-trkB-coverage:T7`
- **Description:** Full live-tenant coverage e2e; cut M365 1.2.0 release; bind UCP to it; governance closure.
- **Requirement refs:** R4, R5, R8
- **Depends on:** T6
- **MATHS phase:** N/A
- **Deliverables:**
  - plan:m365-cps-trkB-p7-end-to-end-and-repackage status: complete
- **Exit criteria:**
  - plan:m365-cps-trkB-p7-end-to-end-and-repackage GATE green; commit + push to feat/m365-cps-trkB
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkB-p7-end-to-end-and-repackage`
- **Implementation notes:** Sub-plan: plan:m365-cps-trkB-p7-end-to-end-and-repackage

## Section 9: Gate Checks

### CHECK:C1 — Parent Phase B1 — SharePoint Reads complete

- **Description:** plan:m365-cps-trkB-p1-sharepoint-reads status == complete with GATE evidence
- **Task ref:** T1
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkB-p1-sharepoint-reads`
- **Pass criteria:** Plan status complete; GATE validation_command exit 0
- **Fail action:** block

### CHECK:C2 — Parent Phase B2 — Calendar Reads complete

- **Description:** plan:m365-cps-trkB-p2-calendar-reads status == complete with GATE evidence
- **Task ref:** T2
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkB-p2-calendar-reads`
- **Pass criteria:** Plan status complete; GATE validation_command exit 0
- **Fail action:** block

### CHECK:C3 — Parent Phase B3 — Mail Reads complete

- **Description:** plan:m365-cps-trkB-p3-mail-reads status == complete with GATE evidence
- **Task ref:** T3
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkB-p3-mail-reads`
- **Pass criteria:** Plan status complete; GATE validation_command exit 0
- **Fail action:** block

### CHECK:C4 — Parent Phase B4 — Service Health & Reports complete

- **Description:** plan:m365-cps-trkB-p4-health-and-reports status == complete with GATE evidence
- **Task ref:** T4
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkB-p4-health-and-reports`
- **Pass criteria:** Plan status complete; GATE validation_command exit 0
- **Fail action:** block

### CHECK:C5 — Parent Phase B5 — Directory & Teams Reads complete

- **Description:** plan:m365-cps-trkB-p5-directory-and-teams status == complete with GATE evidence
- **Task ref:** T5
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkB-p5-directory-and-teams`
- **Pass criteria:** Plan status complete; GATE validation_command exit 0
- **Fail action:** block

### CHECK:C6 — Parent Phase B6 — Auth-Mode Tier System complete

- **Description:** plan:m365-cps-trkB-p6-auth-mode-tiers status == complete with GATE evidence
- **Task ref:** T6
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkB-p6-auth-mode-tiers`
- **Pass criteria:** Plan status complete; GATE validation_command exit 0
- **Fail action:** block

### CHECK:C7 — Parent Phase B7 — Track B End-to-End & Repackage complete

- **Description:** plan:m365-cps-trkB-p7-end-to-end-and-repackage status == complete with GATE evidence
- **Task ref:** T7
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkB-p7-end-to-end-and-repackage`
- **Pass criteria:** Plan status complete; GATE validation_command exit 0
- **Fail action:** block

### Decision rule

- **GO:** All gates pass.
- **NO-GO:** Any gate fails.

### No-go triggers

- Any parent-phase plan in Track B fails its GATE
- Branch feat/m365-cps-trkB merge conflict that cannot be resolved without scope drift

## Section 10: Determinism Requirements

N/A — non-math scope. Tests must be hermetic; live tenant only in GATE smoke tests.

## Section 11: Artifacts

| Path | Format | Producer | Schema ref | Validation |
|------|--------|----------|------------|------------|
| plan:m365-cps-trkB-p1-sharepoint-reads status: complete | varies | T1 | per-task | see Section 8 / T1 |
| plan:m365-cps-trkB-p2-calendar-reads status: complete | varies | T2 | per-task | see Section 8 / T2 |
| plan:m365-cps-trkB-p3-mail-reads status: complete | varies | T3 | per-task | see Section 8 / T3 |
| plan:m365-cps-trkB-p4-health-and-reports status: complete | varies | T4 | per-task | see Section 8 / T4 |
| plan:m365-cps-trkB-p5-directory-and-teams status: complete | varies | T5 | per-task | see Section 8 / T5 |
| plan:m365-cps-trkB-p6-auth-mode-tiers status: complete | varies | T6 | per-task | see Section 8 / T6 |
| plan:m365-cps-trkB-p7-end-to-end-and-repackage status: complete | varies | T7 | per-task | see Section 8 / T7 |

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
| Track B parent phase scope creep | medium | Per-parent allowlist; scope fence | mitigated |

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
- **Prompt doc:** N/A (this is a higher-level plan; per-task prompts live with parent-phase plans)

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

- [ ] T1 — SharePoint Reads — Evidence:
- [ ] T2 — Calendar Reads — Evidence:
- [ ] T3 — Mail Reads — Evidence:
- [ ] T4 — Service Health & Reports — Evidence:
- [ ] T5 — Directory & Teams Reads — Evidence:
- [ ] T6 — Auth-Mode Tier System — Evidence:
- [ ] T7 — Track B End-to-End & Repackage — Evidence:

### Gate checklist

- [ ] CHECK:C1 — Parent Phase B1 — SharePoint Reads complete — Result:
- [ ] CHECK:C2 — Parent Phase B2 — Calendar Reads complete — Result:
- [ ] CHECK:C3 — Parent Phase B3 — Mail Reads complete — Result:
- [ ] CHECK:C4 — Parent Phase B4 — Service Health & Reports complete — Result:
- [ ] CHECK:C5 — Parent Phase B5 — Directory & Teams Reads complete — Result:
- [ ] CHECK:C6 — Parent Phase B6 — Auth-Mode Tier System complete — Result:
- [ ] CHECK:C7 — Parent Phase B7 — Track B End-to-End & Repackage complete — Result:

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
- **Parent plan:** `plan:m365-capability-pack-surface-remediation`
- **Master plan:** `plan:m365-capability-pack-surface-remediation`
- **MATHS prompt template:** `agent_governance/master-maths-prompt-template.md`
- **Plan template:** `agent_governance/PLAN_TEMPLATE.md`

---
<!-- Generated by scripts/generate_m365_cps_scaffold.py on 2026-05-01 -->
