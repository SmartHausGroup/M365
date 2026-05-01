# Parent Phase A1 — Status Code Semantics Fix

## Section 1: Plan Header

- **Plan ID:** `plan:m365-cps-trkA-p1-status-code-semantics`
- **Parent Plan ID:** `plan:m365-cps-trkA-observability`
- **Title:** Parent Phase A1 — Status Code Semantics Fix
- **Version:** 1.0
- **Status:** approved
- **Owner:** Phil Siniscalchi (Founder/Owner)
- **Date Created:** 2026-05-01
- **Date Updated:** 2026-05-01
- **North Star Ref:** `docs/NORTH_STAR.md`
- **Execution Plan Ref:** docs/platform/EXECUTION_PLAN.md - M365 CPS Track A P1
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
  - Fix _denial_to_status to preserve unknown_action as a distinct status (not mutation_fence). Plumb the new status through M365 runtime and UCP tools surface. Unit + integration tests.
- **Intent doc ref:** captured in this plan
- **Intent verification:** Tasks T1..T8 together satisfy this parent phase's objective.

## Section 4: Objective

- **Objective:** Fix _denial_to_status to preserve unknown_action as a distinct status (not mutation_fence). Plumb the new status through M365 runtime and UCP tools surface. Unit + integration tests.
- **Current state:** Parent phase scope draft; no implementation yet.
- **Target state:** All child tasks complete; GATE green; commit + push to feat/m365-cps-trkA.

## Section 5: Scope

### In scope

- Read context for status code semantics
- Update _denial_to_status to preserve unknown_action
- Align actions.py callsite
- Update UCP m365_tools.py to surface unknown_action
- Add M365 unit tests for unknown_action
- Add UCP unit tests for unknown_action routing
- Pre-commit + make test in both repos
- Commit child phases (no push)

### Out of scope

- Anything outside this parent's allowlist

### File allowlist

- `M365: src/m365_runtime/graph/registry.py`
- `M365: src/m365_runtime/graph/actions.py`
- `M365: tests/test_m365_pack_client.py`
- `M365: tests/test_m365_pack_contracts.py`
- `UCP: src/ucp/m365_tools.py`
- `UCP: tests/test_m365_integration.py`

### File denylist

- `M365: src/m365_runtime/graph/client.py`
- `M365: registry/agents.yaml`
- `M365: registry/action_registry.yaml`
- `UCP: any file outside src/ucp/m365_tools.py and tests/`
- `Any file not in allowlist of the active child-phase task`

### Scope fence rule

Agent must STOP and re-scope if any file outside the allowlist is needed. Emit BLOCKED.

## Section 6: Requirements

### R1

- **Ref:** `plan:m365-cps-trkA-p1-status-code-semantics:R1`
- **Description:** Carry-through of master R1; this parent phase contributes scoped behavior.
- **Acceptance criteria:** Per-task exit criteria; parent GATE passes.
- **Depends on:** none
- **User intent trace:** Master R1

### R8

- **Ref:** `plan:m365-cps-trkA-p1-status-code-semantics:R8`
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

### T1 — Read context for status code semantics

- **Ref:** `plan:m365-cps-trkA-p1-status-code-semantics:T1`
- **Description:** Read M365 src/m365_runtime/graph/registry.py, actions.py end-to-end. Read UCP src/ucp/m365_tools.py. Document current _denial_to_status mapping behavior in commit notes.
- **Requirement refs:** R1
- **Depends on:** none
- **MATHS phase:** N/A
- **Deliverables:**
  - Read confirmation logged in implementation_notes of this task
- **Exit criteria:**
  - All three files read; current behavior documented
- **Validation command:** `test -f $M365_ROOT/src/m365_runtime/graph/registry.py && test -f $M365_ROOT/src/m365_runtime/graph/actions.py && test -f $UCP_ROOT/src/ucp/m365_tools.py`
- **Implementation notes:** Read-only task. No writes.
- **Files to read:**
  - M365: src/m365_runtime/graph/registry.py
  - M365: src/m365_runtime/graph/actions.py
  - UCP: src/ucp/m365_tools.py

### T2 — Update _denial_to_status to preserve unknown_action

