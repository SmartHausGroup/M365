# Parent Phase B7 — Track B End-to-End & Repackage

## Section 1: Plan Header

- **Plan ID:** `plan:m365-cps-trkB-p7-end-to-end-and-repackage`
- **Parent Plan ID:** `plan:m365-cps-trkB-coverage`
- **Title:** Parent Phase B7 — Track B End-to-End & Repackage
- **Version:** 1.0
- **Status:** draft
- **Owner:** Phil Siniscalchi (Founder/Owner)
- **Date Created:** 2026-05-01
- **Date Updated:** 2026-05-01
- **North Star Ref:** `docs/NORTH_STAR.md`
- **Execution Plan Ref:** docs/platform/EXECUTION_PLAN.md - M365 CPS Track B P7
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
  - Full live-tenant coverage e2e; cut M365 1.2.0 release; bind UCP to it; governance closure.
- **Intent doc ref:** captured in this plan
- **Intent verification:** Tasks T1..T6 together satisfy this parent phase's objective.

## Section 4: Objective

- **Objective:** Full live-tenant coverage e2e; cut M365 1.2.0 release; bind UCP to it; governance closure.
- **Current state:** Parent phase scope draft; no implementation yet.
- **Target state:** All child tasks complete; GATE green; commit + push to feat/m365-cps-trkB.

## Section 5: Scope

### In scope

- Full coverage e2e against live tenant
- Re-bump M365 version
- Re-package marketplace artifact
- Update UCP release_artifacts.py spec
- Re-verify SHA256 + provenance
- Update CHANGELOG / EXECUTION_PLAN / ACTION_LOG

### Out of scope

- Anything outside this parent's allowlist

### File allowlist

- `M365: src/m365_runtime/__init__.py`
- `M365: pyproject.toml`
- `M365: CHANGELOG.md`
- `M365: Operations/EXECUTION_PLAN.md`
- `M365: Operations/ACTION_LOG.md`
- `UCP: src/ucp/runtime/release_artifacts.py`
- `UCP: docs/platform/EXECUTION_PLAN.md`
- `UCP: docs/platform/CODDEX_ACTION_LOG.md`
- `UCP: tests/integration/m365_cps_trkB_full_coverage.py`
- `IntegrationPacks/M365/1.2.0/**`

### File denylist

- `Source files (those are p1-p6)`
- `Any file not in allowlist of the active child-phase task`

### Scope fence rule

Agent must STOP and re-scope if any file outside the allowlist is needed. Emit BLOCKED.

## Section 6: Requirements

### R4

- **Ref:** `plan:m365-cps-trkB-p7-end-to-end-and-repackage:R4`
- **Description:** Carry-through of master R4; this parent phase contributes scoped behavior.
- **Acceptance criteria:** Per-task exit criteria; parent GATE passes.
- **Depends on:** none
- **User intent trace:** Master R4

### R5

- **Ref:** `plan:m365-cps-trkB-p7-end-to-end-and-repackage:R5`
- **Description:** Carry-through of master R5; this parent phase contributes scoped behavior.
- **Acceptance criteria:** Per-task exit criteria; parent GATE passes.
- **Depends on:** none
- **User intent trace:** Master R5

### R8

- **Ref:** `plan:m365-cps-trkB-p7-end-to-end-and-repackage:R8`
- **Description:** Carry-through of master R8; this parent phase contributes scoped behavior.
- **Acceptance criteria:** Per-task exit criteria; parent GATE passes.
- **Depends on:** none
- **User intent trace:** Master R8

## Section 7: Execution Sequence

- **Ordering:** ['T1', 'T2', 'T3', 'T4', 'T5', 'T6']
- **Stop on first failure:** true
- **Strict ordering rule:** Do not start task N+1 until task N exit criteria are met.
- **MATHS phase mapping:** N/A (non-math scope)

## Section 8: Task Breakdown

### T1 — Full coverage e2e against live tenant

- **Ref:** `plan:m365-cps-trkB-p7-end-to-end-and-repackage:T1`
- **Description:** Run all Track B parent phase smoke tests in sequence against live tenant; produce consolidated diagnostic.
- **Requirement refs:** R4, R5
- **Depends on:** none
- **MATHS phase:** N/A
- **Deliverables:**
  - artifacts/diagnostics/m365_cps_trkB_full_coverage.json
- **Exit criteria:**
  - All actions return expected status from Graph
- **Validation command:** `cd $UCP_ROOT && .venv/bin/python tests/integration/m365_cps_trkB_full_coverage.py`

### T2 — Re-bump M365 version

