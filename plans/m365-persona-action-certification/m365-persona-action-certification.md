# Plan: M365 Persona-Action Certification

## Section 1: Plan Header

- **Plan ID:** `plan:m365-persona-action-certification`
- **Parent Plan ID:** `none`
- **Title:** `Certify the full persona-to-action graph so every persona is reachable, every allowed action is mapped, and every orphan or stubbed path is truthfully classified`
- **Version:** `1.0`
- **Status:** `active`
- **Owner:** `SMARTHAUS`
- **Date Created:** `2026-04-07`
- **Date Updated:** `2026-04-07`
- **North Star Ref:** `Operations/NORTHSTAR.md`
- **Execution Plan Ref:** `Operations/EXECUTION_PLAN.md § Initiative: M365 Persona-Action Certification`
- **Domain:** `infrastructure`
- **Math/Algorithm Scope:** `false`

## Section 2: North Star Alignment

- **Source:** `Operations/NORTHSTAR.md`
- **Principles served:**
  - `Truthful M365-only workforce execution through reachable personas`
  - `Fail-closed permission, approval, and routing behavior across the full workforce graph`
  - `Self-service operations with no orphaned or implied action surface`
- **Anti-alignment:**
  - `Does NOT widen into UCP runtime work`
  - `Does NOT count legacy stub behavior as real M365 execution`
  - `Does NOT imply persona capability just because a lower-level direct action exists`

## Section 3: Intent Capture

- **User's stated requirements:**
  - `Test that every single persona can be reached`
  - `Test that the actions each persona can do actually work`
  - `Find any orphan actions that are not talking to any person`
  - `Find any persona actions that are dead, stubbed, or not connected to a real implementation`
- **Intent verification:** `This initiative exists because direct-surface certification is complete, but the workforce graph itself is not yet certified.`

## Section 4: Objective

- **Objective:** Lock and certify the full persona-to-action graph so every persona is either reachable or fenced, every persona action is either mapped to a real execution path or fenced, and the workforce graph contains no unclassified orphan surface.
- **Current state:** The repo now has a truthfully reduced direct support matrix at `155` direct instruction actions with `64` certified green and `91` fenced. But the workforce graph is broader: `59` agents in `registry/agents.yaml`, `184` persona-facing allowed-action aliases, `125` aliases outside the current direct crosswalk, and `41` legacy stub actions across `8` agents in `src/ops_adapter/actions.py`.
- **Target state:** Every persona in the authoritative workforce graph is classified for reachability, every persona-facing action is classified for mapping and execution truth, every orphan action is identified, and the final workforce certification matrix says exactly which persona/action pairs are live-green, approval-gated, fenced, stubbed, or orphaned.

## Section 4A: Current Phase State

- `G0` is complete.
- `G1` is now the active next act.
- The predecessor direct-surface certification initiative is complete.
- The current predecessor artifact is `artifacts/diagnostics/m365_direct_full_surface_certification.json`.
- The current workforce baseline artifact is `artifacts/diagnostics/m365_persona_action_certification.json`.

## Section 5: Scope

### In scope (conceptual)

- lock the authoritative persona-to-action universe from repo truth sources
- prove persona reachability through the governed runtime surfaces
- map every persona-facing action to canonical execution, approval, and executor truth
- identify orphan actions, dead routes, and legacy stubs
- execute workforce certification across unique actions and persona/action paths
- publish a final workforce certification matrix

### Out of scope (conceptual)

- UCP runtime changes
- production release promotion
- silent bypasses of approval, actor identity, or permission enforcement
- counting persona aliases as supported if they remain unmapped, stubbed, or dead

### File allowlist (agent MAY touch these)

- `plans/m365-persona-action-certification/**`
- `docs/prompts/codex-m365-persona-action-certification.md`
- `docs/prompts/codex-m365-persona-action-certification-prompt.txt`
- `docs/commercialization/m365-persona-action-certification.md`
- `artifacts/diagnostics/m365_persona_action_certification.json`
- `registry/agents.yaml`
- `registry/ai_team.json`
- `registry/persona_registry_v2.yaml`
- `registry/persona_capability_map.yaml`
- `registry/capability_registry.yaml`
- `registry/auth_model_v2.yaml`
- `registry/approval_risk_matrix_v2.yaml`
- `registry/executor_routing_v2.yaml`
- `registry/*_expansion_v2.yaml`
- `registry/cross_workload_automation_recipes_v2.yaml`
- `src/provisioning_api/routers/m365.py`
- `src/ops_adapter/main.py`
- `src/ops_adapter/app.py`
- `src/ops_adapter/actions.py`
- `src/ops_adapter/personas.py`
- `src/smarthaus_common/executor_routing.py`
- `src/smarthaus_common/approval_risk.py`
- `tests/test_ops_adapter.py`
- `tests/test_executor_routing_v2.py`
- `tests/test_auth_model_v2.py`
- `tests/test_approval_risk_v2.py`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist (agent MUST NOT touch these)

