# M365 Capability Pack Surface Remediation

## Section 1: Plan Header

- **Plan ID:** `plan:m365-capability-pack-surface-remediation`
- **Parent Plan ID:** `null`
- **Title:** M365 Capability Pack Surface Remediation
- **Version:** 1.0
- **Status:** approved
- **Owner:** Phil Siniscalchi (Founder/Owner)
- **Date Created:** 2026-05-01
- **Date Updated:** 2026-05-01
- **North Star Ref:** `docs/NORTH_STAR.md`
- **Execution Plan Ref:** docs/platform/EXECUTION_PLAN.md (UCP) / Operations/EXECUTION_PLAN.md (M365) - M365 Capability Pack Remediation
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
  - Make the gate's denial reasons honest - unknown action must not masquerade as mutation_fence.
  - Build out the missing read coverage so the runtime actually implements what agents.yaml advertises.
  - Surface coverage status in the contract so operators see the gap explicitly instead of finding it call-by-call.
  - Master plan with three tracks; granular child phases so an executing agent does not drift.
  - Each child commits, each parent commits + pushes, each track merges. Test before each gate.
- **Intent doc ref:** captured in this plan
- **Intent verification:** Track A (status semantics + observability) -> user requirement 1. Track B (coverage build-out) -> user requirement 2. Track C (coverage status contract) -> user requirement 3. Section 7 strict ordering + per-phase validation commands -> user requirements 4 + 5.

## Section 4: Objective

- **Objective:** Remediate the M365 capability pack so its advertised surface matches its implemented surface, denials are semantically honest, and operators have a pre-flight diagnostic to see the gap. Delivered in three tracks of increasing scope.
- **Current state:** Of 161 actions advertised in agents.yaml, only 11 are implemented in READ_ONLY_REGISTRY (~7% coverage). _denial_to_status() collapses unknown_action into mutation_fence, making denials misleading. There is no introspection of the runtime's own surface. UCP exposes 23+ m365_* MCP tools whose docstrings advertise actions the runtime does not know.
- **Target state:** Track A complete: denial reasons honest; m365_inventory tool exists; auth_check surfaces token-vs-registry intersection. Track B complete: SharePoint/Calendar/Mail/Health/Reports/Directory/Teams reads implemented; auth-mode tiers (read-only/standard/admin) supported. Track C complete: every advertised action carries coverage_status; not_yet_implemented status code exists; capability map doc auto-generated.

## Section 5: Scope

### In scope

- Status code semantics fix in m365_runtime/graph/registry.py + actions.py (Track A)
- Capability inventory endpoint + MCP tool (Track A)
- Pre-flight scope/registry intersection in auth_check (Track A)
- Read action implementations in m365_runtime + alias table updates (Track B)
- Auth-mode tier system at m365_auth_start (Track B)
- Coverage-status field in agents.yaml schema (Track C)
- not_yet_implemented status code (Track C)
- Operator capability map doc generation (Track C)

### Out of scope

- Mutation/write actions (covered by separate mutation-governance plan)
- Risk-tier reclassification of existing agents
- New MCP tools beyond m365_inventory
- Frontend changes to apps/desktop
- M365 version bump unless Track B p7 explicitly cuts a new release
- Power Platform executor changes
- Mathematical Autopsy / invariant promotion (this work is non-math scope)

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

### R1

- **Ref:** `plan:m365-capability-pack-surface-remediation:R1`
- **Description:** Denial reasons returned by the runtime must be semantically distinct. unknown_action MUST NOT be reported as mutation_fence.
- **Acceptance criteria:** Calling an action not in READ_ONLY_REGISTRY returns status_class == "unknown_action" (not "mutation_fence"). Verified by unit test test_unknown_action_returns_unknown_action_status in M365 and integration test test_m365_unknown_action_routing in UCP.
- **Depends on:** none
- **User intent trace:** User requirement 1 (make denials honest)

### R2

- **Ref:** `plan:m365-capability-pack-surface-remediation:R2`
- **Description:** An inventory endpoint and MCP tool MUST exist that report which actions are implemented in the runtime, which legacy aliases exist, and which agents advertise actions that have no runtime implementation.
- **Acceptance criteria:** m365_inventory MCP tool returns JSON with keys {implemented_actions, alias_map, advertised_only, auth_mode_capability}. Verified by test_m365_inventory_tool_shape and live integration call.
- **Depends on:** R1
- **User intent trace:** User requirements 1 and 3

### R3

