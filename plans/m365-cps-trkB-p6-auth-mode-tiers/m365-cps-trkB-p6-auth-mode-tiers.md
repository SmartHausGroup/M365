# Parent Phase B6 — Auth-Mode Tier System

## Section 1: Plan Header

- **Plan ID:** `plan:m365-cps-trkB-p6-auth-mode-tiers`
- **Parent Plan ID:** `plan:m365-cps-trkB-coverage`
- **Title:** Parent Phase B6 — Auth-Mode Tier System
- **Version:** 1.0
- **Status:** approved
- **Owner:** Phil Siniscalchi (Founder/Owner)
- **Date Created:** 2026-05-01
- **Date Updated:** 2026-05-01
- **North Star Ref:** `docs/NORTH_STAR.md`
- **Execution Plan Ref:** docs/platform/EXECUTION_PLAN.md - M365 CPS Track B P6
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
  - Introduce read-only / standard / admin tiers at m365_auth_start. Token store records tier; registry actions declare min_tier; admit() enforces.
- **Intent doc ref:** captured in this plan
- **Intent verification:** Tasks T1..T8 together satisfy this parent phase's objective.

## Section 4: Objective

- **Objective:** Introduce read-only / standard / admin tiers at m365_auth_start. Token store records tier; registry actions declare min_tier; admit() enforces.
- **Current state:** Parent phase scope draft; no implementation yet.
- **Target state:** All child tasks complete; GATE green; commit + push to feat/m365-cps-trkB.

## Section 5: Scope

### In scope

- Define scope tier sets
- Update m365_auth_start to accept tier
- Update token store to record tier
- Update registry actions to declare min_tier
- Update admit() to enforce tier
- Unit tests both repos
- Live tenant smoke (each tier)
- Pre-commit + commit

### Out of scope

- Anything outside this parent's allowlist

### File allowlist

- `M365: src/m365_runtime/auth/oauth.py`
- `M365: src/m365_runtime/auth/token_store.py`
- `M365: src/m365_runtime/graph/registry.py`
- `M365: tests/test_m365_auth_tiers.py`
- `M365: tests/test_token_store_tier.py`
- `M365: tests/test_m365_admit_tier.py`
- `UCP: src/ucp/m365_tools.py`
- `UCP: tests/test_m365_integration.py`
- `M365: docs/contracts/m365_auth_tiers.md`

### File denylist

- `Files outside auth/registry surface`
- `Any file not in allowlist of the active child-phase task`

### Scope fence rule

Agent must STOP and re-scope if any file outside the allowlist is needed. Emit BLOCKED.

## Section 6: Requirements

### R5

- **Ref:** `plan:m365-cps-trkB-p6-auth-mode-tiers:R5`
- **Description:** Carry-through of master R5; this parent phase contributes scoped behavior.
- **Acceptance criteria:** Per-task exit criteria; parent GATE passes.
- **Depends on:** none
- **User intent trace:** Master R5

### R8

- **Ref:** `plan:m365-cps-trkB-p6-auth-mode-tiers:R8`
- **Description:** Carry-through of master R8; this parent phase contributes scoped behavior.
- **Acceptance criteria:** Per-task exit criteria; parent GATE passes.
- **Depends on:** none
- **User intent trace:** Master R8

## Section 7: Execution Sequence

- **Ordering:** ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8']
- **Stop on first failure:** true
- **Strict ordering rule:** Do not start task N+1 until task N exit criteria are met.
- **MATHS phase mapping:** N/A (non-math scope)

## Section 8: Task Breakdown

### T1 — Define scope tier sets

- **Ref:** `plan:m365-cps-trkB-p6-auth-mode-tiers:T1`
- **Description:** Document the three tiers and their Graph scope sets: read-only={User.Read, Mail.Read, Calendars.Read, Sites.Read.All, Files.Read.All, Team.ReadBasic.All}; standard=read-only + write scopes for Mail/Calendar/Files; admin=standard + Directory.ReadWrite.All, RoleManagement.ReadWrite.Directory.
- **Requirement refs:** R5
- **Depends on:** none
- **MATHS phase:** N/A
- **Deliverables:**
  - docs/contracts/m365_auth_tiers.md
