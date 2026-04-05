# Plan: M365 Authoritative Persona Activation Gate Closeout

**Plan ID:** `m365-authoritative-persona-activation-gate-closeout`
**Parent Plan ID:** `m365-authoritative-persona-humanization-expansion`
**Status:** 🟠 Draft
**Date:** 2026-04-05
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-authoritative-persona-activation-gate-closeout:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — close the activation gate only when every promoted persona is fully named, department-bound, manager-bound, escalation-bound, capability-mapped, registry-authoritative, and truthfully certified, so no silent active-state expansion occurs.
**Canonical predecessor:** `plans/m365-authoritative-persona-certification-and-count-rebase/m365-authoritative-persona-certification-and-count-rebase.md`

**Draft vs Active semantics:** This child plan starts in **Draft**. It transitions to **Active** only when (1) H4 is green, (2) the operator presents the approval packet and receives explicit "go", and (3) no other child phase under the parent initiative is concurrently active. It transitions to **Complete** only after its own gate emits GO, the phase is committed, and the branch is pushed.

**Approval and governance gates:** Before execution, present the approval packet and wait for explicit "go". During execution, call MCP `validate_action` before every mutating action and obey the verdict. Stop on first red. This is the final child phase for the initiative.

**Notebook-first discipline:** H5 is the final notebook-backed activation phase. All gate conditions, activation counts, and final active-surface truth must be derived and proven in notebooks first. No direct activation-state extraction is allowed before scorecard green.

## Objective

Promote the `20` newly authoritative personas from staged authoritative records into the active surface only after H2 through H4 are green, and rebase the final active-surface truth to the post-closeout state.

## Decision Rule

`PrereqGreen = H2_GO AND H3_GO AND H4_GO`

`ActivationPrereqsSatisfied = FOR ALL promoted_persona: {display_name, title, department, manager, escalation_owner, capability_map_entry, authoritative_registry_entry} are present and verified`

`FinalRegistryStateTruthful = persona_registry.summary.total_personas = 59 AND active_personas = 54 AND planned_personas = 5`

`FinalActiveSurfaceTruthful = activated_surface.registry_backed_personas = 54 AND deferred_external_personas = 5`

`H5_GO = PrereqGreen AND ActivationPrereqsSatisfied AND FinalRegistryStateTruthful AND FinalActiveSurfaceTruthful`

If `H5_GO` is false, H5 must emit `NO-GO`, stop, and leave the promoted personas non-active.

## Scope

### In scope

- activate all `20` promoted personas only after their prerequisites are green
- update `registry/persona_registry_v2.yaml` and `registry/persona_capability_map.yaml` to the final active-state truth
- update the final active-surface and packaging/commercialization boundary artifacts
- update verifiers and tests for the final `59 total / 54 active / 5 planned` state
- produce notebook-backed proof and generated verification output for final activation closeout

### Out of scope

- changing `registry/agents.yaml`
- widening the department model
- adding any new persona beyond the `20` already governed in the parent initiative

### File allowlist

- `plans/m365-authoritative-persona-activation-gate-closeout/**`
- `docs/prompts/codex-m365-authoritative-persona-activation-gate-closeout.md`
- `docs/prompts/codex-m365-authoritative-persona-activation-gate-closeout-prompt.txt`
- `registry/persona_registry_v2.yaml`
- `registry/persona_capability_map.yaml`
- `registry/activated_persona_surface_v1.yaml`
- `registry/workforce_packaging_v1.yaml`
- `docs/commercialization/m365-activated-persona-surface-v1.md`
- `docs/commercialization/m365-workforce-packaging-v1.md`
- `docs/commercialization/m365-persona-registry-v2.md`
- `scripts/ci/build_persona_registry_v2.py`
- `scripts/ci/verify_persona_registry_v2.py`
- `scripts/ci/verify_activated_persona_surface_v1.py`
- `scripts/ci/verify_workforce_packaging_v1.py`
- `tests/test_persona_registry_v2.py`
- `tests/test_activated_persona_surface_v1.py`
- `tests/test_workforce_packaging_v1.py`
- `docs/ma/lemmas/L*_m365_authoritative_persona_activation_gate_closeout_v1.md`
- `invariants/lemmas/L*_m365_authoritative_persona_activation_gate_closeout_v1.yaml`
- `notebooks/m365/INV-M365-*-authoritative-persona-activation-gate-closeout-v1.ipynb`
- `notebooks/lemma_proofs/L*_m365_authoritative_persona_activation_gate_closeout_v1.ipynb`
- `artifacts/scorecards/scorecard_*.json`
- `configs/generated/authoritative_persona_activation_gate_closeout_v1_verification.json`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `registry/agents.yaml`
- `registry/ai_team.json`

## Requirements

- **R1** — Enforce that all H2 through H4 prerequisites are green before activation.
- **R2** — Activate all `20` promoted personas only if every fail-closed prerequisite is satisfied.
- **R3** — Rebase the final registry state to `59 total / 54 active / 5 planned`.
- **R4** — Rebase the final active-surface and packaging truth to the post-closeout state.
- **R5** — Update verifiers and tests for the final active-state truth.
- **R6** — Produce notebook-backed proof, commit, and push final closeout.

## Child Acts

### H5A — Activation Gate Verification

- verify all promoted personas satisfy the fail-closed prerequisites
- stop immediately if any prerequisite is missing

### H5B — Final Registry and Active-Surface Rebase

- promote the `20` personas to the final active state
- update the final activated-surface truth

### H5C — Final Validation and Branch Closeout

- run targeted verifiers and tests
- update governance surfaces
- commit and push the final H5 closeout

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-authoritative-persona-activation-gate-closeout.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-authoritative-persona-activation-gate-closeout-prompt.txt`

## Validation Strategy

- verify the final registry summary is `59 total / 54 active / 5 planned`
- verify the final active-surface contract reports `54` active personas and `5` deferred external personas
- verify targeted verifiers and tests are green
- run `git diff --check`

## Governance Closure

- [ ] `Operations/ACTION_LOG.md`
- [ ] `Operations/EXECUTION_PLAN.md`
- [ ] `Operations/PROJECT_FILE_INDEX.md`
- [ ] This child plan `status -> complete`

## Execution Outcome

- **Decision:** `pending`
- **Approved by:** `pending`
- **Completion timestamp:** `pending`

## Agent Constraints

- Do not activate a partial subset of the `20` promoted personas.
- Do not widen the department model.
- This is the final child phase; close it truthfully or stop fail-closed.