- **Ref:** `plan:m365-cps-trkA-p1-status-code-semantics:T2`
- **Description:** In M365 src/m365_runtime/graph/registry.py, change the unknown_action branch return value from 'mutation_fence' to 'unknown_action'. Preserve all other branches exactly.
- **Requirement refs:** R1
- **Depends on:** T1
- **MATHS phase:** N/A
- **Deliverables:**
  - src/m365_runtime/graph/registry.py with_denial_to_status updated
- **Exit criteria:**
  - _denial_to_status('unknown_action') returns 'unknown_action'
  - _denial_to_status('mutation_fence') returns 'mutation_fence'
  - all other branches unchanged
- **Validation command:** `.venv/bin/python -c "from m365_runtime.graph.registry import _denial_to_status; assert _denial_to_status('unknown_action') == 'unknown_action'; assert _denial_to_status('mutation_fence') == 'mutation_fence'; assert _denial_to_status('permission_missing') == 'permission_missing'; assert _denial_to_status('auth_mode_mismatch') == 'auth_required'; assert _denial_to_status('foo') == 'policy_denied'; print('OK')"`
- **Files to modify:**
  - M365: src/m365_runtime/graph/registry.py

### T3 — Align actions.py callsite

- **Ref:** `plan:m365-cps-trkA-p1-status-code-semantics:T3`
- **Description:** Verify ActionInvocation.status_class plumbs the new 'unknown_action' value through unchanged. No code change expected; this is a verification + assertion task.
- **Requirement refs:** R1
- **Depends on:** T2
- **MATHS phase:** N/A
- **Deliverables:**
  - Confirmation that no callsite remaps unknown_action
- **Exit criteria:**
  - grep -r 'unknown_action' in actions.py shows no remapping
  - test_action_invocation_unknown_status passes
- **Validation command:** `cd $M365_ROOT && grep -n 'unknown_action' src/m365_runtime/graph/actions.py || echo 'no remap callsites - OK'`
- **Files to read:**
  - M365: src/m365_runtime/graph/actions.py

### T4 — Update UCP m365_tools.py to surface unknown_action

- **Ref:** `plan:m365-cps-trkA-p1-status-code-semantics:T4`
- **Description:** In UCP src/ucp/m365_tools.py, ensure the_m365_execute path surfaces status_class == 'unknown_action' without remapping it back to mutation_fence.
- **Requirement refs:** R1
- **Depends on:** T3
- **MATHS phase:** N/A
- **Deliverables:**
  - src/ucp/m365_tools.py with no unknown_action remap
- **Exit criteria:**
  - grep on m365_tools.py shows no 'mutation_fence' substitution for unknown_action
  - test_m365_unknown_action_routing passes
- **Validation command:** `cd $UCP_ROOT && grep -n 'unknown_action\|mutation_fence' src/ucp/m365_tools.py || true`
- **Files to modify:**
  - UCP: src/ucp/m365_tools.py

### T5 — Add M365 unit tests for unknown_action

- **Ref:** `plan:m365-cps-trkA-p1-status-code-semantics:T5`
- **Description:** Add test_unknown_action_returns_unknown_action_status in tests/test_m365_pack_client.py. Update any existing tests that asserted mutation_fence on unknown actions.
- **Requirement refs:** R1
- **Depends on:** T4
- **MATHS phase:** N/A
- **Deliverables:**
  - tests/test_m365_pack_client.py with new test
  - Updated existing tests that assumed unknown -> mutation_fence
- **Exit criteria:**
  - pytest -k unknown_action -x exits 0
- **Validation command:** `cd $M365_ROOT && .venv/bin/python -m pytest tests/test_m365_pack_client.py -k unknown_action -x`
- **Files to modify:**
  - M365: tests/test_m365_pack_client.py

### T6 — Add UCP unit tests for unknown_action routing

- **Ref:** `plan:m365-cps-trkA-p1-status-code-semantics:T6`
- **Description:** Add test_m365_unknown_action_routing in tests/test_m365_integration.py.
- **Requirement refs:** R1
- **Depends on:** T5
- **MATHS phase:** N/A
- **Deliverables:**
  - tests/test_m365_integration.py with new test
- **Exit criteria:**
  - pytest -k m365_unknown -x exits 0
- **Validation command:** `cd $UCP_ROOT && .venv/bin/python -m pytest tests/test_m365_integration.py -k m365_unknown -x`
- **Files to modify:**
  - UCP: tests/test_m365_integration.py

### T7 — Pre-commit + make test in both repos