- **Exit criteria:**
  - Doc committed
- **Validation command:** `test -f $M365_ROOT/docs/contracts/m365_auth_tiers.md`
- **Files to modify:**
  - M365: docs/contracts/m365_auth_tiers.md (new)

### T2 — Update m365_auth_start to accept tier

- **Ref:** `plan:m365-cps-trkB-p6-auth-mode-tiers:T2`
- **Description:** Add tier parameter to m365_auth_start endpoint and OAuth flow. Default tier=read-only.
- **Requirement refs:** R5
- **Depends on:** T1
- **MATHS phase:** N/A
- **Deliverables:**
  - src/m365_runtime/auth/oauth.py with tier param
- **Exit criteria:**
  - m365_auth_start(tier='standard') succeeds; scope set matches
- **Validation command:** `cd $M365_ROOT && .venv/bin/python -m pytest tests/test_m365_auth_tiers.py -x`
- **Files to modify:**
  - M365: src/m365_runtime/auth/oauth.py

### T3 — Update token store to record tier

- **Ref:** `plan:m365-cps-trkB-p6-auth-mode-tiers:T3`
- **Description:** Token store schema gains tier field. Migration: existing tokens default to read-only.
- **Requirement refs:** R5
- **Depends on:** T2
- **MATHS phase:** N/A
- **Deliverables:**
  - src/m365_runtime/auth/token_store.py with tier
- **Exit criteria:**
  - token_store.read() returns tier
- **Validation command:** `cd $M365_ROOT && .venv/bin/python -m pytest tests/test_token_store_tier.py -x`
- **Files to modify:**
  - M365: src/m365_runtime/auth/token_store.py

### T4 — Update registry actions to declare min_tier

- **Ref:** `plan:m365-cps-trkB-p6-auth-mode-tiers:T4`
- **Description:** Each ActionSpec gains min_tier field (read-only by default; admin reads use admin).
- **Requirement refs:** R5
- **Depends on:** T3
- **MATHS phase:** N/A
- **Deliverables:**
  - src/m365_runtime/graph/registry.py with min_tier on each spec
- **Exit criteria:**
  - get_action returns spec with min_tier
- **Validation command:** `cd $M365_ROOT && .venv/bin/python -c "from m365_runtime.graph.registry import get_action; assert get_action('graph.users.list').min_tier == 'read-only'"`
- **Files to modify:**
  - M365: src/m365_runtime/graph/registry.py

### T5 — Update admit() to enforce tier

- **Ref:** `plan:m365-cps-trkB-p6-auth-mode-tiers:T5`
- **Description:** admit() rejects with 'tier_insufficient' if session.tier < spec.min_tier.
- **Requirement refs:** R5
- **Depends on:** T4
- **MATHS phase:** N/A
- **Deliverables:**
  - src/m365_runtime/graph/registry.py admit() updated
- **Exit criteria:**
  - admit('admin-action', session_tier='read-only') returns ('denied', 'tier_insufficient')
- **Validation command:** `cd $M365_ROOT && .venv/bin/python -m pytest tests/test_m365_admit_tier.py -x`
- **Files to modify:**
  - M365: src/m365_runtime/graph/registry.py

### T6 — Unit tests both repos

- **Ref:** `plan:m365-cps-trkB-p6-auth-mode-tiers:T6`
- **Description:** M365: test_m365_auth_tiers, test_m365_admit_tier. UCP: test_m365_auth_start_tier_passthrough.
- **Requirement refs:** R5
- **Depends on:** T5
- **MATHS phase:** N/A
- **Deliverables:**
  - Test files added
- **Exit criteria:**
  - pytest exits 0
- **Validation command:** `cd $M365_ROOT && .venv/bin/python -m pytest -k tier -x && cd $UCP_ROOT && .venv/bin/python -m pytest -k tier -x`

### T7 — Live tenant smoke (each tier)

