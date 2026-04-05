# Plan: M365 authoritative persona humanization expansion

## Section 1: Plan Header

- **Plan Slug:** `m365-authoritative-persona-humanization-expansion`
- **Plan ID:** `plan:m365-authoritative-persona-humanization-expansion`
- **Parent Plan ID:** `plan:m365-post-expansion-promotion-and-persona-activation`
- **Title:** `Promote all 20 extra agents into named digital employees through a governed census rebase`
- **Version:** `1.2`
- **Status:** `active`
- **Owner:** `SMARTHAUS`
- **Date Created:** `2026-04-03`
- **Date Updated:** `2026-04-05`
- **North Star Ref:** `Operations/NORTHSTAR.md`
- **Execution Plan Ref:** `Operations/EXECUTION_PLAN.md § Initiative: Authoritative Persona Humanization Expansion`
- **Domain:** `governance`
- **Math/Algorithm Scope:** `false`

## Section 2: North Star Alignment

- **Source:** `Operations/NORTHSTAR.md`
- **Principles served:**
  - `truthful authoritative workforce governance instead of silent runtime expansion`
  - `department-based organization preserved unless a later explicit governed change says otherwise`
  - `policy-gated, auditable, fail-closed persona activation rules`
- **Anti-alignment:**
  - `Does NOT silently claim the current 39-persona / 10-department North Star is already rebased to 59`
  - `Does NOT add freeform personality schema`
  - `Does NOT activate any new persona in runtime during this planning slice`

## Section 3: Current-State Truth

- `development` was clean before this task and no pre-branch commit or push was required.
- `registry/agents.yaml` currently contains `59` total agent definitions.
- `registry/ai_team.json` currently contains `39` named authoritative personas.
- `registry/persona_registry_v2.yaml` is currently locked to `39` total personas and `34` active personas.
- There is no existing execution-plan item governing an authoritative named-roster expansion from `39` to `59`.
- Therefore the correct move in this slice is to create a new governed plan package, not to patch runtime authorities directly.

## Section 4: Objective

- **Objective:** define the formal governed path for promoting all `20` currently extra non-authoritative agents into named digital employees with bounded personality-style metadata and rebased authoritative census truth.
- **Current state:** the repo already carries `59` runtime agent definitions, but only `39` are currently authoritative named personas and only `34` are active in `registry/persona_registry_v2.yaml`.
- **Target state:** a future approved implementation can rebase the authoritative roster, persona registry, capability map, certification counts, and activation gates so all `20` extras become named digital employees without ambiguity or over-claiming.

## Section 5: Decision Summary

- **Recommended path:** keep the current `10`-department North Star by default and remap the `20` extra agents into those departments unless H1 proves a remap is impossible without distortion.
- **Metadata contract:** use bounded fields `working_style`, `communication_style`, and `decision_style`; reject freeform personality blobs.
- **Activation rule:** no promoted persona may become `active` until it has a real name, title, department placement, manager, escalation owner, capability-map coverage, authoritative registry entry, and rebased certification/count truth.

### Options considered

- **Option A:** remap the `20` extras into the existing `10` departments and rebase the authoritative census.
  - **Pros:** preserves current North Star claims, minimizes governance drift, and avoids needless department proliferation.
  - **Cons:** some personas may need careful department placement decisions.
- **Option B:** expand the department model at the same time as the persona census.
  - **Pros:** allows a cleaner semantic grouping for some extras.
  - **Cons:** widens the change boundary from persona humanization into North Star and operating-model change.
- **Option C:** add a broader freeform personality schema while rebasing the census.
  - **Pros:** maximal expressive flexibility.
  - **Cons:** weakens determinism, complicates validation, and adds unnecessary governance surface.

### Chosen path

- **Chosen:** `Option A`
- **Why:** the current North Star still states `39` personas across `10` departments. The least-risk truthful path is to preserve that structure by default, reopen the authoritative census deliberately, and require a separate governed stop if department expansion becomes necessary.

### Architectural Complexity Warning

- **Warning:** expanding both the authoritative census and the department model while also introducing freeform personality schema would materially increase governance complexity without improving fail-closed guarantees.
- **Simpler approach:** preserve the `10`-department model by default and use only bounded humanization metadata fields in the first implementation pass.

## Section 6: Scope

### In scope (current planning slice)

