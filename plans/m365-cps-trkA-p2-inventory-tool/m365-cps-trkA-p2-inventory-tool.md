# Parent Phase A2 — Capability Inventory Tool

## Section 1: Plan Header

- **Plan ID:** `plan:m365-cps-trkA-p2-inventory-tool`
- **Parent Plan ID:** `plan:m365-cps-trkA-observability`
- **Title:** Parent Phase A2 — Capability Inventory Tool
- **Version:** 1.0
- **Status:** draft
- **Owner:** Phil Siniscalchi (Founder/Owner)
- **Date Created:** 2026-05-01
- **Date Updated:** 2026-05-01
- **North Star Ref:** `docs/NORTH_STAR.md`
- **Execution Plan Ref:** docs/platform/EXECUTION_PLAN.md - M365 CPS Track A P2
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
  - Add /v1/inventory endpoint to m365_runtime and m365_inventory MCP tool to UCP. Operators see implemented vs advertised vs aliased actions in one call.
- **Intent doc ref:** captured in this plan
- **Intent verification:** Tasks T1..T7 together satisfy this parent phase's objective.

## Section 4: Objective

- **Objective:** Add /v1/inventory endpoint to m365_runtime and m365_inventory MCP tool to UCP. Operators see implemented vs advertised vs aliased actions in one call.
- **Current state:** Parent phase scope draft; no implementation yet.
- **Target state:** All child tasks complete; GATE green; commit + push to feat/m365-cps-trkA.

## Section 5: Scope

### In scope

- Define inventory contract schema
- Implement runtime /v1/inventory endpoint
- Runtime endpoint unit tests
- Add UCP m365_inventory MCP tool
- MCP tool unit tests
- Pre-commit + make test in both repos
- Commit child phases (no push)

### Out of scope

- Anything outside this parent's allowlist

### File allowlist

- `M365: src/m365_runtime/graph/inventory.py`
- `M365: src/m365_runtime/__main__.py`
- `M365: tests/test_m365_inventory_endpoint.py`
- `UCP: src/ucp/m365_tools.py`
- `UCP: tests/test_m365_integration.py`
- `M365: docs/contracts/m365_inventory_schema.json`

### File denylist

- `Files outside the inventory + MCP tool surface`
- `Any file not in allowlist of the active child-phase task`

### Scope fence rule

Agent must STOP and re-scope if any file outside the allowlist is needed. Emit BLOCKED.

## Section 6: Requirements

### R2

- **Ref:** `plan:m365-cps-trkA-p2-inventory-tool:R2`
- **Description:** Carry-through of master R2; this parent phase contributes scoped behavior.
- **Acceptance criteria:** Per-task exit criteria; parent GATE passes.
- **Depends on:** none
- **User intent trace:** Master R2

### R8

- **Ref:** `plan:m365-cps-trkA-p2-inventory-tool:R8`
- **Description:** Carry-through of master R8; this parent phase contributes scoped behavior.
- **Acceptance criteria:** Per-task exit criteria; parent GATE passes.
- **Depends on:** none
- **User intent trace:** Master R8

## Section 7: Execution Sequence

- **Ordering:** ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']
- **Stop on first failure:** true
- **Strict ordering rule:** Do not start task N+1 until task N exit criteria are met.
- **MATHS phase mapping:** N/A (non-math scope)

## Section 8: Task Breakdown

### T1 — Define inventory contract schema

- **Ref:** `plan:m365-cps-trkA-p2-inventory-tool:T1`
- **Description:** Define JSON schema for the inventory response: {implemented_actions, alias_map, advertised_only, auth_mode_capability}. Document each field semantically.
- **Requirement refs:** R2
- **Depends on:** none
- **MATHS phase:** N/A
- **Deliverables:**
  - docs/contracts/m365_inventory_schema.json or inline in code
- **Exit criteria:**
  - Schema document committed; reviewed for completeness
- **Validation command:** `test -f $M365_ROOT/docs/contracts/m365_inventory_schema.json || echo 'inline-acceptable'`
- **Implementation notes:** Schema can live inline in m365_runtime/graph/inventory.py or as a separate JSON file.

### T2 — Implement runtime /v1/inventory endpoint

- **Ref:** `plan:m365-cps-trkA-p2-inventory-tool:T2`
- **Description:** Add /v1/inventory endpoint in m365_runtime that returns the inventory contract: list READ_ONLY_REGISTRY actions, the alias map (loaded from ucp_m365_pack.client), and the advertised-but-unimplemented set (agents.yaml allowed_actions minus alias keys minus registry keys).
- **Requirement refs:** R2
- **Depends on:** T1
- **MATHS phase:** N/A
- **Deliverables:**
  - m365_runtime endpoint /v1/inventory
- **Exit criteria:**
  - GET /v1/inventory returns 200 with valid JSON matching schema