- **Ref:** `plan:m365-cps-trkB-p6-auth-mode-tiers:T7`
- **Description:** Auth at each tier; verify scope set returned by Graph matches expected.
- **Requirement refs:** R5
- **Depends on:** T6
- **MATHS phase:** N/A
- **Deliverables:**
  - Diagnostic evidence
- **Exit criteria:**
  - All three tiers work
- **Validation command:** `cd $UCP_ROOT && .venv/bin/python tests/integration/m365_auth_tiers_live.py`

### T8 — Pre-commit + commit

- **Ref:** `plan:m365-cps-trkB-p6-auth-mode-tiers:T8`
- **Description:** Standard validation + commit.
- **Requirement refs:** R8
- **Depends on:** T7
- **MATHS phase:** N/A
- **Deliverables:**
  - Commit in both repos
- **Exit criteria:**
  - git log shows commit
- **Validation command:** `cd $M365_ROOT && pre-commit run --all-files && make test && git log --oneline -1 | grep 'plan:m365-cps-trkB-p6'`

## Section 9: Gate Checks

### CHECK:C0 — Parent phase B6 integration

- **Description:** All child tasks T1..T8 green; integration test pass
- **Task ref:** T1..T8
- **Validation command:** `cd $UCP_ROOT && .venv/bin/python tests/integration/m365_auth_tiers_e2e.py`
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
| docs/contracts/m365_auth_tiers.md | Markdown | T1 | per-task | see Section 8 / T1 |
| src/m365_runtime/auth/oauth.py with tier param | varies | T2 | per-task | see Section 8 / T2 |
| src/m365_runtime/auth/token_store.py with tier | varies | T3 | per-task | see Section 8 / T3 |
| src/m365_runtime/graph/registry.py with min_tier on each spec | varies | T4 | per-task | see Section 8 / T4 |
| src/m365_runtime/graph/registry.py admit() updated | varies | T5 | per-task | see Section 8 / T5 |
| Test files added | varies | T6 | per-task | see Section 8 / T6 |
| Diagnostic evidence | varies | T7 | per-task | see Section 8 / T7 |
| Commit in both repos | varies | T8 | per-task | see Section 8 / T8 |

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
  - `docs/prompts/codex-m365-cps-trkB-p6-auth-mode-tiers-T1.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p6-auth-mode-tiers-T1-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p6-auth-mode-tiers-T2.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p6-auth-mode-tiers-T2-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p6-auth-mode-tiers-T3.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p6-auth-mode-tiers-T3-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p6-auth-mode-tiers-T4.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p6-auth-mode-tiers-T4-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p6-auth-mode-tiers-T5.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p6-auth-mode-tiers-T5-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p6-auth-mode-tiers-T6.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p6-auth-mode-tiers-T6-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p6-auth-mode-tiers-T7.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p6-auth-mode-tiers-T7-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p6-auth-mode-tiers-T8.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p6-auth-mode-tiers-T8-prompt.txt` (kickoff)

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

- [ ] T1 — Define scope tier sets — Evidence:
- [ ] T2 — Update m365_auth_start to accept tier — Evidence:
- [ ] T3 — Update token store to record tier — Evidence:
- [ ] T4 — Update registry actions to declare min_tier — Evidence:
- [ ] T5 — Update admit() to enforce tier — Evidence:
- [ ] T6 — Unit tests both repos — Evidence:
- [ ] T7 — Live tenant smoke (each tier) — Evidence:
- [ ] T8 — Pre-commit + commit — Evidence:

### Gate checklist

- [ ] CHECK:C0 — Parent phase B6 integration — Result:

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
- **Parent plan:** `plan:m365-cps-trkB-coverage`
- **Master plan:** `plan:m365-capability-pack-surface-remediation`
- **MATHS prompt template:** `agent_governance/master-maths-prompt-template.md`
- **Plan template:** `agent_governance/PLAN_TEMPLATE.md`

---
<!-- Generated by scripts/generate_m365_cps_scaffold.py on 2026-05-01 -->