- create the approved feature branch for this governed planning package
- create the formal plan triplet in Markdown, YAML, and JSON
- create the remaining H2 through H5 child-phase plan triplets in Markdown, YAML, and JSON
- create additional blocker child-phase packages if later governed `NO-GO` evidence proves an execution-scope gap
- create the required prompt pairs for the governed child-phase execution packages
- update `Operations/EXECUTION_PLAN.md`, `Operations/PROJECT_FILE_INDEX.md`, and `Operations/ACTION_LOG.md`
- accept formatter-only normalization in `tests/test_authoritative_persona_registry_rebase_v1.py` if the mandatory repo gate requires it for H4S package closeout
- repair the bounded mandatory pre-commit remediation set in `tests/test_ucp_m365_pack_contracts.py` and `tests/test_ucp_m365_pack_client.py` if it prevents `R5` closeout
- define the future implementation requirements for census rebase, metadata contract, registry rebase, count rebase, and fail-closed activation

### Out of scope (current planning slice)

- editing `registry/ai_team.json`
- editing `registry/persona_registry_v2.yaml`
- editing `registry/persona_capability_map.yaml`
- editing `registry/agents.yaml`
- changing any runtime router, approval, audit, or activation code
- claiming the `20` extra agents are already authoritative or active
- changing the North Star department model without separate approval
- changing any other test or runtime file beyond the bounded pre-commit remediation set

### File allowlist (agent MAY touch in this slice)

- `plans/m365-authoritative-persona-humanization-expansion/**`
- `docs/prompts/codex-m365-authoritative-persona-humanization-expansion.md`
- `docs/prompts/codex-m365-authoritative-persona-humanization-expansion-prompt.txt`
- `plans/m365-authoritative-persona-humanized-employee-record-completion/**`
- `docs/prompts/codex-m365-authoritative-persona-humanized-employee-record-completion.md`
- `docs/prompts/codex-m365-authoritative-persona-humanized-employee-record-completion-prompt.txt`
- `plans/m365-authoritative-persona-registry-and-capability-map-rebase/**`
- `docs/prompts/codex-m365-authoritative-persona-registry-and-capability-map-rebase.md`
- `docs/prompts/codex-m365-authoritative-persona-registry-and-capability-map-rebase-prompt.txt`
- `plans/m365-authoritative-persona-h4-scope-correction/**`
- `docs/prompts/codex-m365-authoritative-persona-h4-scope-correction.md`
- `docs/prompts/codex-m365-authoritative-persona-h4-scope-correction-prompt.txt`
- `plans/m365-authoritative-persona-certification-and-count-rebase/**`
- `docs/prompts/codex-m365-authoritative-persona-certification-and-count-rebase.md`
- `docs/prompts/codex-m365-authoritative-persona-certification-and-count-rebase-prompt.txt`
- `plans/m365-authoritative-persona-activation-gate-closeout/**`
- `docs/prompts/codex-m365-authoritative-persona-activation-gate-closeout.md`
- `docs/prompts/codex-m365-authoritative-persona-activation-gate-closeout-prompt.txt`
- `Operations/EXECUTION_PLAN.md`
- `Operations/PROJECT_FILE_INDEX.md`
- `Operations/ACTION_LOG.md`
- `tests/test_authoritative_persona_registry_rebase_v1.py`
- `tests/test_ucp_m365_pack_contracts.py`
- `tests/test_ucp_m365_pack_client.py`

### File denylist (agent MUST NOT touch in this slice)

- `registry/ai_team.json`
- `registry/persona_registry_v2.yaml`
- `registry/persona_capability_map.yaml`
- `registry/agents.yaml`
- `src/**`
- `tests/**`
- `Any path not listed in the allowlist`

### Scope fence rule

Stop and re-scope if the work expands beyond branch creation, planning artifacts, prompt artifacts, or tracker synchronization.

### Execution-phase discipline

- the parent initiative may remain `active`, but child phases `H1` through `H5` plus blocker phase `H4S` start in `draft` and must run strictly one at a time
- `H2`, `H3`, `H4S`, `H4`, and `H5` are notebook-first / MA-first phases; all iteration must occur in notebooks first before any runtime, registry, verifier, or documentation extraction
- `H2`, `H3`, `H4S`, `H4`, and `H5` must explicitly follow MA phases `0` through `7`; phase `0` intent definition must be restated in the approval packet and approved before any notebook or extraction work begins
- no phase may advance until the predecessor phase is green, committed, and pushed
- each child phase requires its own approval packet, explicit `go`, full validation, commit, and push before the next child phase begins

## Section 7: Requirements

