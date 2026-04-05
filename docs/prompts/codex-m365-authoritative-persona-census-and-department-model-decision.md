# MATHS Prompt: M365 Authoritative Persona Census and Department-Model Decision

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-authoritative-persona-census-and-department-model-decision:R1`
- `PARENT_PLAN_ACK: plan:m365-authoritative-persona-humanization-expansion`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Approval and Governance Gates

1. **Present the approval packet first** — before executing any check, present the H1 recommendation, the projected department counts, the stop condition, and the intended write surface to the operator.
2. **Wait for explicit "go"** — do not begin execution until the operator confirms with "go" in the chat interface.
3. **Call MCP `validate_action` before any mutating action** — before writing, editing, or creating any file, call `validate_action` and obey the verdict. If the verdict is not `allowed`, stop immediately.
4. **Stop on first red** — if any check emits `FAIL` or `BLOCKED`, stop the entire phase. Do not continue to subsequent checks.
5. **Do not auto-advance to H2** — even if H1 emits GO, H2 requires its own approval packet and explicit "go".

## Draft vs Active Semantics

This phase starts in **Draft** status. It transitions to **Active** only after the operator presents the approval packet and receives "go". The parent initiative can be Active while this phase remains Draft.

## Predecessor Authority

The canonical predecessor for this child phase is `plans/m365-authoritative-persona-humanization-expansion/m365-authoritative-persona-humanization-expansion.md`. H1 is the first execution phase under that parent initiative.

## Approval Packet Template

Use this exact structure before execution:

1. `Decision Summary`
2. `Options Considered`
3. `Evaluation Criteria`
4. `Why This Choice`
5. `Risks`
6. `Next Steps`

The default H1 recommendation is: preserve the current `10`-department model, accept the proposed remap of the `20` extras into the existing department set, and stop immediately if any evidence forces an eleventh department or breaks the projected `59`-persona total.

## Execution Rules

- Run checks `H1-CENSUS-DECISION-C0` -> `H1-CENSUS-DECISION-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:H1-CENSUS-DECISION STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `H1-CENSUS-DECISION`
- Run ID: `m365-authoritative-persona-census-and-department-model-decision`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-authoritative-persona-census-and-department-model-decision:R1`
  - `plan:m365-authoritative-persona-census-and-department-model-decision:R2`
  - `plan:m365-authoritative-persona-census-and-department-model-decision:R3`
  - `plan:m365-authoritative-persona-census-and-department-model-decision:R4`
  - `plan:m365-authoritative-persona-census-and-department-model-decision:R5`
  - `plan:m365-authoritative-persona-census-and-department-model-decision:R6`
  - `plan:m365-authoritative-persona-census-and-department-model-decision:T1`
  - `plan:m365-authoritative-persona-census-and-department-model-decision:T2`
  - `plan:m365-authoritative-persona-census-and-department-model-decision:T3`
  - `plan:m365-authoritative-persona-census-and-department-model-decision:T4`
  - `plan:m365-authoritative-persona-census-and-department-model-decision:T5`

## Context

- Task name: `Lock the authoritative persona census rebase contract and department-model decision`
- Domain: `governance`
- Dependencies:
  - `plans/m365-authoritative-persona-humanization-expansion/m365-authoritative-persona-humanization-expansion.md`
  - `registry/agents.yaml`
  - `registry/ai_team.json`
  - `registry/persona_registry_v2.yaml`
  - `docs/commercialization/m365-department-persona-census.md`
- Allowlist:
  - `plans/m365-authoritative-persona-census-and-department-model-decision/**`
  - `docs/prompts/codex-m365-authoritative-persona-census-and-department-model-decision.md`
  - `docs/prompts/codex-m365-authoritative-persona-census-and-department-model-decision-prompt.txt`
  - `docs/commercialization/m365-authoritative-persona-census-and-department-model-decision.md`
  - `artifacts/diagnostics/m365_authoritative_persona_census_and_department_model_decision.json`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
- Denylist:
  - `registry/ai_team.json`
  - `registry/persona_registry_v2.yaml`
  - `registry/persona_capability_map.yaml`
  - `registry/agents.yaml`
  - `src/**`
  - `tests/**`
  - `Operations/NORTHSTAR.md`

## M - Model

- Problem: `The authoritative roster still claims 39 personas across 10 departments while 20 extra runtime agents remain outside the named authoritative census.`
- Goal: `Determine whether those 20 extras can be promoted without widening the existing department model.`
- Success criteria:
  - `The current 39/10/59/20 baseline is explicit.`
  - `Every one of the 20 extras is mapped to an existing department or H1 emits NO-GO.`
  - `Projected department counts reconcile to 59 personas across 10 departments.`

## A - Annotate

Required measurable evidence:

- Baseline evidence:
  - `runtime count = 59`
  - `authoritative roster count = 39`
  - `active authoritative count = 34`
  - `current department count = 10`
- Decision evidence:
  - `20-persona mapping matrix exists`
  - `projected department-count table exists`
  - `projected total = 59`
  - `projected distinct departments = 10`
- Governance evidence:
  - `decision doc exists`
  - `diagnostics artifact exists`
  - `Operations/EXECUTION_PLAN.md updated`
  - `Operations/ACTION_LOG.md updated`
  - `Operations/PROJECT_FILE_INDEX.md updated`

## T - Tie

- Dependency ties:
  - `H2 through H5 remain blocked until H1 emits GO.`
  - `If H1 emits NO-GO, the next required action is a separate governed department-model change, not roster rebase work.`
- Known failure modes:
  - `An extra agent needs an eleventh department.`
  - `Projected counts do not reconcile to 59.`
  - `H1 drifts into registry edits or activation work.`
- GO criteria:
  - `All 20 extras map into existing departments and projected counts remain 59 across 10 departments.`
- NO-GO criteria:
  - `Any extra persona cannot be placed cleanly, or H1 requires changing the department model.`

## H - Harness (ordered checks)

`H1-CENSUS-DECISION-C0` Preflight
- Read AGENTS, rules, North Star, execution plan, action log, parent plan, child plan, parent prompt, and `docs/governance/MATHS_PROMPT_TEMPLATE.md`.

`H1-CENSUS-DECISION-C1` Baseline inventory
- Confirm the current `59` runtime agents, `39` authoritative personas, `34` active authoritative personas, and `10` departments.

`H1-CENSUS-DECISION-C2` Department-set lock
- Enumerate the current authoritative department set and forbid any new department in this phase.

`H1-CENSUS-DECISION-C3` Persona mapping matrix
- Evaluate and document all `20` planned persona placements against the current department set.

`H1-CENSUS-DECISION-C4` Projection reconciliation
- Compute the projected authoritative department counts and require a total of `59` across `10` departments.

`H1-CENSUS-DECISION-C5` Decision doc and diagnostics artifact
- Write the bounded decision doc and diagnostics artifact with `GO` or `NO-GO`.

`H1-CENSUS-DECISION-C6` Governance synchronization
- Update the execution plan, action log, and project file index for the H1 outcome.

`H1-CENSUS-DECISION-C7` Targeted validations
- Validate that every mapped persona lands in an existing department and no registry files changed.

`H1-CENSUS-DECISION-C8` Strict artifact validation
- Fail if the decision doc omits the baseline, mapping matrix, projected counts, or stop condition.

`H1-CENSUS-DECISION-C9` Hard gates (strict order)
1. `artifact and plan readback`
2. `file-index and governance readback`
3. `git diff --check`

`H1-CENSUS-DECISION-C10` Final decision
- Emit the explicit `GO` or `NO-GO` lines and stop.

## S - Stress-test

- Adversarial checks:
  - `If H1 edits registry or runtime files, fail.`
  - `If H1 silently creates an eleventh department, fail.`
  - `If any of the 20 extras remain unmapped, fail.`
- Replay checks:
  - `Rereading the artifacts must reproduce the same baseline counts, projected counts, and final decision.`

## Output Contract

- Deliverables:
  - `H1 decision doc`
  - `H1 diagnostics artifact`
  - `projected department-count table`
  - `explicit GO/NO-GO decision`
- Validation results:
  - `H1-CENSUS-DECISION-C0..C10 statuses`
- Evidence links:
  - `file paths and commands only`
- Residual risks:
  - `one-line truthful note if any ambiguity remains`
- Final decision lines:
  - `GATE:H1-CENSUS-DECISION STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Any attempt to widen the department model inside H1.
- Any attempt to edit registry or runtime authority files in H1.
- Any mismatch between the projected department counts and the claimed total of `59`.
- Any unmapped extra persona.