- **Ref:** `plan:m365-capability-pack-surface-remediation:R3`
- **Description:** m365_auth_check response MUST include a token-vs-registry intersection showing which registered actions the current session can actually invoke.
- **Acceptance criteria:** m365_auth_check returns {invokable_actions, blocked_by_auth_mode, blocked_by_scopes}. Verified by test_auth_check_intersection.
- **Depends on:** R1
- **User intent trace:** User requirements 1 and 3

### R4

- **Ref:** `plan:m365-capability-pack-surface-remediation:R4`
- **Description:** Coverage of read actions across SharePoint, Calendar, Mail, Service Health, Reports, Directory, and Teams MUST be implemented in READ_ONLY_REGISTRY with matching alias entries.
- **Acceptance criteria:** Every action listed in Track B parent phases B1-B5 has a registry entry, an alias entry where named differently, a YAML mirror, unit tests, and a live tenant smoke test pass.
- **Depends on:** R1, R2
- **User intent trace:** User requirement 2

### R5

- **Ref:** `plan:m365-capability-pack-surface-remediation:R5`
- **Description:** Auth-mode tiers (read-only / standard / admin) MUST be selectable at m365_auth_start and enforced at admit().
- **Acceptance criteria:** m365_auth_start accepts {tier}; token store records tier; admit() rejects calls whose registry entry requires a higher tier than session holds. Verified by test_auth_tier_enforcement.
- **Depends on:** R4
- **User intent trace:** User requirement 2

### R6

- **Ref:** `plan:m365-capability-pack-surface-remediation:R6`
- **Description:** Every entry in agents.yaml allowed_actions MUST carry a coverage_status field of {implemented, aliased, planned}. Calling a planned action MUST return status_class == "not_yet_implemented".
- **Acceptance criteria:** agents.yaml schema updated; existing entries migrated; validate_agent_action surfaces coverage_status; runtime returns not_yet_implemented for planned actions.
- **Depends on:** R1
- **User intent trace:** User requirement 3

### R7

- **Ref:** `plan:m365-capability-pack-surface-remediation:R7`
- **Description:** An operator-facing capability map document MUST be auto-generated from registry + agents.yaml + alias table and committed to docs/.
- **Acceptance criteria:** Doc exists; CI regenerates on registry changes; doc matches runtime state on every commit.
- **Depends on:** R6
- **User intent trace:** User requirement 3

### R8

- **Ref:** `plan:m365-capability-pack-surface-remediation:R8`
- **Description:** Each child phase commits locally; each parent phase commits + pushes; each track merges. Tests pass at each gate before the next phase opens.
- **Acceptance criteria:** Git history shows the cadence; each parent-phase plan's GATE task records validation_command output as evidence.
- **Depends on:** none
- **User intent trace:** User requirements 4 and 5

## Section 7: Execution Sequence

- **Ordering:** ['T1', 'T2', 'T3']
- **Stop on first failure:** true
- **Strict ordering rule:** Do not start task N+1 until task N exit criteria are met.
- **MATHS phase mapping:** N/A (non-math scope)

## Section 8: Task Breakdown

### T1 — Execute Track A

- **Ref:** `plan:m365-capability-pack-surface-remediation:T1`
- **Description:** Execute plan:m365-cps-trkA-observability end-to-end across all 4 parent phases.
- **Requirement refs:** R1, R2, R3, R8
- **Depends on:** none
- **MATHS phase:** N/A
- **Deliverables:**
  - All Track A parent-phase plans status: complete
  - feat/m365-cps-trkA branch merged to development (UCP) and main (M365)
- **Exit criteria:**
  - plan:m365-cps-trkA-observability status == complete
  - All Track A gates green
  - Live integration test pass
- **Validation command:** `.venv/bin/python scripts/check_track_complete.py trkA`
- **Implementation notes:** Sub-plan: plan:m365-cps-trkA-observability

### T2 — Execute Track B

- **Ref:** `plan:m365-capability-pack-surface-remediation:T2`
- **Description:** Execute plan:m365-cps-trkB-coverage end-to-end across all 7 parent phases.
- **Requirement refs:** R4, R5, R8
- **Depends on:** T1
- **MATHS phase:** N/A
- **Deliverables:**
  - Track B merged
  - New M365 marketplace artifact published
- **Exit criteria:**
  - plan:m365-cps-trkB-coverage status == complete
  - Live tenant smoke pass on every parent phase
- **Validation command:** `.venv/bin/python scripts/check_track_complete.py trkB`
- **Implementation notes:** Sub-plan: plan:m365-cps-trkB-coverage. Cuts new M365 release.

### T3 — Execute Track C