- **Ref:** `plan:m365-cps-trkB-p7-end-to-end-and-repackage:T2`
- **Description:** Update src/m365_runtime/**init**.py version constant to 1.2.0; update pyproject.toml.
- **Requirement refs:** R4
- **Depends on:** T1
- **MATHS phase:** N/A
- **Deliverables:**
  - Version bumped
- **Exit criteria:**
  - pip show smarthaus_m365 | grep 1.2.0
- **Validation command:** `cd $M365_ROOT && grep -n '1.2.0' src/m365_runtime/__init__.py pyproject.toml`
- **Files to modify:**
  - M365: src/m365_runtime/**init**.py
  - M365: pyproject.toml

### T3 — Re-package marketplace artifact

- **Ref:** `plan:m365-cps-trkB-p7-end-to-end-and-repackage:T3`
- **Description:** Run make pack to produce com.smarthaus.m365-1.2.0.ucp.tar.gz and IntegrationPacks/M365/1.2.0/ contents.
- **Requirement refs:** R4
- **Depends on:** T2
- **MATHS phase:** N/A
- **Deliverables:**
  - IntegrationPacks/M365/1.2.0/com.smarthaus.m365-1.2.0.ucp.tar.gz
- **Exit criteria:**
  - Tarball exists; SHA256SUMS valid
- **Validation command:** `ls $INTEGRATION_PACKS_ROOT/M365/1.2.0/com.smarthaus.m365-1.2.0.ucp.tar.gz`
- **Files to modify:**
  - IntegrationPacks/M365/1.2.0/** (generated)

### T4 — Update UCP release_artifacts.py spec

- **Ref:** `plan:m365-cps-trkB-p7-end-to-end-and-repackage:T4`
- **Description:** Add M365_120_RELEASE_SPEC; update M365_RELEASE_SPEC alias to point at 1.2.0.
- **Requirement refs:** R4
- **Depends on:** T3
- **MATHS phase:** N/A
- **Deliverables:**
  - src/ucp/runtime/release_artifacts.py with M365_120_RELEASE_SPEC
- **Exit criteria:**
  - Import succeeds; spec.version == 1.2.0
- **Validation command:** `cd $UCP_ROOT && .venv/bin/python -c "from ucp.runtime.release_artifacts import M365_RELEASE_SPEC; assert M365_RELEASE_SPEC.version == '1.2.0'"`
- **Files to modify:**
  - UCP: src/ucp/runtime/release_artifacts.py

### T5 — Re-verify SHA256 + provenance

- **Ref:** `plan:m365-cps-trkB-p7-end-to-end-and-repackage:T5`
- **Description:** Update expected_bundle_sha256 in M365_120_RELEASE_SPEC; run release artifact acceptance test.
- **Requirement refs:** R4
- **Depends on:** T4
- **MATHS phase:** N/A
- **Deliverables:**
  - SHA pinned
- **Exit criteria:**
  - scripts/verify_release_artifact.py exits 0
- **Validation command:** `cd $UCP_ROOT && .venv/bin/python scripts/verify_release_artifact.py M365_120_RELEASE_SPEC`

### T6 — Update CHANGELOG / EXECUTION_PLAN / ACTION_LOG

- **Ref:** `plan:m365-cps-trkB-p7-end-to-end-and-repackage:T6`
- **Description:** Document Track B completion + 1.2.0 release in CHANGELOG (M365), EXECUTION_PLAN (both), ACTION_LOG (both).
- **Requirement refs:** R8
- **Depends on:** T5
- **MATHS phase:** N/A
- **Deliverables:**
  - Governance docs updated
- **Exit criteria:**
  - git diff shows updates
- **Validation command:** `cd $UCP_ROOT && git diff --stat docs/platform/EXECUTION_PLAN.md docs/platform/CODDEX_ACTION_LOG.md`
- **Files to modify:**
  - UCP: docs/platform/EXECUTION_PLAN.md
  - UCP: docs/platform/CODDEX_ACTION_LOG.md
  - M365: Operations/EXECUTION_PLAN.md
  - M365: Operations/ACTION_LOG.md
  - M365: CHANGELOG.md

## Section 9: Gate Checks

### CHECK:C0 — Parent phase B7 integration

- **Description:** All child tasks T1..T6 green; integration test pass
- **Task ref:** T1..T6
- **Validation command:** `cd $UCP_ROOT && .venv/bin/python tests/integration/m365_cps_trkB_full_coverage.py`
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
| artifacts/diagnostics/m365_cps_trkB_full_coverage.json | JSON | T1 | per-task | see Section 8 / T1 |
| Version bumped | varies | T2 | per-task | see Section 8 / T2 |
| IntegrationPacks/M365/1.2.0/com.smarthaus.m365-1.2.0.ucp.tar.gz | varies | T3 | per-task | see Section 8 / T3 |
| src/ucp/runtime/release_artifacts.py with M365_120_RELEASE_SPEC | varies | T4 | per-task | see Section 8 / T4 |
| SHA pinned | varies | T5 | per-task | see Section 8 / T5 |
| Governance docs updated | varies | T6 | per-task | see Section 8 / T6 |

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
  - `docs/prompts/codex-m365-cps-trkB-p7-end-to-end-and-repackage-T1.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p7-end-to-end-and-repackage-T1-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p7-end-to-end-and-repackage-T2.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p7-end-to-end-and-repackage-T2-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p7-end-to-end-and-repackage-T3.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p7-end-to-end-and-repackage-T3-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p7-end-to-end-and-repackage-T4.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p7-end-to-end-and-repackage-T4-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p7-end-to-end-and-repackage-T5.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p7-end-to-end-and-repackage-T5-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p7-end-to-end-and-repackage-T6.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p7-end-to-end-and-repackage-T6-prompt.txt` (kickoff)

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

- [ ] T1 — Full coverage e2e against live tenant — Evidence:
- [ ] T2 — Re-bump M365 version — Evidence:
- [ ] T3 — Re-package marketplace artifact — Evidence:
- [ ] T4 — Update UCP release_artifacts.py spec — Evidence:
- [ ] T5 — Re-verify SHA256 + provenance — Evidence:
- [ ] T6 — Update CHANGELOG / EXECUTION_PLAN / ACTION_LOG — Evidence:

### Gate checklist

- [ ] CHECK:C0 — Parent phase B7 integration — Result:

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
