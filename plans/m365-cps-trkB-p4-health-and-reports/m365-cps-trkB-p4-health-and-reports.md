# Parent Phase B4 — Service Health & Reports

## Section 1: Plan Header

- **Plan ID:** `plan:m365-cps-trkB-p4-health-and-reports`
- **Parent Plan ID:** `plan:m365-cps-trkB-coverage`
- **Title:** Parent Phase B4 — Service Health & Reports
- **Version:** 1.0
- **Status:** draft
- **Owner:** Phil Siniscalchi (Founder/Owner)
- **Date Created:** 2026-05-01
- **Date Updated:** 2026-05-01
- **North Star Ref:** `docs/NORTH_STAR.md`
- **Execution Plan Ref:** docs/platform/EXECUTION_PLAN.md - M365 CPS Track B P4
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
  - Add health.overview, health.issues, health.messages, reports.users_active, reports.email_activity, reports.teams_activity, reports.sharepoint_usage, reports.onedrive_usage.
- **Intent doc ref:** captured in this plan
- **Intent verification:** Tasks T1..T15 together satisfy this parent phase's objective.

## Section 4: Objective

- **Objective:** Add health.overview, health.issues, health.messages, reports.users_active, reports.email_activity, reports.teams_activity, reports.sharepoint_usage, reports.onedrive_usage.
- **Current state:** Parent phase scope draft; no implementation yet.
- **Target state:** All child tasks complete; GATE green; commit + push to feat/m365-cps-trkB.

## Section 5: Scope

### In scope

- Read context for parent phase
- Add graph.health.overview registry entry
- Add graph.health.issues registry entry
- Add graph.health.messages registry entry
- Add graph.reports.users_active registry entry
- Add graph.reports.email_activity registry entry
- Add graph.reports.teams_activity registry entry
- Add graph.reports.sharepoint_usage registry entry
- Add graph.reports.onedrive_usage registry entry
- Update legacy alias table
- Update YAML registry mirror
- M365 unit tests
- UCP routing unit tests
- Pre-commit + make test
- Commit (no push)

### Out of scope

- Anything outside this parent's allowlist

### File allowlist

- `M365: src/m365_runtime/graph/registry.py`
- `M365: src/ucp_m365_pack/client.py`
- `M365: registry/action_registry.yaml`
- `M365: tests/test_m365_pack_client.py`
- `UCP: tests/test_m365_integration.py`

### File denylist

- `Files outside health+reports coverage scope`
- `Any file not in allowlist of the active child-phase task`

### Scope fence rule

Agent must STOP and re-scope if any file outside the allowlist is needed. Emit BLOCKED.

## Section 6: Requirements

### R4

- **Ref:** `plan:m365-cps-trkB-p4-health-and-reports:R4`
- **Description:** Carry-through of master R4; this parent phase contributes scoped behavior.
- **Acceptance criteria:** Per-task exit criteria; parent GATE passes.
- **Depends on:** none
- **User intent trace:** Master R4

### R8

- **Ref:** `plan:m365-cps-trkB-p4-health-and-reports:R8`
- **Description:** Carry-through of master R8; this parent phase contributes scoped behavior.
- **Acceptance criteria:** Per-task exit criteria; parent GATE passes.
- **Depends on:** none
- **User intent trace:** Master R8

## Section 7: Execution Sequence

- **Ordering:** ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12', 'T13', 'T14', 'T15']
- **Stop on first failure:** true
- **Strict ordering rule:** Do not start task N+1 until task N exit criteria are met.
- **MATHS phase mapping:** N/A (non-math scope)

## Section 8: Task Breakdown

### T1 — Read context for parent phase

- **Ref:** `plan:m365-cps-trkB-p4-health-and-reports:T1`
- **Description:** Read existing m365_runtime/graph/registry.py, ucp_m365_pack/client.py alias table, registry/action_registry.yaml. Document existing patterns to match.
- **Requirement refs:** R4
- **Depends on:** none
- **MATHS phase:** N/A
- **Deliverables:**
  - Read confirmation
- **Exit criteria:**
  - All three files read