- **Ref:** `plan:m365-cps-trkA-p1-status-code-semantics:T7`
- **Description:** Run pre-commit run --all-files in both repos. Run make test in both repos. Fix any issues.
- **Requirement refs:** R1, R8
- **Depends on:** T6
- **MATHS phase:** N/A
- **Deliverables:**
  - pre-commit clean in both repos
  - make test green in both repos
- **Exit criteria:**
  - pre-commit exit 0 (both)
  - make test exit 0 (both)
- **Validation command:** `cd $M365_ROOT && pre-commit run --all-files && make test && cd $UCP_ROOT && pre-commit run --all-files && make test`

### T8 — Commit child phases (no push)

- **Ref:** `plan:m365-cps-trkA-p1-status-code-semantics:T8`
- **Description:** Create commits in both repos with message format 'plan:m365-cps-trkA-p1: T1-T7 status code semantics'. No push.
- **Requirement refs:** R8
- **Depends on:** T7
- **MATHS phase:** N/A
- **Deliverables:**
  - Commit in UCP feat/m365-cps-trkA branch
  - Commit in M365 feat/m365-cps-trkA branch
- **Exit criteria:**
  - git log --oneline -1 shows the commit message in both repos
- **Validation command:** `cd $UCP_ROOT && git log --oneline -1 | grep 'plan:m365-cps-trkA-p1' && cd $M365_ROOT && git log --oneline -1 | grep 'plan:m365-cps-trkA-p1'`

## Section 9: Gate Checks

### CHECK:C0 — Parent phase A1 integration

- **Description:** All child tasks T1..T8 green; integration test pass
- **Task ref:** T1..T8
- **Validation command:** `cd $UCP_ROOT && .venv/bin/python tests/integration/m365_unknown_action_e2e.py`
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
| Read confirmation logged in implementation_notes of this task | varies | T1 | per-task | see Section 8 / T1 |
| src/m365_runtime/graph/registry.py with_denial_to_status updated | varies | T2 | per-task | see Section 8 / T2 |
| Confirmation that no callsite remaps unknown_action | varies | T3 | per-task | see Section 8 / T3 |
| src/ucp/m365_tools.py with no unknown_action remap | varies | T4 | per-task | see Section 8 / T4 |
| tests/test_m365_pack_client.py with new test | varies | T5 | per-task | see Section 8 / T5 |
| Updated existing tests that assumed unknown -> mutation_fence | varies | T5 | per-task | see Section 8 / T5 |
| tests/test_m365_integration.py with new test | varies | T6 | per-task | see Section 8 / T6 |
| pre-commit clean in both repos | varies | T7 | per-task | see Section 8 / T7 |
| make test green in both repos | varies | T7 | per-task | see Section 8 / T7 |
| Commit in UCP feat/m365-cps-trkA branch | varies | T8 | per-task | see Section 8 / T8 |
| Commit in M365 feat/m365-cps-trkA branch | varies | T8 | per-task | see Section 8 / T8 |

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
  - `docs/prompts/codex-m365-cps-trkA-p1-status-code-semantics-T1.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkA-p1-status-code-semantics-T1-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkA-p1-status-code-semantics-T2.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkA-p1-status-code-semantics-T2-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkA-p1-status-code-semantics-T3.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkA-p1-status-code-semantics-T3-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkA-p1-status-code-semantics-T4.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkA-p1-status-code-semantics-T4-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkA-p1-status-code-semantics-T5.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkA-p1-status-code-semantics-T5-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkA-p1-status-code-semantics-T6.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkA-p1-status-code-semantics-T6-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkA-p1-status-code-semantics-T7.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkA-p1-status-code-semantics-T7-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkA-p1-status-code-semantics-T8.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkA-p1-status-code-semantics-T8-prompt.txt` (kickoff)

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

- [ ] T1 — Read context for status code semantics — Evidence:
- [ ] T2 — Update _denial_to_status to preserve unknown_action — Evidence:
- [ ] T3 — Align actions.py callsite — Evidence:
- [ ] T4 — Update UCP m365_tools.py to surface unknown_action — Evidence:
- [ ] T5 — Add M365 unit tests for unknown_action — Evidence:
- [ ] T6 — Add UCP unit tests for unknown_action routing — Evidence:
- [ ] T7 — Pre-commit + make test in both repos — Evidence:
- [ ] T8 — Commit child phases (no push) — Evidence:

### Gate checklist

- [ ] CHECK:C0 — Parent phase A1 integration — Result:

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