- **R0 — Current-state acknowledgment**
  - Explicitly record that the repo was already clean on `development`, `registry/agents.yaml` already contains `59` agents, `registry/ai_team.json` remains authoritative at `39`, and `registry/persona_registry_v2.yaml` remains locked at `39` total / `34` active.
- **R1 — Branch creation and governance validation**
  - Create `codex/m365-authoritative-persona-humanization-expansion-plan` only after governance validation is green.
- **R2 — Plan artifact creation**
  - Create the Markdown, YAML, and JSON artifacts for the parent initiative and the remaining child-phase packages required to complete the governed execution stack.
- **R3 — Prompt-pair creation**
  - Create the required detailed prompt plus kickoff prompt for each newly created child-phase execution package.
- **R4 — Tracker synchronization**
  - Update `Operations/EXECUTION_PLAN.md`, `Operations/PROJECT_FILE_INDEX.md`, and `Operations/ACTION_LOG.md`.
- **R5 — Commit and push branch**
  - Commit this planning package and push the approved feature branch after resolving any mandatory pre-commit blocker limited to `tests/test_ucp_m365_pack_contracts.py` plus the formatter-only import normalization in `tests/test_ucp_m365_pack_client.py`.
- **R6 — Authoritative census rebase contract**
  - Define the future work required to reopen the authoritative persona census from `39` to `59` without silently changing truth in this slice.
- **R7 — Department-model decision gate**
  - Require the future implementation to preserve the current `10`-department model by default or stop for a separate governed department-model change.
- **R8 — Bounded humanization metadata**
  - Require future humanization metadata to stay bounded to `working_style`, `communication_style`, and `decision_style`.
- **R9 — Registry and certification rebase set**
  - Require future implementation coverage for authoritative roster updates, capability-map updates, persona-registry rebase, and certification/count rebase.
- **R10 — Fail-closed activation gate**
  - Require that no promoted persona may be marked active unless it has a name, title, manager, escalation owner, capability-map entry, and authoritative registry entry.

## Section 8: Execution Sequence

- `T1 -> T2 -> T3 -> T4 -> T5 -> T6`
- Stop on first red.

## Section 9: Planning Tasks

- **T1 — Lock current-state truth and create the branch**
  - Confirm the clean starting point on `development`, validate governance, and create the approved feature branch.
- **T2 — Publish the governed plan triplet**
  - Create the Markdown, YAML, and JSON artifacts for the parent initiative plus the remaining draft child-phase packages needed for the execution stack.
- **T3 — Publish the prompt pair**
  - Create the detailed execution prompt and kickoff prompt for each newly created child-phase package.
- **T4 — Synchronize trackers**
  - Update `Operations/EXECUTION_PLAN.md`, `Operations/PROJECT_FILE_INDEX.md`, and `Operations/ACTION_LOG.md`.
- **T5 — Validate the planning package**
  - Re-read created files, parse YAML and JSON plan artifacts, run `git diff --check`, and run mandatory pre-commit validation.
- **T6 — Commit and push**
  - Commit the planning package and push `codex/m365-authoritative-persona-humanization-expansion-plan` after the bounded pre-commit blocker is green.

## Section 10: Future Implementation Track

### Parent execution discipline

- **Current next act:** `H4S`
- **Execution model:** one child phase at a time, in order, with no auto-advance
- **Notebook-first rule:** `H2`, `H3`, `H4S`, `H4`, and `H5` must complete notebook-backed iteration before any code, registry, verifier, or documentation extraction
- **Landing rule:** each child phase must validate, commit, and push before the next child phase begins

### H1 — Authoritative census and department-model decision

- **Status:** `draft-package-created`
- **Plan:** `plans/m365-authoritative-persona-census-and-department-model-decision/m365-authoritative-persona-census-and-department-model-decision.md`
- **Prompt:** `docs/prompts/codex-m365-authoritative-persona-census-and-department-model-decision.md`
- **Child acts:** `H1A baseline truth lock`, `H1B mapping matrix`, `H1C decision artifact`
- **Gate:** stop and open a separate governed change if any of the `20` extras cannot fit inside the current `10` departments without distortion

### H2 — Humanized employee record completion