- **Validation command:** `test -f $M365_ROOT/src/m365_runtime/graph/registry.py`
- **Files to read:**
  - M365: src/m365_runtime/graph/registry.py
  - M365: src/ucp_m365_pack/client.py
  - M365: registry/action_registry.yaml

### T2 — Add graph.health.overview registry entry

- **Ref:** `plan:m365-cps-trkB-p4-health-and-reports:T2`
- **Description:** Add ActionSpec for graph.health.overview (workload admin; auth_modes ['app_only_secret', 'app_only_certificate']; scopes ['ServiceHealth.Read.All']; risk low; rw read) to READ_ONLY_REGISTRY in src/m365_runtime/graph/registry.py. Endpoint per parent plan B-action spec table.
- **Requirement refs:** R4
- **Depends on:** T1
- **MATHS phase:** N/A
- **Deliverables:**
  - src/m365_runtime/graph/registry.py with graph.health.overview ActionSpec
- **Exit criteria:**
  - get_action('graph.health.overview') returns the spec; admit() works
- **Validation command:** `cd $M365_ROOT && .venv/bin/python -c "from m365_runtime.graph.registry import get_action; spec = get_action('graph.health.overview'); assert spec.workload == 'admin'; print('OK')"`
- **Files to modify:**
  - M365: src/m365_runtime/graph/registry.py

### T3 — Add graph.health.issues registry entry

- **Ref:** `plan:m365-cps-trkB-p4-health-and-reports:T3`
- **Description:** Add ActionSpec for graph.health.issues (workload admin; auth_modes ['app_only_secret', 'app_only_certificate']; scopes ['ServiceHealth.Read.All']; risk low; rw read) to READ_ONLY_REGISTRY in src/m365_runtime/graph/registry.py. Endpoint per parent plan B-action spec table.
- **Requirement refs:** R4
- **Depends on:** T2
- **MATHS phase:** N/A
- **Deliverables:**
  - src/m365_runtime/graph/registry.py with graph.health.issues ActionSpec
- **Exit criteria:**
  - get_action('graph.health.issues') returns the spec; admit() works
- **Validation command:** `cd $M365_ROOT && .venv/bin/python -c "from m365_runtime.graph.registry import get_action; spec = get_action('graph.health.issues'); assert spec.workload == 'admin'; print('OK')"`
- **Files to modify:**
  - M365: src/m365_runtime/graph/registry.py

### T4 — Add graph.health.messages registry entry

- **Ref:** `plan:m365-cps-trkB-p4-health-and-reports:T4`
- **Description:** Add ActionSpec for graph.health.messages (workload admin; auth_modes ['app_only_secret', 'app_only_certificate']; scopes ['ServiceMessage.Read.All']; risk low; rw read) to READ_ONLY_REGISTRY in src/m365_runtime/graph/registry.py. Endpoint per parent plan B-action spec table.
- **Requirement refs:** R4
- **Depends on:** T3
- **MATHS phase:** N/A
- **Deliverables:**
  - src/m365_runtime/graph/registry.py with graph.health.messages ActionSpec
- **Exit criteria:**
  - get_action('graph.health.messages') returns the spec; admit() works
- **Validation command:** `cd $M365_ROOT && .venv/bin/python -c "from m365_runtime.graph.registry import get_action; spec = get_action('graph.health.messages'); assert spec.workload == 'admin'; print('OK')"`
- **Files to modify:**
  - M365: src/m365_runtime/graph/registry.py

### T5 — Add graph.reports.users_active registry entry

- **Ref:** `plan:m365-cps-trkB-p4-health-and-reports:T5`
- **Description:** Add ActionSpec for graph.reports.users_active (workload reports; auth_modes ['app_only_secret', 'app_only_certificate']; scopes ['Reports.Read.All']; risk low; rw read) to READ_ONLY_REGISTRY in src/m365_runtime/graph/registry.py. Endpoint per parent plan B-action spec table.
- **Requirement refs:** R4
- **Depends on:** T4
- **MATHS phase:** N/A
- **Deliverables:**
  - src/m365_runtime/graph/registry.py with graph.reports.users_active ActionSpec
- **Exit criteria:**
  - get_action('graph.reports.users_active') returns the spec; admit() works
