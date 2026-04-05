# MATHS Prompt: M365 Authoritative Persona Registry and Capability-Map Rebase

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-authoritative-persona-registry-and-capability-map-rebase:R1`
- `PARENT_PLAN_ACK: plan:m365-authoritative-persona-humanization-expansion`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Approval and Governance Gates

1. **Present the approval packet first** — summarize the H2 result, the staged `34 active / 25 planned` target, and the exact registry/code write set.
2. **Wait for explicit "go"** — do not begin execution until the operator confirms with "go".
3. **Call MCP `validate_action` before any mutating action** — obey the verdict and stop on red.
4. **Notebook first** — all registry transformation logic must be proven in notebooks first.
5. **Do not auto-advance to H4** — H4 needs its own approval packet and explicit "go".

## MA Hardline Requirements

1. **Phase 0 — Intent definition first** — restate the staged registry-rebase problem, the non-goals, required guarantees, success criteria, and determinism rules in the approval packet before any notebook work begins.
2. **Phases 1 through 4 — Formal proof chain first** — define the governing formula, calculus, lemmas, and executable invariants for the staged `59 / 34 / 25` model before extraction.
3. **Phase 5 — Notebook development only** — model every roster, registry, and capability-map transformation in notebooks first with deterministic assertions.
4. **Phase 6 — Scorecard gate** — require scorecard green before updating authoritative surfaces.
5. **Phase 7 — Extraction parity** — extracted registry and capability-map outputs must mirror the notebook-proven transforms exactly.

## Draft vs Active Semantics

This phase starts in **Draft** status. It transitions to **Active** only after H2 is green and the operator presents the approval packet and receives "go".

## Execution Rules

- Run checks `H3-REGISTRY-REBASE-C0` -> `H3-REGISTRY-REBASE-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:H3-REGISTRY-REBASE STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `H3-REGISTRY-REBASE`
- Run ID: `m365-authoritative-persona-registry-and-capability-map-rebase`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-authoritative-persona-registry-and-capability-map-rebase:R1`
  - `plan:m365-authoritative-persona-registry-and-capability-map-rebase:R2`
  - `plan:m365-authoritative-persona-registry-and-capability-map-rebase:R3`
  - `plan:m365-authoritative-persona-registry-and-capability-map-rebase:R4`
  - `plan:m365-authoritative-persona-registry-and-capability-map-rebase:R5`
  - `plan:m365-authoritative-persona-registry-and-capability-map-rebase:R6`

## Context

- Task name: `Rebase the authoritative roster, persona registry, and capability map`
- Domain: `governance`
- Dependencies:
  - `plans/m365-authoritative-persona-humanized-employee-record-completion/m365-authoritative-persona-humanized-employee-record-completion.md`
  - `registry/ai_team.json`
  - `registry/persona_registry_v2.yaml`
  - `registry/persona_capability_map.yaml`
- Allowlist:
  - `registry/ai_team.json`
  - `registry/persona_registry_v2.yaml`
  - `registry/persona_capability_map.yaml`
  - `src/ops_adapter/personas.py`
  - `scripts/ci/build_persona_registry_v2.py`
  - `scripts/ci/verify_persona_registry_v2.py`
  - `tests/test_persona_registry_v2.py`
  - `notebooks/**`
  - `artifacts/scorecards/**`
- Denylist:
  - `registry/agents.yaml`
  - `registry/activated_persona_surface_v1.yaml`
  - `docs/commercialization/m365-activated-persona-surface-v1.md`

## M - Model

- Problem: `The authoritative roster and capability surfaces still exclude the 20 promoted personas.`
- Goal: `Rebase the three core authoritative surfaces to 59 total personas while keeping the promoted set non-active until H5.`
- Success criteria:
  - `ai_team.json totals 59 personas across 10 departments`
  - `persona_registry_v2.yaml totals 59 with 34 active and 25 planned`
  - `persona_capability_map.yaml clears the 20-agent overflow set`
- Out of scope:
  - `activation`
  - `active-surface commercialization rebase`

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `all three authoritative surfaces are updated`
- Runtime/test evidence:
  - `targeted builder/verifier/tests pass`
- Governance evidence:
  - `Operations/EXECUTION_PLAN.md updated`
  - `Operations/ACTION_LOG.md updated`
  - `Operations/PROJECT_FILE_INDEX.md updated`
- Determinism evidence:
  - `repeated notebook/build steps reproduce the same registry outputs`

## T - Tie

- GO criteria:
  - `59 total personas across all three surfaces`
  - `34 active / 25 planned preserved until H5`
  - `20-agent overflow cleared from capability map summary`
- NO-GO criteria:
  - `any surface still excludes promoted personas`
  - `any promoted persona becomes active in H3`

## H - Harness (ordered checks)

`H3-REGISTRY-REBASE-C0` Preflight
- Verify H2 is green and the governance docs are current.

`H3-REGISTRY-REBASE-C1` Baseline inventory
- Capture current authoritative summaries and overflow counts.

`H3-REGISTRY-REBASE-C2` Notebook roster transform
- Model the `ai_team.json` rebase in notebooks first.

`H3-REGISTRY-REBASE-C3` Notebook registry transform
- Model the `persona_registry_v2.yaml` rebase in notebooks first.

`H3-REGISTRY-REBASE-C4` Notebook capability-map transform
- Model the `persona_capability_map.yaml` rebase in notebooks first.

`H3-REGISTRY-REBASE-C5` Activation separation gate
- Verify promoted personas remain non-active in H3 outputs.

`H3-REGISTRY-REBASE-C6` Execute targeted validations
- Run the targeted builder, verifier, and tests.

`H3-REGISTRY-REBASE-C7` Strict artifact validation
- Fail if any summary count or staged-state rule is inconsistent.

`H3-REGISTRY-REBASE-C8` Deterministic replay
- Repeat the build and require identical outputs.

`H3-REGISTRY-REBASE-C9` Hard gates
1. `git diff --check`
2. `targeted builder/verifier/tests`
3. `scorecard green`

`H3-REGISTRY-REBASE-C10` Governance synchronization and final decision
- Update docs, commit, push, and emit GO/NO-GO.

## Output Contract

- Deliverables:
  - `rebased ai_team.json`
  - `rebased persona_registry_v2.yaml`
  - `rebased persona_capability_map.yaml`
- Validation results:
  - `H3-REGISTRY-REBASE-C0..C10 statuses`
- Evidence links:
  - `file paths and commands only`
- Final decision lines:
  - `GATE:H3-REGISTRY-REBASE STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`
