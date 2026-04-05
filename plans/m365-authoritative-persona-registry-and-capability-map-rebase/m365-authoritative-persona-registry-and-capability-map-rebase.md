# Plan: M365 Authoritative Persona Registry and Capability-Map Rebase

**Plan ID:** `m365-authoritative-persona-registry-and-capability-map-rebase`
**Parent Plan ID:** `m365-authoritative-persona-humanization-expansion`
**Status:** 🟠 Draft
**Date:** 2026-04-05
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-authoritative-persona-registry-and-capability-map-rebase:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — deliberately rebase the authoritative roster and capability surfaces from the current `39`-persona truth to the future `59`-persona truth without silently activating the promoted personas before the activation gate closes.
**Canonical predecessor:** `plans/m365-authoritative-persona-humanized-employee-record-completion/m365-authoritative-persona-humanized-employee-record-completion.md`

**Draft vs Active semantics:** This child plan starts in **Draft**. It transitions to **Active** only when (1) H2 is green, (2) the operator presents the approval packet and receives explicit "go", and (3) no other child phase under the parent initiative is concurrently active. It transitions to **Complete** only after its own gate emits GO, the phase is committed, and the branch is pushed.

**Approval and governance gates:** Before execution, present the approval packet and wait for explicit "go". During execution, call MCP `validate_action` before every mutating action and obey the verdict. Stop on first red. Do not auto-advance to H4.

**Notebook-first discipline:** H3 is a notebook-backed registry-rebase phase. All roster, registry, and capability-map transformations must be modeled and verified in notebooks first. No direct extraction into the authoritative surfaces is allowed before notebook evidence and scorecard outputs are green.

## Objective

Rebase `registry/ai_team.json`, `registry/persona_registry_v2.yaml`, and `registry/persona_capability_map.yaml` so all `20` promoted personas become authoritative named digital employees while remaining non-active until H5 closes the activation gate.

## Decision Rule

`RosterRebased = ai_team.total_agents = 59 AND ai_team.departments = 10 AND all 20 promoted personas are present with names and titles`

`RegistryRebased = persona_registry.summary.total_personas = 59 AND active_personas = 34 AND planned_personas = 25`

`CapabilityMapRebased = persona_capability_map.summary.total_personas = 59 AND current_registry_backed_personas = 34 AND persona_contract_only_personas = 25 AND non_authoritative_registry_agents = 0`

`ActivationSeparationPreserved = promoted_personas remain non-active in H3 and are not counted inside the active surface`

`H3_GO = H2_GO AND RosterRebased AND RegistryRebased AND CapabilityMapRebased AND ActivationSeparationPreserved`

If `H3_GO` is false, H3 must emit `NO-GO`, stop, and keep the authoritative registry surfaces at their prior truth.

## Scope

### In scope

- rebase `registry/ai_team.json` to `59` named authoritative personas across `10` departments
- rebase `registry/persona_registry_v2.yaml` to `59` total personas while preserving the fail-closed pre-H5 active/planned split
- rebase `registry/persona_capability_map.yaml` to remove the `20` extras from the non-authoritative overflow set
- update the authoritative runtime loader and verifier surfaces if required by the truthful staged model
- produce notebook-backed proof, generated verification output, and tests

### Out of scope

- activating the `20` promoted personas
- rebasing commercialization active-surface claims
- changing `registry/agents.yaml`
- widening the department model

### File allowlist

- `plans/m365-authoritative-persona-registry-and-capability-map-rebase/**`
- `docs/prompts/codex-m365-authoritative-persona-registry-and-capability-map-rebase.md`
- `docs/prompts/codex-m365-authoritative-persona-registry-and-capability-map-rebase-prompt.txt`
- `registry/ai_team.json`
- `registry/persona_registry_v2.yaml`
- `registry/persona_capability_map.yaml`
- `docs/commercialization/m365-persona-registry-v2.md`
- `docs/commercialization/m365-persona-capability-and-risk-map.md`
- `src/ops_adapter/personas.py`
- `scripts/ci/build_persona_registry_v2.py`
- `scripts/ci/verify_persona_registry_v2.py`
- `docs/ma/lemmas/L*_m365_authoritative_persona_registry_rebase_v1.md`
- `invariants/lemmas/L*_m365_authoritative_persona_registry_rebase_v1.yaml`
- `notebooks/m365/INV-M365-*-authoritative-persona-registry-rebase-v1.ipynb`
- `notebooks/lemma_proofs/L*_m365_authoritative_persona_registry_rebase_v1.ipynb`
- `artifacts/scorecards/scorecard_*.json`
- `configs/generated/authoritative_persona_registry_rebase_v1_verification.json`
- `tests/test_persona_registry_v2.py`
- `tests/test_authoritative_persona_registry_rebase_v1.py`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `registry/agents.yaml`
- `registry/activated_persona_surface_v1.yaml`
- `docs/commercialization/m365-activated-persona-surface-v1.md`

## Requirements

- **R1** — Rebase the authoritative roster to `59` named personas across the existing `10` departments.
- **R2** — Rebase the persona registry to `59` total while preserving the pre-H5 active/planned split of `34` / `25`.
- **R3** — Rebase the capability map so the `20` extras are no longer non-authoritative overflow agents.
- **R4** — Keep the promoted personas non-active until H5.
- **R5** — Produce notebook-backed proof, generated verification, and tests.
- **R6** — Commit and push the H3 result before H4 begins.

## Child Acts

### H3A — Authoritative Roster Rebase

- update `registry/ai_team.json` to include all `59` named authoritative personas
- preserve the `10`-department model

### H3B — Persona Registry Rebase

- update `registry/persona_registry_v2.yaml`, builder/verifier, and runtime loader surfaces as needed
- preserve the `34 active / 25 planned` pre-H5 state

### H3C — Capability Map and Validation Rebase

- update `registry/persona_capability_map.yaml`
- remove the `20` extras from the non-authoritative summary
- validate, commit, and push before H4

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-authoritative-persona-registry-and-capability-map-rebase.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-authoritative-persona-registry-and-capability-map-rebase-prompt.txt`

## Validation Strategy

- verify `registry/ai_team.json` totals `59` personas across `10` departments
- verify `registry/persona_registry_v2.yaml` totals `59` personas with `34` active and `25` planned
- verify `registry/persona_capability_map.yaml` shows `0` non-authoritative overflow agents
- verify targeted runtime and verifier tests are green
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

- Do not mark the promoted personas active in H3.
- Do not widen the department model.
- Do not auto-advance to H4.
- Commit and push H3 before any H4 work begins.
