# Plan: M365 Authoritative Persona Certification and Count Rebase

**Plan ID:** `m365-authoritative-persona-certification-and-count-rebase`
**Parent Plan ID:** `m365-authoritative-persona-humanization-expansion`
**Status:** 🟢 Complete
**Date:** 2026-04-05
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-authoritative-persona-certification-and-count-rebase:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — keep certification, census, and commercialization truth aligned with the authoritative workforce state instead of leaving stale `39` / `34` claims in place after the registry rebase.
**Canonical predecessor:** `plans/m365-authoritative-persona-h4-scope-correction/m365-authoritative-persona-h4-scope-correction.md`

**Draft vs Active semantics:** This child plan starts in **Draft**. It transitions to **Active** only when (1) H4S is green and pushed, (2) the operator presents the approval packet and receives explicit "go", and (3) no other child phase under the parent initiative is concurrently active. It transitions to **Complete** only after its own gate emits GO, the phase is committed, and the branch is pushed.

**Approval and governance gates:** Before execution, present the approval packet and wait for explicit "go". During execution, call MCP `validate_action` before every mutating action and obey the verdict. Stop on first red. Do not auto-advance to H5.

**Notebook-first discipline:** H4 is a notebook-backed certification and count-truth phase. All count reconciliations, staged-state truth assertions, and certification updates must be derived and verified in notebooks first. No direct count-surface extraction is allowed before scorecard green.

## Objective

Rebase the certification and count surfaces to the truthful post-H4S pre-H5 state: `59` total authoritative personas across `10` departments, `34` active personas, and `25` planned personas, with no stale `39`-persona authoritative claims remaining in the scoped certification surfaces.

## Decision Rule

`CountTruthConsistent = All scoped artifacts agree on total authoritative personas = 59 and total departments = 10`

`PreActivationTruthConsistent = All scoped artifacts agree on active personas = 34 and planned personas = 25 until H5 closes the activation gate`

`CertificationSurfacesGreen = all scoped certification and commercialization artifacts pass their targeted verifiers and tests`

`H4_GO = H3_GO AND CountTruthConsistent AND PreActivationTruthConsistent AND CertificationSurfacesGreen`

If `H4_GO` is false, H4 must emit `NO-GO`, stop, and keep the certification/count truth at the prior proven state.

## Scope

### In scope

- update count and certification surfaces that still assert `39` total authoritative personas
- rebase the department census, persona-certification, department-certification, and persona-registry documentation to the truthful pre-H5 staged state
- update verifier scripts and tests that enforce the old count model
- create notebook-backed proof and generated verification output for the rebased count/certification state

### Out of scope

- activating the `20` promoted personas
- rebasing the final active-surface commercialization boundary
- changing `registry/agents.yaml`
- widening the department model

### File allowlist

- `plans/m365-authoritative-persona-certification-and-count-rebase/**`
- `docs/prompts/codex-m365-authoritative-persona-certification-and-count-rebase.md`
- `docs/prompts/codex-m365-authoritative-persona-certification-and-count-rebase-prompt.txt`
- `registry/persona_certification_v1.yaml`
- `registry/department_certification_v1.yaml`
- `registry/enterprise_release_gate_v2.yaml`
- `docs/commercialization/m365-persona-certification-v1.md`
- `docs/commercialization/m365-department-certification-v1.md`
- `docs/commercialization/m365-persona-registry-v2.md`
- `docs/commercialization/m365-department-persona-census.md`
- `docs/commercialization/m365-enterprise-release-gate-v2.md`
- `scripts/ci/verify_persona_certification_v1.py`
- `scripts/ci/verify_department_certification_v1.py`
- `tests/test_persona_certification_v1.py`
- `tests/test_department_certification_v1.py`
- `tests/test_persona_registry_v2.py`
- `docs/ma/lemmas/L*_m365_authoritative_persona_certification_count_rebase_v1.md`
- `invariants/lemmas/L*_m365_authoritative_persona_certification_count_rebase_v1.yaml`
- `notebooks/m365/INV-M365-*-authoritative-persona-certification-count-rebase-v1.ipynb`
- `notebooks/lemma_proofs/L*_m365_authoritative_persona_certification_count_rebase_v1.ipynb`
- `artifacts/scorecards/scorecard_*.json`
- `configs/generated/authoritative_persona_certification_count_rebase_v1_verification.json`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `registry/activated_persona_surface_v1.yaml`
- `docs/commercialization/m365-activated-persona-surface-v1.md`
- `registry/workforce_packaging_v1.yaml`
- `registry/agents.yaml`

## Requirements

- **R1** — Rebase authoritative total counts from `39` to `59`.
- **R2** — Rebase the pre-H5 staged active/planned counts to `34` / `25`.
- **R3** — Update certification and commercialization documents that enforce the old count model.
- **R4** — Update verifier scripts and tests for the new staged truth.
- **R5** — Produce notebook-backed proof and generated verification output.
- **R6** — Commit and push H4 before H5 begins.

## Child Acts

### H4A — Certification Contract Rebase

- update persona and department certification contracts to the `59`-persona authoritative truth

### H4B — Census and Commercialization Truth Rebase

- update the human-readable census and certification docs to the pre-H5 staged counts

### H4C — Verifier and Test Rebase

- update targeted verifiers and tests
- validate, commit, and push before H5

## Prompt References

- **Detailed prompt:** `docs/prompts/codex-m365-authoritative-persona-certification-and-count-rebase.md`
- **Kickoff prompt:** `docs/prompts/codex-m365-authoritative-persona-certification-and-count-rebase-prompt.txt`

## Validation Strategy

- verify all scoped count/certification surfaces agree on `59 total / 10 departments / 34 active / 25 planned`
- verify targeted verifiers and tests are green
- verify no active-surface files were changed in H4
- run `git diff --check`

## Governance Closure

- [x] `Operations/ACTION_LOG.md`
- [x] `Operations/EXECUTION_PLAN.md`
- [x] `Operations/PROJECT_FILE_INDEX.md`
- [x] This child plan `status -> complete`

## Execution Outcome

- **Decision:** `GO`
- **Approved by:** `operator-explicit-go`
- **Completion timestamp:** `2026-04-05 09:36:56 EDT`

## Agent Constraints

- Do not activate promoted personas in H4.
- Do not modify the final active-surface artifacts in H4.
- Do not auto-advance to H5.
- Commit and push H4 before any H5 work begins.