- **Ref:** `plan:m365-capability-pack-surface-remediation:T3`
- **Description:** Execute plan:m365-cps-trkC-truth-in-advertising end-to-end across all 5 parent phases.
- **Requirement refs:** R6, R7, R8
- **Depends on:** T2
- **MATHS phase:** N/A
- **Deliverables:**
  - Track C merged
  - Capability map doc published
- **Exit criteria:**
  - plan:m365-cps-trkC-truth-in-advertising status == complete
- **Validation command:** `.venv/bin/python scripts/check_track_complete.py trkC`
- **Implementation notes:** Sub-plan: plan:m365-cps-trkC-truth-in-advertising

## Section 9: Gate Checks

### CHECK:C0 — Plan schema valid

- **Description:** Master plan + all sub-plans validate against PLAN_TEMPLATE_SCHEMA
- **Task ref:** T1, T2, T3
- **Validation command:** `.venv/bin/python scripts/validate_plan_schema.py plans/m365-capability-pack-surface-remediation/m365-capability-pack-surface-remediation.yaml`
- **Pass criteria:** exit code 0
- **Fail action:** block

### CHECK:C1 — Track A complete

- **Description:** All Track A parent phases green; live integration pass
- **Task ref:** T1
- **Validation command:** `.venv/bin/python scripts/check_track_complete.py trkA`
- **Pass criteria:** All parent-phase plan statuses == complete
- **Fail action:** block

### CHECK:C2 — Track B complete

- **Description:** All Track B parent phases green; live tenant smoke pass
- **Task ref:** T2
- **Validation command:** `.venv/bin/python scripts/check_track_complete.py trkB`
- **Pass criteria:** All parent-phase plan statuses == complete
- **Fail action:** block

### CHECK:C3 — Track C complete

- **Description:** All Track C parent phases green
- **Task ref:** T3
- **Validation command:** `.venv/bin/python scripts/check_track_complete.py trkC`
- **Pass criteria:** All parent-phase plan statuses == complete
- **Fail action:** block

### Decision rule

- **GO:** All gates pass.
- **NO-GO:** Any gate fails.

### No-go triggers

- Any track plan in failed or blocked state
- Any parent-phase plan unable to complete its GATE
- Live tenant smoke regression on previously-green action
- Schema validation fails on any plan file

## Section 10: Determinism Requirements

N/A — non-math scope. Tests must be hermetic; live tenant only in GATE smoke tests.

## Section 11: Artifacts

| Path | Format | Producer | Schema ref | Validation |
|------|--------|----------|------------|------------|
| All Track A parent-phase plans status: complete | varies | T1 | per-task | see Section 8 / T1 |
| feat/m365-cps-trkA branch merged to development (UCP) and main (M365) | varies | T1 | per-task | see Section 8 / T1 |
| Track B merged | varies | T2 | per-task | see Section 8 / T2 |
| New M365 marketplace artifact published | varies | T2 | per-task | see Section 8 / T2 |
| Track C merged | varies | T3 | per-task | see Section 8 / T3 |
| Capability map doc published | varies | T3 | per-task | see Section 8 / T3 |

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
| Live tenant rate limits during smoke tests | medium | Backoff + spread across parent phases; cache token | open |
| Track B coverage scope grows beyond plan | high | Per-parent-phase allowlist enforces scope fence | mitigated |
| Cross-repo drift between UCP and M365 plan copies | medium | Generator script as single source of truth; re-run to sync | mitigated |
| Status code change breaks downstream consumers | medium | Track A introduces new code without removing old behavior; deprecation in Track C | mitigated |
| Re-packaging M365 release breaks UCP binding | high | release_artifacts.py SHA pinning; release artifact acceptance test | mitigated |

### Hard blockers

- M365 main branch frozen during release cut
- Tenant unavailability during GATE smoke tests
- PLAN_TEMPLATE_SCHEMA changes mid-execution

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

- [ ] T1 — Execute Track A — Evidence:
- [ ] T2 — Execute Track B — Evidence:
- [ ] T3 — Execute Track C — Evidence:

### Gate checklist

- [ ] CHECK:C0 — Plan schema valid — Result:
- [ ] CHECK:C1 — Track A complete — Result:
- [ ] CHECK:C2 — Track B complete — Result:
- [ ] CHECK:C3 — Track C complete — Result:

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
- **Master plan:** `plan:m365-capability-pack-surface-remediation`
- **MATHS prompt template:** `agent_governance/master-maths-prompt-template.md`
- **Plan template:** `agent_governance/PLAN_TEMPLATE.md`

---
<!-- Generated by scripts/generate_m365_cps_scaffold.py on 2026-05-01 -->