- **Status:** `draft-package-created`
- **Plan:** `plans/m365-authoritative-persona-humanized-employee-record-completion/m365-authoritative-persona-humanized-employee-record-completion.md`
- **Prompt:** `docs/prompts/codex-m365-authoritative-persona-humanized-employee-record-completion.md`
- **Child acts:** `H2A field contract`, `H2B notebook-backed employee record artifact`, `H2C verification and closeout`
- **Goal:** create the deterministic employee-record artifact for all `20` promoted personas with bounded metadata and explicit chain-of-command bindings

### H3 — Authoritative registry and capability-map rebase

- **Status:** `draft-package-created`
- **Plan:** `plans/m365-authoritative-persona-registry-and-capability-map-rebase/m365-authoritative-persona-registry-and-capability-map-rebase.md`
- **Prompt:** `docs/prompts/codex-m365-authoritative-persona-registry-and-capability-map-rebase.md`
- **Child acts:** `H3A authoritative roster rebase`, `H3B persona registry rebase`, `H3C capability-map rebase and closeout`
- **Goal:** rebase the authoritative surfaces to `59` total personas while preserving the pre-H5 staged `34 active / 25 planned` split

### H4S — Department-pack scope correction

- **Status:** `draft-package-created`
- **Plan:** `plans/m365-authoritative-persona-h4-scope-correction/m365-authoritative-persona-h4-scope-correction.md`
- **Prompt:** `docs/prompts/codex-m365-authoritative-persona-h4-scope-correction.md`
- **Child acts:** `H4SA dependency and mismatch proof`, `H4SB department-pack authority rebase`, `H4SC validation and H4 unblock`
- **Goal:** rebase the department-pack authority surface to the staged post-H3 truth so H4 can resume on a truthful dependency base

### H4 — Certification and count rebase

- **Status:** `draft-package-created-and-blocked-by-H4S`
- **Plan:** `plans/m365-authoritative-persona-certification-and-count-rebase/m365-authoritative-persona-certification-and-count-rebase.md`
- **Prompt:** `docs/prompts/codex-m365-authoritative-persona-certification-and-count-rebase.md`
- **Child acts:** `H4A certification contract rebase`, `H4B census and commercialization truth rebase`, `H4C verifier/test rebase and closeout`
- **Goal:** rebase certification and count truth to the post-H4S pre-H5 staged state of `59 total / 10 departments / 34 active / 25 planned`

### H5 — Activation gate closeout

- **Status:** `draft-package-created`
- **Plan:** `plans/m365-authoritative-persona-activation-gate-closeout/m365-authoritative-persona-activation-gate-closeout.md`
- **Prompt:** `docs/prompts/codex-m365-authoritative-persona-activation-gate-closeout.md`
- **Child acts:** `H5A activation prerequisite verification`, `H5B final registry and active-surface rebase`, `H5C final validation and branch closeout`
- **Goal:** close the fail-closed activation gate and land the final authoritative state at `59 total / 54 active / 5 planned`

## Section 11: Gates

- **CHECK:C0 — Current-state truth explicit**
  - The plan must explicitly capture `59` runtime definitions, `39` authoritative named personas, `34` active authoritative personas, and the lack of an existing governing plan item.
- **CHECK:C1 — Bounded metadata contract**
  - The plan must explicitly choose bounded metadata fields and reject casual freeform personality schema.
- **CHECK:C2 — Department-model decision gate**
  - The plan must preserve the existing `10`-department model by default or explicitly stop for a separate governed change.
- **CHECK:C3 — Fail-closed activation rule**
  - The plan must state that no promoted persona can be active without name, title, manager, escalation owner, capability-map coverage, and authoritative registry entry.
- **CHECK:C4 — Artifact completeness**
  - The plan triplet and prompt pair must exist and be parseable.
- **CHECK:C5 — Diff hygiene**
  - `git diff --check` must pass before commit.

## Section 12: Determinism Requirements

- `N/A — this is governance and planning work, not math/algorithm work. Determinism is enforced here through bounded metadata fields, explicit stop conditions, and fail-closed activation gates.`

## Section 13: Candidate Persona Humanization Map

