# Track C — Truth-in-Advertising

## Section 1: Plan Header

- **Plan ID:** `plan:m365-cps-trkC-truth-in-advertising`
- **Parent Plan ID:** `plan:m365-capability-pack-surface-remediation`
- **Title:** Track C — Truth-in-Advertising
- **Version:** 1.0
- **Status:** approved
- **Owner:** Phil Siniscalchi (Founder/Owner)
- **Date Created:** 2026-05-01
- **Date Updated:** 2026-05-01
- **North Star Ref:** `docs/NORTH_STAR.md`
- **Execution Plan Ref:** docs/platform/EXECUTION_PLAN.md - M365 CPS Track C
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
  - Execute Track C per master plan.
- **Intent doc ref:** captured in this plan
- **Intent verification:** Tasks T1..T5 drive each parent-phase plan to completion.

## Section 4: Objective

- **Objective:** Track C — Truth-in-Advertising
- **Current state:** Track C parent-phase plans defined; status draft; no execution started.
- **Target state:** All Track C parent-phase plans status: complete; branch feat/m365-cps-trkC merged.

## Section 5: Scope

### In scope

- plan:m365-cps-trkC-p1-coverage-status-contract
- plan:m365-cps-trkC-p2-agents-yaml-schema
- plan:m365-cps-trkC-p3-mcp-tool-docstrings
- plan:m365-cps-trkC-p4-operator-capability-map
- plan:m365-cps-trkC-p5-end-to-end

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

### R6

- **Ref:** `plan:m365-cps-trkC-truth-in-advertising:R6`
- **Description:** Track C requirement carry-through from master plan R6.
- **Acceptance criteria:** All parent phases satisfying master R6 are complete.
- **Depends on:** none
- **User intent trace:** Master R6

### R7

- **Ref:** `plan:m365-cps-trkC-truth-in-advertising:R7`
- **Description:** Track C requirement carry-through from master plan R7.
- **Acceptance criteria:** All parent phases satisfying master R7 are complete.
- **Depends on:** none
- **User intent trace:** Master R7

### R8

- **Ref:** `plan:m365-cps-trkC-truth-in-advertising:R8`
- **Description:** Track C requirement carry-through from master plan R8.
- **Acceptance criteria:** All parent phases satisfying master R8 are complete.
- **Depends on:** none
- **User intent trace:** Master R8

## Section 7: Execution Sequence

- **Ordering:** ['T1', 'T2', 'T3', 'T4', 'T5']
- **Stop on first failure:** true
- **Strict ordering rule:** Do not start task N+1 until task N exit criteria are met.
- **MATHS phase mapping:** N/A (non-math scope)

## Section 8: Task Breakdown

### T1 — Coverage-Status Contract

- **Ref:** `plan:m365-cps-trkC-truth-in-advertising:T1`
- **Description:** Define coverage_status enum + schema; add not_yet_implemented to runtime status code enum.
- **Requirement refs:** R6, R7, R8
- **Depends on:** none
- **MATHS phase:** N/A
- **Deliverables:**
  - plan:m365-cps-trkC-p1-coverage-status-contract status: complete
- **Exit criteria:**
  - plan:m365-cps-trkC-p1-coverage-status-contract GATE green; commit + push to feat/m365-cps-trkC
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkC-p1-coverage-status-contract`
- **Implementation notes:** Sub-plan: plan:m365-cps-trkC-p1-coverage-status-contract

### T2 — agents.yaml Schema Upgrade

- **Ref:** `plan:m365-cps-trkC-truth-in-advertising:T2`
- **Description:** Add coverage_status to agents.yaml entries; migrate existing data; update validate_agent_action and execute_m365_action.
- **Requirement refs:** R6, R7, R8
- **Depends on:** T1
- **MATHS phase:** N/A
- **Deliverables:**
  - plan:m365-cps-trkC-p2-agents-yaml-schema status: complete
- **Exit criteria:**
  - plan:m365-cps-trkC-p2-agents-yaml-schema GATE green; commit + push to feat/m365-cps-trkC
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkC-p2-agents-yaml-schema`
- **Implementation notes:** Sub-plan: plan:m365-cps-trkC-p2-agents-yaml-schema

### T3 — MCP Tool Docstring Alignment

- **Ref:** `plan:m365-cps-trkC-truth-in-advertising:T3`
- **Description:** Audit + update MCP tool docstrings to mark every action with its coverage_status. Add linter.
- **Requirement refs:** R6, R7, R8
- **Depends on:** T2
- **MATHS phase:** N/A
- **Deliverables:**
  - plan:m365-cps-trkC-p3-mcp-tool-docstrings status: complete
- **Exit criteria:**
  - plan:m365-cps-trkC-p3-mcp-tool-docstrings GATE green; commit + push to feat/m365-cps-trkC
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkC-p3-mcp-tool-docstrings`
- **Implementation notes:** Sub-plan: plan:m365-cps-trkC-p3-mcp-tool-docstrings

### T4 — Operator Capability Map

- **Ref:** `plan:m365-cps-trkC-truth-in-advertising:T4`
- **Description:** Auto-generate operator-facing capability map doc from registry + agents.yaml. Mirror to UCP docs.
- **Requirement refs:** R6, R7, R8
- **Depends on:** T3
- **MATHS phase:** N/A
- **Deliverables:**
  - plan:m365-cps-trkC-p4-operator-capability-map status: complete
- **Exit criteria:**
  - plan:m365-cps-trkC-p4-operator-capability-map GATE green; commit + push to feat/m365-cps-trkC
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkC-p4-operator-capability-map`
- **Implementation notes:** Sub-plan: plan:m365-cps-trkC-p4-operator-capability-map

