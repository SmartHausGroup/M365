# Plan: M365 authoritative persona humanization expansion

## Section 1: Plan Header

- **Plan Slug:** `m365-authoritative-persona-humanization-expansion`
- **Plan ID:** `plan:m365-authoritative-persona-humanization-expansion`
- **Parent Plan ID:** `plan:m365-post-expansion-promotion-and-persona-activation`
- **Title:** `Promote all 20 extra agents into named digital employees through a governed census rebase`
- **Version:** `1.0`
- **Status:** `active`
- **Owner:** `SMARTHAUS`
- **Date Created:** `2026-04-03`
- **Date Updated:** `2026-04-03`
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
- create the required prompt pair for the future implementation package
- update `Operations/EXECUTION_PLAN.md`, `Operations/PROJECT_FILE_INDEX.md`, and `Operations/ACTION_LOG.md`
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
- `Operations/EXECUTION_PLAN.md`
- `Operations/PROJECT_FILE_INDEX.md`
- `Operations/ACTION_LOG.md`
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

## Section 7: Requirements

- **R0 — Current-state acknowledgment**
  - Explicitly record that the repo was already clean on `development`, `registry/agents.yaml` already contains `59` agents, `registry/ai_team.json` remains authoritative at `39`, and `registry/persona_registry_v2.yaml` remains locked at `39` total / `34` active.
- **R1 — Branch creation and governance validation**
  - Create `codex/m365-authoritative-persona-humanization-expansion-plan` only after governance validation is green.
- **R2 — Plan artifact creation**
  - Create the Markdown, YAML, and JSON plan artifacts for this initiative.
- **R3 — Prompt-pair creation**
  - Create the required detailed prompt plus kickoff prompt for the future implementation package.
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
  - Create the Markdown, YAML, and JSON plan artifacts for the initiative.
- **T3 — Publish the prompt pair**
  - Create the detailed execution prompt and kickoff prompt for the future implementation slice.
- **T4 — Synchronize trackers**
  - Update `Operations/EXECUTION_PLAN.md`, `Operations/PROJECT_FILE_INDEX.md`, and `Operations/ACTION_LOG.md`.
- **T5 — Validate the planning package**
  - Re-read created files, parse YAML and JSON plan artifacts, run `git diff --check`, and run mandatory pre-commit validation.
- **T6 — Commit and push**
  - Commit the planning package and push `codex/m365-authoritative-persona-humanization-expansion-plan` after the bounded pre-commit blocker is green.

## Section 10: Future Implementation Track

### H1 — Authoritative census and department-model decision

- Lock the authoritative expansion contract from `39` to `59`.
- Confirm whether each of the `20` extras can be remapped into the existing `10` departments.
- If any required placement forces a new department, STOP and open a separate governed North Star and execution-plan change before continuing.

### H2 — Humanized employee record completion

- Add or confirm for each promoted persona:
  - `display_name`
  - `title`
  - `department`
  - `manager`
  - `escalation_owner`
  - `working_style`
  - `communication_style`
  - `decision_style`

### H3 — Authoritative registry and capability-map rebase

- Rebase `registry/ai_team.json` to include the promoted named personas.
- Rebase `registry/persona_registry_v2.yaml` to the new authoritative census and status model.
- Rebase `registry/persona_capability_map.yaml` so all promoted personas have bounded capability coverage and approval posture.

### H4 — Certification and count rebase

- Recompute all persona summary counts that currently assert `39` total / `34` active.
- Rebase any certification or commercialization truth surfaces that cite the old authoritative census.
- Fail closed if any public-facing or machine-readable count remains stale.

### H5 — Activation gate closeout

- Ensure no promoted persona is set `active` until H2 through H4 are green.
- Require manager/escalation chain, capability-map entry, authoritative registry entry, and certification-count alignment before activation.
- Close only when runtime truth and claim surfaces agree.

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
- `Operations/EXECUTION_PLAN.md`
- `Operations/PROJECT_FILE_INDEX.md`
- `Operations/ACTION_LOG.md`
- `tests/test_ucp_m365_pack_contracts.py`
- `tests/test_ucp_m365_pack_client.py`

## Section 17: Prompt References

- **Prompt doc:** `docs/prompts/codex-m365-authoritative-persona-humanization-expansion.md`
- **Prompt kickoff:** `docs/prompts/codex-m365-authoritative-persona-humanization-expansion-prompt.txt`
- **Prompt template:** `docs/governance/MATHS_PROMPT_TEMPLATE.md`