| Agent ID | Proposed Name | Recommended Department | Working Style | Communication Style | Decision Style |
| --- | --- | --- | --- | --- | --- |
| `audit-operations` | `Naomi Brooks` | `operations` | `meticulous` | `skeptical` | `evidence-first` |
| `calendar-management-agent` | `Mateo Alvarez` | `communication` | `organized` | `anticipatory` | `conflict-averse` |
| `client-relationship-agent` | `Priya Mehta` | `studio-operations` | `warm` | `responsive` | `follow-through driven` |
| `compliance-monitoring-agent` | `Farah Alvi` | `operations` | `exacting` | `policy-first` | `calm under pressure` |
| `device-management` | `Connor Walsh` | `operations` | `practical` | `methodical` | `steady` |
| `email-processing-agent` | `Hannah Kim` | `communication` | `fast` | `clear` | `triage-oriented` |
| `financial-operations-agent` | `Luis Carvalho` | `studio-operations` | `conservative` | `numbers-first` | `controls-minded` |
| `identity-security` | `Amara Okoye` | `operations` | `vigilant` | `uncompromising` | `least-privilege focused` |
| `it-operations-manager` | `Peter Novak` | `operations` | `calm` | `decisive` | `reliability-first` |
| `knowledge-management-agent` | `Leah Goldstein` | `operations` | `structured` | `curious` | `documentation-heavy` |
| `platform-manager` | `Andre Baptiste` | `engineering` | `systems-minded` | `disciplined` | `dependency-aware` |
| `project-coordination-agent` | `Sofia Petrova` | `project-management` | `organized` | `diplomatic` | `deadline-focused` |
| `project-manager` | `Haruto Tanaka` | `project-management` | `decisive` | `scope-protective` | `milestone-driven` |
| `recruitment-assistance-agent` | `Camila Torres` | `hr` | `personable` | `fair` | `process-consistent` |
| `reports` | `Youssef Haddad` | `studio-operations` | `analytical` | `succinct` | `KPI-focused` |
| `security-operations` | `Tunde Adeyemi` | `operations` | `alert` | `no-nonsense` | `incident-driven` |
| `service-health` | `Chloe Martin` | `operations` | `watchful` | `steady` | `escalation-aware` |
| `teams-manager` | `Alicia Nguyen` | `communication` | `collaborative` | `structured` | `governance-minded` |
| `ucp-administrator` | `Omar El-Masry` | `operations` | `strict` | `fail-closed` | `control-plane focused` |
| `website-operations-specialist` | `Lucia Fernandez` | `marketing` | `careful` | `release-minded` | `rollback-ready` |

## Section 14: Risks and Mitigations

- **Risk:** the repo's current North Star and authoritative registry surfaces still assert `39` personas across `10` departments.
  - **Impact:** `high`
  - **Mitigation:** treat this plan as the only authorized future path to rebase that truth and stop implementation if department expansion is required.
  - **Status:** `open`
- **Risk:** adding freeform personality schema would create unstable and weakly enforceable metadata.
  - **Impact:** `medium`
  - **Mitigation:** keep the metadata contract bounded to `working_style`, `communication_style`, and `decision_style`.
  - **Status:** `open`
- **Risk:** a promoted persona could be marked active before chain-of-command and capability-map truth are ready.
  - **Impact:** `high`
  - **Mitigation:** enforce the H5 fail-closed activation gate.
  - **Status:** `open`
- **Risk:** the repo-wide mandatory pre-commit gate can surface existing hook-driven changes outside the original planning allowlist.
  - **Impact:** `medium`
  - **Mitigation:** permit only the bounded import-bootstrap lint fix in `tests/test_ucp_m365_pack_contracts.py` plus the formatter-only import normalization in `tests/test_ucp_m365_pack_client.py`, and keep all other non-plan runtime/test edits out of scope.
  - **Status:** `open`

## Section 15: Rollback

- **Procedure:**
  - revert only the planning-package files listed in the allowlist
  - remove the new execution-plan initiative block and file-index entries
  - remove the action-log entry if the package is withdrawn before merge