- **Validation command:** `cd $M365_ROOT && .venv/bin/python -c "from m365_runtime.graph.registry import get_action; spec = get_action('graph.reports.users_active'); assert spec.workload == 'reports'; print('OK')"`
- **Files to modify:**
  - M365: src/m365_runtime/graph/registry.py

### T6 — Add graph.reports.email_activity registry entry

- **Ref:** `plan:m365-cps-trkB-p4-health-and-reports:T6`
- **Description:** Add ActionSpec for graph.reports.email_activity (workload reports; auth_modes ['app_only_secret', 'app_only_certificate']; scopes ['Reports.Read.All']; risk low; rw read) to READ_ONLY_REGISTRY in src/m365_runtime/graph/registry.py. Endpoint per parent plan B-action spec table.
- **Requirement refs:** R4
- **Depends on:** T5
- **MATHS phase:** N/A
- **Deliverables:**
  - src/m365_runtime/graph/registry.py with graph.reports.email_activity ActionSpec
- **Exit criteria:**
  - get_action('graph.reports.email_activity') returns the spec; admit() works
- **Validation command:** `cd $M365_ROOT && .venv/bin/python -c "from m365_runtime.graph.registry import get_action; spec = get_action('graph.reports.email_activity'); assert spec.workload == 'reports'; print('OK')"`
- **Files to modify:**
  - M365: src/m365_runtime/graph/registry.py

### T7 — Add graph.reports.teams_activity registry entry

- **Ref:** `plan:m365-cps-trkB-p4-health-and-reports:T7`
- **Description:** Add ActionSpec for graph.reports.teams_activity (workload reports; auth_modes ['app_only_secret', 'app_only_certificate']; scopes ['Reports.Read.All']; risk low; rw read) to READ_ONLY_REGISTRY in src/m365_runtime/graph/registry.py. Endpoint per parent plan B-action spec table.
- **Requirement refs:** R4
- **Depends on:** T6
- **MATHS phase:** N/A
- **Deliverables:**
  - src/m365_runtime/graph/registry.py with graph.reports.teams_activity ActionSpec
- **Exit criteria:**
  - get_action('graph.reports.teams_activity') returns the spec; admit() works
- **Validation command:** `cd $M365_ROOT && .venv/bin/python -c "from m365_runtime.graph.registry import get_action; spec = get_action('graph.reports.teams_activity'); assert spec.workload == 'reports'; print('OK')"`
- **Files to modify:**
  - M365: src/m365_runtime/graph/registry.py

### T8 — Add graph.reports.sharepoint_usage registry entry

- **Ref:** `plan:m365-cps-trkB-p4-health-and-reports:T8`
- **Description:** Add ActionSpec for graph.reports.sharepoint_usage (workload reports; auth_modes ['app_only_secret', 'app_only_certificate']; scopes ['Reports.Read.All']; risk low; rw read) to READ_ONLY_REGISTRY in src/m365_runtime/graph/registry.py. Endpoint per parent plan B-action spec table.
- **Requirement refs:** R4
- **Depends on:** T7
- **MATHS phase:** N/A
- **Deliverables:**
  - src/m365_runtime/graph/registry.py with graph.reports.sharepoint_usage ActionSpec
- **Exit criteria:**
  - get_action('graph.reports.sharepoint_usage') returns the spec; admit() works
- **Validation command:** `cd $M365_ROOT && .venv/bin/python -c "from m365_runtime.graph.registry import get_action; spec = get_action('graph.reports.sharepoint_usage'); assert spec.workload == 'reports'; print('OK')"`
- **Files to modify:**
  - M365: src/m365_runtime/graph/registry.py

### T9 — Add graph.reports.onedrive_usage registry entry

- **Ref:** `plan:m365-cps-trkB-p4-health-and-reports:T9`
- **Description:** Add ActionSpec for graph.reports.onedrive_usage (workload reports; auth_modes ['app_only_secret', 'app_only_certificate']; scopes ['Reports.Read.All']; risk low; rw read) to READ_ONLY_REGISTRY in src/m365_runtime/graph/registry.py. Endpoint per parent plan B-action spec table.
- **Requirement refs:** R4
- **Depends on:** T8
- **MATHS phase:** N/A
- **Deliverables:**
  - src/m365_runtime/graph/registry.py with graph.reports.onedrive_usage ActionSpec