- `../UCP/**`
- `Any path not listed in the allowlist`

### Scope fence rule

Stop and re-scope if truthful workforce certification requires UCP-side edits or undocumented tenant changes outside the repo-local runtime and documented local operator tooling.

## Section 6: Requirements

- **R0 — Create the governed persona-to-action certification package**
  - Create the bounded plan triplet, prompt pair, and tracker activation before any new workforce certification work.
- **R1 — Lock the workforce graph**
  - Freeze the persona universe, persona-facing action universe, canonical action mappings, approval/risk bindings, and executor-routing truth from repo sources.
- **R2 — Certify persona reachability**
  - Prove every persona is reachable through the governed runtime or explicitly fence unreachable personas with reasons.
- **R3 — Certify mapping completeness**
  - Classify every persona-facing action as mapped, orphaned, dead-routed, legacy-stubbed, or fenced for another explicit reason.
- **R4 — Certify execution truth**
  - Reuse unique-action execution proofs where valid, and run additional live persona/action probes where persona routing, approval, or actor-tier behavior materially differs.
- **R5 — Repair repo-local defects or reduce the claimed workforce surface**
  - Any repo-local defect exposed by workforce certification must be fixed and rerun; any action or persona path that cannot be made truthful must be fenced.
- **R6 — Publish the final workforce certification matrix**
  - Close the initiative only when every persona and every persona-facing action is classified with written evidence.

## Section 7: Execution Sequence

- `G0 -> G1 -> G2 -> G3 -> G4 -> G5`
- Stop on first red that escapes the allowlist or requires unsafe/undocumented tenant changes.

## Section 8: Phases

- **G0 — Workforce graph lock**
  - Freeze the persona universe, persona-facing action universe, and predecessor direct-support matrix.
- **G1 — Persona reachability certification**
  - Prove which personas are actually reachable through the governed runtime surfaces.
- **G2 — Mapping / orphan / stub audit**
  - Classify every persona-facing action as mapped, orphaned, dead-routed, legacy-stubbed, or fenced.
- **G3 — Unique action execution certification reuse**
  - Reuse completed direct-surface evidence where valid and identify the remaining unique actions that still need live proof.
- **G4 — Persona/action certification**
  - Certify persona/action execution, approval, and actor-tier behavior across the workforce graph.
- **G5 — Closeout**
  - Publish the final workforce certification matrix and governance closeout.

## Section 9: Gates

- **CHECK:C0 — Package and tracker truth locked**
  - The plan, prompt pair, and tracker state must exist before workforce certification begins.
- **CHECK:C1 — Workforce graph frozen**
  - The persona and persona-action universes must be frozen before reachability or mapping claims.
- **CHECK:C2 — Reachability truth published**
  - Every persona must be classified as reachable or fenced.
- **CHECK:C3 — Mapping truth published**
  - Every persona-facing action must be classified as mapped, orphaned, dead-routed, stubbed, or fenced.
- **CHECK:C4 — Execution truth published**
  - Every unique action and every material persona/action path must be classified as green, approval-gated, permission-blocked, tenant-blocked, stubbed, or fenced.
- **CHECK:C5 — Final workforce matrix published**
  - The initiative closes only with a complete workforce certification matrix and machine-readable artifact.

## Section 10: Artifacts

- `plans/m365-persona-action-certification/m365-persona-action-certification.md`
- `plans/m365-persona-action-certification/m365-persona-action-certification.yaml`
- `plans/m365-persona-action-certification/m365-persona-action-certification.json`
- `docs/prompts/codex-m365-persona-action-certification.md`
- `docs/prompts/codex-m365-persona-action-certification-prompt.txt`
- `docs/commercialization/m365-persona-action-certification.md`
- `artifacts/diagnostics/m365_persona_action_certification.json`

## Section 11: Current Result

- `R0` is complete.
- `G0` is complete.
- The frozen workforce baseline now records:
  - `59` agents
  - `59` authoritative personas
  - `184` persona-facing allowed-action aliases
  - `41` approval rules
  - `5` contract-only personas
  - `8` known stub agents with `46` currently attached actions
- The predecessor direct-surface certification remains locked at:
  - `155` direct instruction actions
  - `64` certified live-green direct actions
  - `91` fenced direct actions
- `G0` also froze the current candidate mismatch zones:
  - `2` exact-name overlaps between persona aliases and direct instruction actions
  - `182` persona aliases without an exact direct-action name match
  - `153` direct instruction actions without an exact persona-alias name match
- No reachability, orphan, or final execution classification has been claimed yet under this package.
- `G1` persona reachability certification is the next act.