- **Files to revert:**
  - `plans/m365-authoritative-persona-humanization-expansion/m365-authoritative-persona-humanization-expansion.md`
  - `plans/m365-authoritative-persona-humanization-expansion/m365-authoritative-persona-humanization-expansion.yaml`
  - `plans/m365-authoritative-persona-humanization-expansion/m365-authoritative-persona-humanization-expansion.json`
  - `docs/prompts/codex-m365-authoritative-persona-humanization-expansion.md`
  - `docs/prompts/codex-m365-authoritative-persona-humanization-expansion-prompt.txt`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/PROJECT_FILE_INDEX.md`
  - `Operations/ACTION_LOG.md`

## Section 16: Artifacts

- `plans/m365-authoritative-persona-humanization-expansion/m365-authoritative-persona-humanization-expansion.md`
- `plans/m365-authoritative-persona-humanization-expansion/m365-authoritative-persona-humanization-expansion.yaml`
- `plans/m365-authoritative-persona-humanization-expansion/m365-authoritative-persona-humanization-expansion.json`
- `docs/prompts/codex-m365-authoritative-persona-humanization-expansion.md`
- `docs/prompts/codex-m365-authoritative-persona-humanization-expansion-prompt.txt`
- `plans/m365-authoritative-persona-census-and-department-model-decision/m365-authoritative-persona-census-and-department-model-decision.md`
- `plans/m365-authoritative-persona-census-and-department-model-decision/m365-authoritative-persona-census-and-department-model-decision.yaml`
- `plans/m365-authoritative-persona-census-and-department-model-decision/m365-authoritative-persona-census-and-department-model-decision.json`
- `docs/prompts/codex-m365-authoritative-persona-census-and-department-model-decision.md`
- `docs/prompts/codex-m365-authoritative-persona-census-and-department-model-decision-prompt.txt`
- `plans/m365-authoritative-persona-humanized-employee-record-completion/m365-authoritative-persona-humanized-employee-record-completion.md`
- `plans/m365-authoritative-persona-humanized-employee-record-completion/m365-authoritative-persona-humanized-employee-record-completion.yaml`
- `plans/m365-authoritative-persona-humanized-employee-record-completion/m365-authoritative-persona-humanized-employee-record-completion.json`
- `docs/prompts/codex-m365-authoritative-persona-humanized-employee-record-completion.md`
- `docs/prompts/codex-m365-authoritative-persona-humanized-employee-record-completion-prompt.txt`
- `plans/m365-authoritative-persona-registry-and-capability-map-rebase/m365-authoritative-persona-registry-and-capability-map-rebase.md`
- `plans/m365-authoritative-persona-registry-and-capability-map-rebase/m365-authoritative-persona-registry-and-capability-map-rebase.yaml`
- `plans/m365-authoritative-persona-registry-and-capability-map-rebase/m365-authoritative-persona-registry-and-capability-map-rebase.json`
- `docs/prompts/codex-m365-authoritative-persona-registry-and-capability-map-rebase.md`
- `docs/prompts/codex-m365-authoritative-persona-registry-and-capability-map-rebase-prompt.txt`
- `plans/m365-authoritative-persona-certification-and-count-rebase/m365-authoritative-persona-certification-and-count-rebase.md`
- `plans/m365-authoritative-persona-certification-and-count-rebase/m365-authoritative-persona-certification-and-count-rebase.yaml`
- `plans/m365-authoritative-persona-certification-and-count-rebase/m365-authoritative-persona-certification-and-count-rebase.json`
- `docs/prompts/codex-m365-authoritative-persona-certification-and-count-rebase.md`
- `docs/prompts/codex-m365-authoritative-persona-certification-and-count-rebase-prompt.txt`
- `plans/m365-authoritative-persona-activation-gate-closeout/m365-authoritative-persona-activation-gate-closeout.md`
- `plans/m365-authoritative-persona-activation-gate-closeout/m365-authoritative-persona-activation-gate-closeout.yaml`
- `plans/m365-authoritative-persona-activation-gate-closeout/m365-authoritative-persona-activation-gate-closeout.json`
- `docs/prompts/codex-m365-authoritative-persona-activation-gate-closeout.md`
- `docs/prompts/codex-m365-authoritative-persona-activation-gate-closeout-prompt.txt`
- `Operations/EXECUTION_PLAN.md`
- `Operations/PROJECT_FILE_INDEX.md`
- `Operations/ACTION_LOG.md`
- `tests/test_ucp_m365_pack_contracts.py`
- `tests/test_ucp_m365_pack_client.py`

## Section 17: Prompt References

- **Prompt doc:** `docs/prompts/codex-m365-authoritative-persona-humanization-expansion.md`
- **Prompt kickoff:** `docs/prompts/codex-m365-authoritative-persona-humanization-expansion-prompt.txt`
- **Child prompt docs:** `docs/prompts/codex-m365-authoritative-persona-census-and-department-model-decision.md`, `docs/prompts/codex-m365-authoritative-persona-humanized-employee-record-completion.md`, `docs/prompts/codex-m365-authoritative-persona-registry-and-capability-map-rebase.md`, `docs/prompts/codex-m365-authoritative-persona-certification-and-count-rebase.md`, `docs/prompts/codex-m365-authoritative-persona-activation-gate-closeout.md`
- **Prompt template:** `docs/governance/MATHS_PROMPT_TEMPLATE.md`