- **Exit criteria:**
  - get_action('graph.reports.onedrive_usage') returns the spec; admit() works
- **Validation command:** `cd $M365_ROOT && .venv/bin/python -c "from m365_runtime.graph.registry import get_action; spec = get_action('graph.reports.onedrive_usage'); assert spec.workload == 'reports'; print('OK')"`
- **Files to modify:**
  - M365: src/m365_runtime/graph/registry.py

### T10 — Update legacy alias table

- **Ref:** `plan:m365-cps-trkB-p4-health-and-reports:T10`
- **Description:** Update LEGACY_ACTION_TO_RUNTIME_ACTION in ucp_m365_pack/client.py with legacy_name -> graph.X.Y mappings for the new actions.
- **Requirement refs:** R4
- **Depends on:** T9
- **MATHS phase:** N/A
- **Deliverables:**
  - src/ucp_m365_pack/client.py with new alias entries
- **Exit criteria:**
  - map_legacy_action_to_runtime() returns expected runtime action_id for each legacy name
- **Validation command:** `cd $M365_ROOT && .venv/bin/python -c "from ucp_m365_pack.client import map_legacy_action_to_runtime, LEGACY_ACTION_TO_RUNTIME_ACTION; assert len(LEGACY_ACTION_TO_RUNTIME_ACTION) > 22"`
- **Files to modify:**
  - M365: src/ucp_m365_pack/client.py

### T11 — Update YAML registry mirror

- **Ref:** `plan:m365-cps-trkB-p4-health-and-reports:T11`
- **Description:** Update registry/action_registry.yaml with corresponding stanzas for the new graph.* actions.
- **Requirement refs:** R4
- **Depends on:** T10
- **MATHS phase:** N/A
- **Deliverables:**
  - registry/action_registry.yaml with new entries
- **Exit criteria:**
  - yaml.safe_load passes; new keys present
- **Validation command:** `cd $M365_ROOT && .venv/bin/python -c "import yaml; data=yaml.safe_load(open('registry/action_registry.yaml')); assert len(data['actions']) > 11"`
- **Files to modify:**
  - M365: registry/action_registry.yaml

### T12 — M365 unit tests

- **Ref:** `plan:m365-cps-trkB-p4-health-and-reports:T12`
- **Description:** Add per-action unit tests in tests/test_m365_pack_client.py covering: registry lookup, admit() success, admit() denial when missing scope.
- **Requirement refs:** R4
- **Depends on:** T11
- **MATHS phase:** N/A
- **Deliverables:**
  - Updated test file
- **Exit criteria:**
  - pytest exits 0
- **Validation command:** `cd $M365_ROOT && .venv/bin/python -m pytest tests/test_m365_pack_client.py -k 'p4' -x`
- **Files to modify:**
  - M365: tests/test_m365_pack_client.py

### T13 — UCP routing unit tests

- **Ref:** `plan:m365-cps-trkB-p4-health-and-reports:T13`
- **Description:** Add UCP-side test_m365_integration entries that exercise execute_m365_action with the new actions through the alias table.
- **Requirement refs:** R4
- **Depends on:** T12
- **MATHS phase:** N/A
- **Deliverables:**
  - Updated UCP test file
- **Exit criteria:**
  - pytest exits 0
- **Validation command:** `cd $UCP_ROOT && .venv/bin/python -m pytest tests/test_m365_integration.py -k 'p4' -x`
- **Files to modify:**
  - UCP: tests/test_m365_integration.py

### T14 — Pre-commit + make test

- **Ref:** `plan:m365-cps-trkB-p4-health-and-reports:T14`
- **Description:** Standard validation gate.
- **Requirement refs:** R8
- **Depends on:** T13
- **MATHS phase:** N/A
- **Deliverables:**
  - pre-commit + make test green in both repos
- **Exit criteria:**
  - exit 0
- **Validation command:** `cd $M365_ROOT && pre-commit run --all-files && make test && cd $UCP_ROOT && pre-commit run --all-files && make test`

### T15 — Commit (no push)

