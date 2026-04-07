# Plan: M365 Persona-Action P1 Notebook Evidence Scope Correction

**Plan ID:** `m365-persona-action-p1-notebook-evidence-scope-correction`
**Parent Plan ID:** `m365-persona-action-full-support-remediation`
**Status:** 🟢 Active
**Date:** 2026-04-07
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-persona-action-p1-notebook-evidence-scope-correction:R0`
**North Star alignment:** `Operations/NORTHSTAR.md` — keep the persona-action remediation truthful and fail-closed by refusing to start dead-route code repair until the phase has explicit notebook-backed evidence accepted by governance.
**Canonical predecessor:** `plans/m365-persona-action-full-support-remediation/m365-persona-action-full-support-remediation.md`
**Governance evidence:** `notebooks/m365/INV-M365-CO-persona-action-p1-notebook-evidence-scope-correction-v1.ipynb`, `configs/generated/persona_action_p1_notebook_evidence_scope_correction_v1_verification.json`
**Historical lineage:** successor blocker package after the first `P1` dead-route code write was denied with `map-2-code-notebook-required`.

**Draft vs Active semantics:** This child plan starts in **Draft**. It becomes **Active** only when the parent initiative remains on `P1`, the approval packet is presented and receives explicit `go`, and no sibling remediation phase is concurrently active. It becomes **Complete** only after the notebook-backed blocker evidence is published, the blocked `P1` code-write validation is reopened under child-plan authority, trackers are synchronized, and the parent initiative truthfully returns control to `P1`.

**Approval and governance gates:** Present the approval packet first. Wait for explicit `go`. Call MCP `validate_action` before every mutating action, including notebook extraction, file edits, commits, pushes, and tracker synchronization. Stop on first red. Do not auto-advance to `P2`.

**Notebook-first discipline:** `P1S` is a notebook-backed governance-unblock phase. The blocked write set, the exact MCP denial, and the required future dead-route evidence chain must be frozen in notebooks first. No `P1` code repair is allowed before that notebook-backed evidence exists and the blocked validation is re-opened.

## Objective

Create the bounded child phase that publishes explicit notebook-backed evidence for the `P1` dead-route remediation blocker so the parent initiative can truthfully reopen the first code-write validation and continue dead-route repair under governed notebook-first conditions.

## Current State

- Parent initiative:
  - `plan:m365-persona-action-full-support-remediation`
- Completed parent phase:
  - `P0` read-only backlog lock
- Observed `P1` write target:
  - `src/ops_adapter/actions.py`
  - `src/smarthaus_common/permission_enforcer.py`
  - `policies/ops.rego`
  - `tests/test_ops_adapter.py`
  - `tests/test_policies.py`
  - `tests/test_executor_routing_v2.py`
- Blocking governance verdict:
  - `validate_action(file_edit)` for the first `P1` code repair returned `allowed:false`
  - violation id: `map-2-code-notebook-required`
- Existing supporting notebook evidence:
  - `notebooks/m365/INV-M365-CK-persona-action-mapping-audit-v1.ipynb`
  - `notebooks/m365/INV-M365-CN-persona-action-route-certification-v1.ipynb`
- Existing supporting scorecards:
  - `artifacts/scorecards/scorecard_l86.json`
  - `artifacts/scorecards/scorecard_l88.json`
- Gap:
  - those notebooks prove the certified mapping and route backlog, but the parent initiative still lacks a phase-specific notebook-backed blocker package that defines the admissible `P1` evidence chain for dead-route code remediation

## Decision Rule

`DeadRouteBacklogFrozen = DeadRoutedPairs116 AND DeadRoutedAliases21`

`FirstP1WriteBlocked = validate_action(file_edit, first P1 code repair) returns map-2-code-notebook-required`

`PhaseSpecificEvidenceSurfaceDefined = P1S owns governance notebook evidence, generated verification output, and the required future L89 dead-route evidence chain`

`BlockedWriteSetFrozen = actions.py AND permission_enforcer.py AND ops.rego AND tests/test_ops_adapter.py AND tests/test_policies.py AND tests/test_executor_routing_v2.py`

`P1S_GO = DeadRouteBacklogFrozen AND FirstP1WriteBlocked AND PhaseSpecificEvidenceSurfaceDefined AND BlockedWriteSetFrozen`

If `P1S_GO` is false, `P1S` must emit `NO-GO`, stop fail-closed, and keep the parent initiative at `P1`.

## Scope

### In scope

- restate the `P1` dead-route blocker explicitly from certification and MCP truth
- create a phase-specific notebook-backed governance evidence chain for the blocked `P1` code write
- publish generated verification output for that governance evidence
- expand the parent remediation package to acknowledge the `P1S` blocker-fix child phase
- synchronize trackers so the parent initiative truthfully pauses at `P1S`
- reopen the blocked `P1` code-write validation under child-plan authority
- hand control back to the parent initiative with `P1` as the next act only after `P1S` is green, committed, and pushed

### Out of scope

- actual `P1` dead-route code remediation
- `P2` legacy-stub remediation
- `P3` permission/alias remediation
- `P4` policy-fence remediation
- any runtime code, registry, or test extraction beyond the blocker evidence package
- any UCP-side changes

### File allowlist

- `plans/m365-persona-action-p1-notebook-evidence-scope-correction/**`
- `docs/prompts/codex-m365-persona-action-p1-notebook-evidence-scope-correction.md`
- `docs/prompts/codex-m365-persona-action-p1-notebook-evidence-scope-correction-prompt.txt`
- `plans/m365-persona-action-full-support-remediation/m365-persona-action-full-support-remediation.md`
- `notebooks/m365/INV-M365-CO-persona-action-p1-notebook-evidence-scope-correction-v1.ipynb`
- `configs/generated/persona_action_p1_notebook_evidence_scope_correction_v1_verification.json`
- `docs/ma/lemmas/L89_m365_persona_action_dead_route_remediation_v1.md`
- `invariants/lemmas/L89_m365_persona_action_dead_route_remediation_v1.yaml`
- `notebooks/m365/INV-M365-CP-persona-action-dead-route-remediation-v1.ipynb`
- `notebooks/lemma_proofs/L89_m365_persona_action_dead_route_remediation_v1.ipynb`
- `artifacts/scorecards/scorecard_l89.json`
- `configs/generated/persona_action_dead_route_remediation_v1_verification.json`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `registry/**`
- `src/**`
- `tests/**`
- `../UCP/**`
- any path not listed in the allowlist

## Requirements

- **R0** — Create the bounded `P1S` blocker package.
- **R1** — Make the `P1` governance blocker explicit from certification and MCP truth.
- **R2** — Produce notebook-backed governance evidence for the blocked `P1` write.
- **R3** — Expand the admissible evidence surface to include the future `L89` dead-route notebook chain.
- **R4** — Reopen the blocked `P1` code-write validation under child-plan authority.
- **R5** — Synchronize the parent plan and governance trackers truthfully.
- **R6** — Commit and push `P1S` before resuming parent `P1`.

## Child Acts

### P1SA — Blocker restatement

- freeze the certified dead-route backlog and the exact MCP denial that blocked the first `P1` write

### P1SB — Governance notebook evidence

- create the phase-specific governance notebook evidence and generated verification output
- define the required future `L89` dead-route notebook chain explicitly

### P1SC — Validation reopen and handback

- reopen the blocked `P1` code-write validation under child-plan authority
- synchronize trackers
- validate, commit, push, and return the parent initiative to `P1`

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-persona-action-p1-notebook-evidence-scope-correction.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-persona-action-p1-notebook-evidence-scope-correction-prompt.txt`

## Validation Strategy

- require the governance notebook evidence to preserve the observed blocker truth:
  - `116` dead-routed active pairs
  - `21` dead-routed unique aliases
  - blocked write set frozen exactly
  - MCP violation `map-2-code-notebook-required`
- require generated verification output for the governance-alignment notebook
- require the parent remediation plan and trackers to point to `P1S` while the blocker is unresolved
- require a successful reopen of the blocked `P1` file-edit validation under child-plan authority before handback
- run `git diff --check`

## Agent Constraints

- Do not begin `P1` code edits inside `P1S` until the blocked write validation is re-opened.
- Do not widen into `P2`, `P3`, or `P4` during `P1S`.
- Do not edit runtime code, registries, or tests in `P1S`.
- Commit and push `P1S` before any parent `P1` code work begins.

## Governance Closure

- [ ] `Operations/ACTION_LOG.md`
- [ ] `Operations/EXECUTION_PLAN.md`
- [ ] `Operations/PROJECT_FILE_INDEX.md`
- [ ] this child plan `status -> complete`

## Execution Outcome

- **Decision:** `pending`
- **Approved by:** `operator explicit go`
- **Completion timestamp:** `pending`
