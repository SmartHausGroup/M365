# Plan: M365 Authoritative Persona H4 Scope Correction

**Plan ID:** `m365-authoritative-persona-h4-scope-correction`
**Parent Plan ID:** `m365-authoritative-persona-humanization-expansion`
**Status:** 🟢 Complete
**Date:** 2026-04-05
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-authoritative-persona-h4-scope-correction:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — keep certification truth aligned with the real authority surfaces and fail closed when department-pack contracts still encode stale `39`-persona counts after the H3 authoritative rebase.
**Canonical predecessor:** `plans/m365-authoritative-persona-registry-and-capability-map-rebase/m365-authoritative-persona-registry-and-capability-map-rebase.md`

**Draft vs Active semantics:** This child plan starts in **Draft**. It transitions to **Active** only when (1) H3 is green, (2) the operator presents the approval packet and receives explicit "go", and (3) no other child phase under the parent initiative is concurrently active. It transitions to **Complete** only after its own gate emits GO, the phase is committed, and the branch is pushed.

**Approval and governance gates:** Before execution, present the approval packet and wait for explicit "go". During execution, call MCP `validate_action` before every mutating action and obey the verdict. Stop on first red. Do not auto-advance to H4.

**Notebook-first discipline:** H4S is a notebook-backed department-pack authority rebase phase. All staged count reconciliation, pack-boundary updates, and pack-state assertions must be derived and verified in notebooks first. No direct extraction into the department-pack authorities is allowed before scorecard green.

## Objective

Create the formal blocker phase that rebases the `registry/department_pack_*_v1.yaml` authority surface and the corresponding department-pack commercialization and test surfaces to the post-H3 staged `59`-persona authoritative truth before H4 certification/count rebase can continue.

## Decision Rule

`DependencyProofEstablished = verify_department_certification_v1.py joins department_certification_v1.yaml, department_pack_*_v1.yaml, and persona_registry_v2.yaml`

`ScopeGapEstablished = H4 as currently defined excludes department_pack_*_v1.yaml and the related pack docs/tests even though those surfaces still encode the old 39-persona distribution`

`DepartmentPackRebaseDefined = a governed blocker phase owns the department-pack authority rebase across all 10 departments before H4 resumes`

`H4S_GO = H3_GO AND DependencyProofEstablished AND ScopeGapEstablished AND DepartmentPackRebaseDefined`

If `H4S_GO` is false, H4S must emit `NO-GO`, stop, and keep H4 blocked.

## Scope

### In scope

- prove the H4 dependency on the department-pack authority surface explicitly
- rebase `registry/department_pack_*_v1.yaml` to the staged post-H3 authoritative counts
- rebase the corresponding `docs/commercialization/m365-*-department-pack-v1.md` contracts
- rebase the corresponding `tests/test_*_department_pack_v1.py` pack assertions and any targeted department-pack verifier surfaces required for the truthful staged model
- produce notebook-backed proof, generated verification output, and targeted pack validation
- unblock H4 only after the department-pack authority surface is green, committed, and pushed

### Out of scope

- rebasing `registry/persona_certification_v1.yaml`
- rebasing `registry/department_certification_v1.yaml`
- rebasing `registry/enterprise_release_gate_v2.yaml`
- activating promoted personas
- rebasing final active-surface commercialization truth
- changing `registry/agents.yaml`

### File allowlist

- `plans/m365-authoritative-persona-h4-scope-correction/**`
- `docs/prompts/codex-m365-authoritative-persona-h4-scope-correction.md`
- `docs/prompts/codex-m365-authoritative-persona-h4-scope-correction-prompt.txt`
- `registry/department_pack_*_v1.yaml`
- `docs/commercialization/m365-*-department-pack-v1.md`
- `scripts/ci/verify_*_department_pack_v1.py`
- `tests/test_*_department_pack_v1.py`
- `docs/ma/lemmas/L*_m365_authoritative_persona_department_pack_rebase_v1.md`
- `invariants/lemmas/L*_m365_authoritative_persona_department_pack_rebase_v1.yaml`
- `notebooks/m365/INV-M365-*-authoritative-persona-department-pack-rebase-v1.ipynb`
- `notebooks/lemma_proofs/L*_m365_authoritative_persona_department_pack_rebase_v1.ipynb`
- `artifacts/scorecards/scorecard_*.json`
- `configs/generated/authoritative_persona_department_pack_rebase_v1_verification.json`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `registry/persona_certification_v1.yaml`
- `registry/department_certification_v1.yaml`
- `registry/enterprise_release_gate_v2.yaml`
- `docs/commercialization/m365-persona-certification-v1.md`
- `docs/commercialization/m365-department-certification-v1.md`
- `docs/commercialization/m365-enterprise-release-gate-v2.md`
- `registry/activated_persona_surface_v1.yaml`
- `docs/commercialization/m365-activated-persona-surface-v1.md`
- `registry/agents.yaml`

## Requirements

- **R1** — Make the H4 dependency and scope gap explicit from live repo truth.
- **R2** — Rebase all `10` department-pack authority files to the staged post-H3 authoritative counts.
- **R3** — Rebase the corresponding department-pack commercialization contracts.
- **R4** — Rebase the corresponding department-pack tests and targeted verifier surfaces.
- **R5** — Produce notebook-backed proof, generated verification output, and targeted validation.
- **R6** — Keep H4 blocked until H4S is green, committed, and pushed.
- **R7** — Commit and push H4S before H4 begins.

## Child Acts

### H4SA — Dependency and mismatch proof

- prove the current H4 `NO-GO` root cause from live department-pack vs registry counts

### H4SB — Department-pack authority rebase

- update the `10` department-pack authority contracts to the post-H3 staged authoritative truth

### H4SC — Pack validation and H4 unblock

- update targeted pack docs/tests/verifiers
- validate, commit, and push before H4 resumes

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-authoritative-persona-h4-scope-correction.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-authoritative-persona-h4-scope-correction-prompt.txt`

## Validation Strategy

- verify every rebased department pack agrees with the staged post-H3 department counts in `persona_registry_v2.yaml`
- verify no rebased pack over-claims active or registry-backed personas beyond the staged authoritative truth
- verify targeted department-pack tests and verifiers are green
- verify H4 remains blocked until H4S closes
- run `git diff --check`

## Governance Closure

- [x] `Operations/ACTION_LOG.md`
- [x] `Operations/EXECUTION_PLAN.md`
- [x] `Operations/PROJECT_FILE_INDEX.md`
- [x] This child plan `status -> complete`

## Execution Outcome

- **Decision:** `GO`
- **Approved by:** `operator explicit go`
- **Completion timestamp:** `2026-04-05 09:17:05 EDT`

## Agent Constraints

- Do not edit the certification contracts in H4S.
- Do not claim final activation in H4S.
- Do not auto-advance to H4.
- Commit and push H4S before any H4 work begins.