- **Ref:** `plan:m365-cps-trkB-p4-health-and-reports:T15`
- **Description:** Commit format 'plan:m365-cps-trkB-p4: T1-T14 <parent name>'.
- **Requirement refs:** R8
- **Depends on:** T14
- **MATHS phase:** N/A
- **Deliverables:**
  - Commit in both repos
- **Exit criteria:**
  - git log shows commit
- **Validation command:** `cd $UCP_ROOT && git log --oneline -1 | grep 'plan:m365-cps-trkB-p4' && cd $M365_ROOT && git log --oneline -1 | grep 'plan:m365-cps-trkB-p4'`

## Section 9: Gate Checks

### CHECK:C0 — Parent phase B4 integration

- **Description:** All child tasks T1..T15 green; integration test pass
- **Task ref:** T1..T15
- **Validation command:** `cd $UCP_ROOT && .venv/bin/python tests/integration/m365_health_reports_e2e.py`
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
| Read confirmation | varies | T1 | per-task | see Section 8 / T1 |
| src/m365_runtime/graph/registry.py with graph.health.overview ActionSpec | varies | T2 | per-task | see Section 8 / T2 |
| src/m365_runtime/graph/registry.py with graph.health.issues ActionSpec | varies | T3 | per-task | see Section 8 / T3 |
| src/m365_runtime/graph/registry.py with graph.health.messages ActionSpec | varies | T4 | per-task | see Section 8 / T4 |
| src/m365_runtime/graph/registry.py with graph.reports.users_active ActionSpec | varies | T5 | per-task | see Section 8 / T5 |
| src/m365_runtime/graph/registry.py with graph.reports.email_activity ActionSpec | varies | T6 | per-task | see Section 8 / T6 |
| src/m365_runtime/graph/registry.py with graph.reports.teams_activity ActionSpec | varies | T7 | per-task | see Section 8 / T7 |
| src/m365_runtime/graph/registry.py with graph.reports.sharepoint_usage ActionSpec | varies | T8 | per-task | see Section 8 / T8 |
| src/m365_runtime/graph/registry.py with graph.reports.onedrive_usage ActionSpec | varies | T9 | per-task | see Section 8 / T9 |
| src/ucp_m365_pack/client.py with new alias entries | varies | T10 | per-task | see Section 8 / T10 |
| registry/action_registry.yaml with new entries | varies | T11 | per-task | see Section 8 / T11 |
| Updated test file | varies | T12 | per-task | see Section 8 / T12 |
| Updated UCP test file | varies | T13 | per-task | see Section 8 / T13 |
| pre-commit + make test green in both repos | varies | T14 | per-task | see Section 8 / T14 |
| Commit in both repos | varies | T15 | per-task | see Section 8 / T15 |

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
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T1.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T1-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T2.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T2-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T3.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T3-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T4.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T4-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T5.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T5-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T6.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T6-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T7.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T7-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T8.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T8-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T9.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T9-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T10.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T10-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T11.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T11-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T12.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T12-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T13.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T13-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T14.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T14-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T15.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkB-p4-health-and-reports-T15-prompt.txt` (kickoff)

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

- [ ] T1 — Read context for parent phase — Evidence:
- [ ] T2 — Add graph.health.overview registry entry — Evidence:
- [ ] T3 — Add graph.health.issues registry entry — Evidence:
- [ ] T4 — Add graph.health.messages registry entry — Evidence:
- [ ] T5 — Add graph.reports.users_active registry entry — Evidence:
- [ ] T6 — Add graph.reports.email_activity registry entry — Evidence:
- [ ] T7 — Add graph.reports.teams_activity registry entry — Evidence:
- [ ] T8 — Add graph.reports.sharepoint_usage registry entry — Evidence:
- [ ] T9 — Add graph.reports.onedrive_usage registry entry — Evidence:
- [ ] T10 — Update legacy alias table — Evidence:
- [ ] T11 — Update YAML registry mirror — Evidence:
- [ ] T12 — M365 unit tests — Evidence:
- [ ] T13 — UCP routing unit tests — Evidence:
- [ ] T14 — Pre-commit + make test — Evidence:
- [ ] T15 — Commit (no push) — Evidence:

### Gate checklist

- [ ] CHECK:C0 — Parent phase B4 integration — Result:

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