### T5 — Track C End-to-End

- **Ref:** `plan:m365-cps-trkC-truth-in-advertising:T5`
- **Description:** Live e2e of planned vs implemented action behavior; docstring linter green; governance closure.
- **Requirement refs:** R6, R7, R8
- **Depends on:** T4
- **MATHS phase:** N/A
- **Deliverables:**
  - plan:m365-cps-trkC-p5-end-to-end status: complete
- **Exit criteria:**
  - plan:m365-cps-trkC-p5-end-to-end GATE green; commit + push to feat/m365-cps-trkC
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkC-p5-end-to-end`
- **Implementation notes:** Sub-plan: plan:m365-cps-trkC-p5-end-to-end

## Section 9: Gate Checks

### CHECK:C1 — Parent Phase C1 — Coverage-Status Contract complete

- **Description:** plan:m365-cps-trkC-p1-coverage-status-contract status == complete with GATE evidence
- **Task ref:** T1
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkC-p1-coverage-status-contract`
- **Pass criteria:** Plan status complete; GATE validation_command exit 0
- **Fail action:** block

### CHECK:C2 — Parent Phase C2 — agents.yaml Schema Upgrade complete

- **Description:** plan:m365-cps-trkC-p2-agents-yaml-schema status == complete with GATE evidence
- **Task ref:** T2
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkC-p2-agents-yaml-schema`
- **Pass criteria:** Plan status complete; GATE validation_command exit 0
- **Fail action:** block

### CHECK:C3 — Parent Phase C3 — MCP Tool Docstring Alignment complete

- **Description:** plan:m365-cps-trkC-p3-mcp-tool-docstrings status == complete with GATE evidence
- **Task ref:** T3
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkC-p3-mcp-tool-docstrings`
- **Pass criteria:** Plan status complete; GATE validation_command exit 0
- **Fail action:** block

### CHECK:C4 — Parent Phase C4 — Operator Capability Map complete

- **Description:** plan:m365-cps-trkC-p4-operator-capability-map status == complete with GATE evidence
- **Task ref:** T4
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkC-p4-operator-capability-map`
- **Pass criteria:** Plan status complete; GATE validation_command exit 0
- **Fail action:** block

### CHECK:C5 — Parent Phase C5 — Track C End-to-End complete

- **Description:** plan:m365-cps-trkC-p5-end-to-end status == complete with GATE evidence
- **Task ref:** T5
- **Validation command:** `.venv/bin/python scripts/check_plan_complete.py plan:m365-cps-trkC-p5-end-to-end`
- **Pass criteria:** Plan status complete; GATE validation_command exit 0
- **Fail action:** block

### Decision rule

- **GO:** All gates pass.
- **NO-GO:** Any gate fails.

### No-go triggers

- Any parent-phase plan in Track C fails its GATE
- Branch feat/m365-cps-trkC merge conflict that cannot be resolved without scope drift

## Section 10: Determinism Requirements

N/A — non-math scope. Tests must be hermetic; live tenant only in GATE smoke tests.

## Section 11: Artifacts

| Path | Format | Producer | Schema ref | Validation |
|------|--------|----------|------------|------------|
| plan:m365-cps-trkC-p1-coverage-status-contract status: complete | varies | T1 | per-task | see Section 8 / T1 |
| plan:m365-cps-trkC-p2-agents-yaml-schema status: complete | varies | T2 | per-task | see Section 8 / T2 |
| plan:m365-cps-trkC-p3-mcp-tool-docstrings status: complete | varies | T3 | per-task | see Section 8 / T3 |
| plan:m365-cps-trkC-p4-operator-capability-map status: complete | varies | T4 | per-task | see Section 8 / T4 |
| plan:m365-cps-trkC-p5-end-to-end status: complete | varies | T5 | per-task | see Section 8 / T5 |

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
| Track C parent phase scope creep | medium | Per-parent allowlist; scope fence | mitigated |

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

- [ ] T1 — Coverage-Status Contract — Evidence:
- [ ] T2 — agents.yaml Schema Upgrade — Evidence:
- [ ] T3 — MCP Tool Docstring Alignment — Evidence:
- [ ] T4 — Operator Capability Map — Evidence:
- [ ] T5 — Track C End-to-End — Evidence:

### Gate checklist

- [ ] CHECK:C1 — Parent Phase C1 — Coverage-Status Contract complete — Result:
- [ ] CHECK:C2 — Parent Phase C2 — agents.yaml Schema Upgrade complete — Result:
- [ ] CHECK:C3 — Parent Phase C3 — MCP Tool Docstring Alignment complete — Result:
- [ ] CHECK:C4 — Parent Phase C4 — Operator Capability Map complete — Result:
- [ ] CHECK:C5 — Parent Phase C5 — Track C End-to-End complete — Result:

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