- **Validation command:** `cd $M365_ROOT && .venv/bin/python -m pytest tests/test_m365_inventory_endpoint.py -x`
- **Files to modify:**
  - M365: src/m365_runtime/graph/inventory.py (new)
  - M365: src/m365_runtime/**main**.py (route wiring)

### T3 — Runtime endpoint unit tests

- **Ref:** `plan:m365-cps-trkA-p2-inventory-tool:T3`
- **Description:** Add tests/test_m365_inventory_endpoint.py covering: (a) implemented_actions matches READ_ONLY_REGISTRY keys, (b) alias_map matches LEGACY_ACTION_TO_RUNTIME_ACTION, (c) advertised_only correctly diffs agents.yaml.
- **Requirement refs:** R2
- **Depends on:** T2
- **MATHS phase:** N/A
- **Deliverables:**
  - tests/test_m365_inventory_endpoint.py
- **Exit criteria:**
  - pytest -k inventory_endpoint -x exits 0
- **Validation command:** `cd $M365_ROOT && .venv/bin/python -m pytest tests/test_m365_inventory_endpoint.py -x`
- **Files to modify:**
  - M365: tests/test_m365_inventory_endpoint.py

### T4 — Add UCP m365_inventory MCP tool

- **Ref:** `plan:m365-cps-trkA-p2-inventory-tool:T4`
- **Description:** Add @mcp.tool() m365_inventory in src/ucp/m365_tools.py that fetches the runtime /v1/inventory and returns the parsed JSON. Include shape validation against the contract schema.
- **Requirement refs:** R2
- **Depends on:** T3
- **MATHS phase:** N/A
- **Deliverables:**
  - UCP src/ucp/m365_tools.py with m365_inventory tool
- **Exit criteria:**
  - MCP tool m365_inventory listed in tool registry; returns expected shape
- **Validation command:** `cd $UCP_ROOT && .venv/bin/python -c "from ucp.m365_tools import m365_inventory; print('importable')"`
- **Files to modify:**
  - UCP: src/ucp/m365_tools.py

### T5 — MCP tool unit tests

- **Ref:** `plan:m365-cps-trkA-p2-inventory-tool:T5`
- **Description:** Add test_m365_inventory_tool_shape in tests/test_m365_integration.py validating UCP mcp tool returns the contract.
- **Requirement refs:** R2
- **Depends on:** T4
- **MATHS phase:** N/A
- **Deliverables:**
  - tests/test_m365_integration.py with inventory shape test
- **Exit criteria:**
  - pytest -k inventory_tool -x exits 0
- **Validation command:** `cd $UCP_ROOT && .venv/bin/python -m pytest tests/test_m365_integration.py -k inventory_tool -x`
- **Files to modify:**
  - UCP: tests/test_m365_integration.py

### T6 — Pre-commit + make test in both repos

- **Ref:** `plan:m365-cps-trkA-p2-inventory-tool:T6`
- **Description:** Standard validation gate before commit.
- **Requirement refs:** R8
- **Depends on:** T5
- **MATHS phase:** N/A
- **Deliverables:**
  - pre-commit clean
  - make test green
- **Exit criteria:**
  - exit 0 in both repos
- **Validation command:** `cd $M365_ROOT && pre-commit run --all-files && make test && cd $UCP_ROOT && pre-commit run --all-files && make test`

### T7 — Commit child phases (no push)

- **Ref:** `plan:m365-cps-trkA-p2-inventory-tool:T7`
- **Description:** Commit format 'plan:m365-cps-trkA-p2: T1-T6 inventory tool'.
- **Requirement refs:** R8
- **Depends on:** T6
- **MATHS phase:** N/A
- **Deliverables:**
  - Commit in both repos
- **Exit criteria:**
  - git log shows the commit
- **Validation command:** `cd $UCP_ROOT && git log --oneline -1 | grep 'plan:m365-cps-trkA-p2' && cd $M365_ROOT && git log --oneline -1 | grep 'plan:m365-cps-trkA-p2'`

## Section 9: Gate Checks

### CHECK:C0 — Parent phase A2 integration

- **Description:** All child tasks T1..T7 green; integration test pass
- **Task ref:** T1..T7
- **Validation command:** `cd $UCP_ROOT && .venv/bin/python tests/integration/m365_inventory_e2e.py`
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
| docs/contracts/m365_inventory_schema.json or inline in code | varies | T1 | per-task | see Section 8 / T1 |
| m365_runtime endpoint /v1/inventory | varies | T2 | per-task | see Section 8 / T2 |
| tests/test_m365_inventory_endpoint.py | Python | T3 | per-task | see Section 8 / T3 |
| UCP src/ucp/m365_tools.py with m365_inventory tool | varies | T4 | per-task | see Section 8 / T4 |
| tests/test_m365_integration.py with inventory shape test | varies | T5 | per-task | see Section 8 / T5 |
| pre-commit clean | varies | T6 | per-task | see Section 8 / T6 |
| make test green | varies | T6 | per-task | see Section 8 / T6 |
| Commit in both repos | varies | T7 | per-task | see Section 8 / T7 |

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
  - `docs/prompts/codex-m365-cps-trkA-p2-inventory-tool-T1.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkA-p2-inventory-tool-T1-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkA-p2-inventory-tool-T2.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkA-p2-inventory-tool-T2-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkA-p2-inventory-tool-T3.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkA-p2-inventory-tool-T3-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkA-p2-inventory-tool-T4.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkA-p2-inventory-tool-T4-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkA-p2-inventory-tool-T5.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkA-p2-inventory-tool-T5-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkA-p2-inventory-tool-T6.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkA-p2-inventory-tool-T6-prompt.txt` (kickoff)
  - `docs/prompts/codex-m365-cps-trkA-p2-inventory-tool-T7.md` (detailed)
  - `docs/prompts/codex-m365-cps-trkA-p2-inventory-tool-T7-prompt.txt` (kickoff)

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

- [ ] T1 — Define inventory contract schema — Evidence:
- [ ] T2 — Implement runtime /v1/inventory endpoint — Evidence:
- [ ] T3 — Runtime endpoint unit tests — Evidence:
- [ ] T4 — Add UCP m365_inventory MCP tool — Evidence:
- [ ] T5 — MCP tool unit tests — Evidence:
- [ ] T6 — Pre-commit + make test in both repos — Evidence:
- [ ] T7 — Commit child phases (no push) — Evidence:

### Gate checklist

- [ ] CHECK:C0 — Parent phase A2 integration — Result:

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
