# Plan: M365 Persona-Action Full-Support Remediation

## Section 1: Plan Header

- **Plan ID:** `plan:m365-persona-action-full-support-remediation`
- **Parent Plan ID:** `plan:m365-persona-action-certification`
- **Title:** `Drive the certified non-green persona/action surface to truthful full support where possible and explicitly reduce unsupported claims where not`
- **Version:** `1.0`
- **Status:** `active`
- **Owner:** `SMARTHAUS`
- **Date Created:** `2026-04-07`
- **Date Updated:** `2026-04-07`
- **North Star Ref:** `Operations/NORTHSTAR.md`
- **Execution Plan Ref:** `Operations/EXECUTION_PLAN.md § Initiative: M365 Persona-Action Full-Support Remediation`
- **Domain:** `infrastructure`
- **Math/Algorithm Scope:** `false`

## Section 2: North Star Alignment

- **Source:** `Operations/NORTHSTAR.md`
- **Principles served:**
  - `Truthful M365-only workforce execution through real persona-owned operations`
  - `Fail-closed support claims: supported actions must work, unsupported actions must be explicit`
  - `Self-service workforce operation without dead routes, silent stubs, or implied support`
- **Anti-alignment:**
  - `Does NOT widen into UCP runtime work`
  - `Does NOT preserve false claims for legacy aliases that cannot be made truthful`
  - `Does NOT treat policy, tier, or runtime bypasses as acceptable support`

## Section 3: Intent Capture

- **User's stated requirements:**
  - `Get to a fully working state`
  - `If a thing can work, get it working`
  - `If it cannot work truthfully, say so and reduce the claim`
- **Intent verification:** `This initiative exists because persona-action certification is now complete and has produced a classified backlog rather than an implied support surface.`

## Section 4: Objective

- **Objective:** Drive the certified non-green persona/action surface toward truthful full support, prioritizing repo-local dead routes and stubbed handlers first, then permission/policy mismatches, and finally recertifying the repaired workforce graph.
- **Current state:** The completed persona-action certification closes the active workforce graph at `430` persona/action pairs with `136 green`, `1 approval-gated`, `1 actor-tier-gated`, `15 permission-blocked`, `112 fenced`, `49 legacy-stubbed`, `116 dead-routed`, and `0 orphaned`.
- **Target state:** Every persona/action pair that can truthfully work is either `green`, `approval-gated`, or `actor-tier-gated`; any pair that cannot truthfully work is either explicitly fenced by intentional governance or removed from the claimed workforce surface.

## Section 4A: Certified Backlog Baseline

- **Source artifact:** `artifacts/diagnostics/m365_persona_action_certification.json`
- **Backlog buckets to address:**
  - `116` dead-routed active persona/action pairs
  - `49` legacy-stubbed active persona/action pairs
  - `15` permission-blocked active persona/action pairs
  - `112` fenced active persona/action pairs
- **Backlog ordering rule:**
  - fix `dead-routed` first
  - fix `legacy-stubbed` second
  - fix `permission-blocked` alias/tier mismatches third
  - revisit `fenced` surface last and only widen where truthful and safe
- **Truth-reduction rule:** if an action cannot be made truthful at the persona/action layer, remove or reclassify the claim rather than carrying a permanent false positive.

## Section 5: Scope

### In scope (conceptual)

- freeze the certified non-green persona/action backlog as the remediation baseline
- repair dead-routed persona/action paths in registry, routing, and dispatcher surfaces
- replace legacy stub handlers with real M365-backed implementations where feasible
- align permission-tier grants and legacy alias naming where the capability should genuinely exist
- widen OPA/policy support only where governance and runtime truth support it
- downgrade or remove unsupported persona/action claims where remediation is not truthful
- rerun workforce certification until the support surface is truthful

### Out of scope (conceptual)

- UCP runtime edits
- production release promotion
- bypassing OPA, actor identity, approval, or permission tiers
- preserving unsupported persona claims for convenience

### File allowlist (agent MAY touch these)

- `plans/m365-persona-action-full-support-remediation/**`
- `docs/prompts/codex-m365-persona-action-full-support-remediation.md`
- `docs/prompts/codex-m365-persona-action-full-support-remediation-prompt.txt`
- `docs/commercialization/m365-persona-action-certification.md`
- `artifacts/diagnostics/m365_persona_action_certification.json`
- `registry/agents.yaml`
- `registry/persona_registry_v2.yaml`
- `registry/persona_capability_map.yaml`
- `registry/capability_registry.yaml`
- `registry/auth_model_v2.yaml`
- `registry/approval_risk_matrix_v2.yaml`
- `registry/executor_routing_v2.yaml`
- `registry/permission_tiers.yaml`
- `registry/department_pack_operations_v1.yaml`
- `registry/department_pack_project_management_v1.yaml`
- `registry/department_pack_engineering_v1.yaml`
- `policies/ops.rego`
- `policies/agents/*.rego`
- `src/ops_adapter/main.py`
- `src/ops_adapter/app.py`
- `src/ops_adapter/actions.py`
- `src/ops_adapter/personas.py`
- `src/smarthaus_common/permission_enforcer.py`
- `src/smarthaus_common/executor_routing.py`
- `src/smarthaus_common/approval_risk.py`
- `tests/test_ops_adapter.py`
- `tests/test_policies.py`
- `tests/test_executor_routing_v2.py`
- `tests/test_auth_model_v2.py`
- `tests/test_approval_risk_v2.py`
- `docs/commercialization/m365-operations-department-pack-v1.md`
- `docs/commercialization/m365-project-management-department-pack-v1.md`
- `docs/commercialization/m365-engineering-department-pack-v1.md`
- `scripts/ci/verify_operations_department_pack_v1.py`
- `scripts/ci/verify_project_management_department_pack_v1.py`
- `scripts/ci/verify_engineering_department_pack_v1.py`
- `tests/test_operations_department_pack_v1.py`
- `tests/test_project_management_department_pack_v1.py`
- `tests/test_engineering_department_pack_v1.py`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist (agent MUST NOT touch these)

- `../UCP/**`
- `Any path not listed in the allowlist`

### Scope fence rule

Stop and re-scope if truthful remediation requires undocumented tenant changes, UCP-side edits, or governance bypasses outside the repo-local runtime and documented operator tooling.

## Section 6: Requirements

- **R0 — Create the governed remediation package**
  - Create the bounded plan triplet, prompt pair, and tracker activation before any new remediation work.
- **R1 — Freeze the certified backlog**
  - Carry the completed persona-action certification results into a remediation baseline with no unclassified residue.
- **R2 — Repair dead-routed surface**
  - Resolve dead routes in registry, dispatcher, routing, and wrapper layers or remove the false claim.
- **R3 — Replace or retire legacy stubs**
  - Replace legacy literal handlers with real M365-backed implementations where truthful, otherwise reduce the claim surface.
- **R4 — Align permission and alias truth**
  - Fix permission-tier and alias-model mismatches where the capability should exist; otherwise leave it explicitly unsupported.
- **R5 — Revisit policy-fenced surface truthfully**
  - Widen OPA/policy support only where runtime, governance, and risk posture all support the claimed operation.
- **R6 — Re-certify and close out**
  - Re-run the workforce certification matrix and publish the final reduced or repaired support surface.

## Section 7: Phases

- **P0 — Remediation baseline lock**
  - Freeze the certified backlog buckets and the action ordering.
- **P1 — Dead-route remediation**
  - Repair or remove dead-routed persona/action paths.
- **P2 — Legacy-stub remediation**
  - Replace synthetic handlers with real implementations or reduce the claims.
- **P3 — Permission and alias remediation**
  - Normalize legacy alias names and tier grants where truthful.
- **P4 — Policy-fence remediation**
  - Evaluate fenced pairs and widen only where policy truthfully permits.
- **P5 — Final re-certification closeout**
  - Re-run workforce certification and publish final truth.

## Section 8: Validation

- validate every mutating step through UCP before execution
- use notebook-backed evidence for code/config/governance extraction as required
- run focused regression suites after each remediation phase
- run `pre-commit run --all-files`
- run `git diff --check`
- do not claim completion until the successor workforce certification artifact is green and truthful

## Section 9: Gates

- **CHECK:C0 — Remediation package exists**
  - The successor plan, prompt pair, and tracker activation must exist before remediation begins.
- **CHECK:C1 — Certified backlog is frozen**
  - The remediation baseline must match the completed certification artifact.
- **CHECK:C2 — Dead routes truthfully resolved**
  - Dead-routed pairs are either repaired or removed from the claim surface.
- **CHECK:C3 — Legacy stubs truthfully resolved**
  - Stubbed pairs are either implemented or retired from claimed support.
- **CHECK:C4 — Permission and policy truth aligned**
  - Alias, tier, and OPA support surfaces no longer drift from claimed persona capabilities.
- **CHECK:C5 — Final workforce matrix republished**
  - The initiative closes only with a successor truthful workforce certification artifact.

## Section 10: Artifacts

- `plans/m365-persona-action-full-support-remediation/m365-persona-action-full-support-remediation.md`
- `plans/m365-persona-action-full-support-remediation/m365-persona-action-full-support-remediation.yaml`
- `plans/m365-persona-action-full-support-remediation/m365-persona-action-full-support-remediation.json`
- `docs/prompts/codex-m365-persona-action-full-support-remediation.md`
- `docs/prompts/codex-m365-persona-action-full-support-remediation-prompt.txt`

## Section 11: Current Result

- `R0` is complete once this package is created and tracked.
- The certified predecessor initiative `plan:m365-persona-action-certification` is complete.
- The current remediation baseline is:
  - `430` active persona/action pairs
  - `136` `green`
  - `1` `approval-gated`
  - `1` `actor-tier-gated`
  - `15` `permission-blocked`
  - `112` `fenced`
  - `49` `legacy-stubbed`
  - `116` `dead-routed`
  - `0` `orphaned`
- `P0` is complete as a read-only backlog lock; the certified remediation ordering remains `dead-routed -> legacy-stubbed -> permission/alias -> policy-fenced -> re-certification`.
- The first `P1` dead-route code write was originally blocked by MCP `validate_action(file_edit)` denial `map-2-code-notebook-required`.
- The bounded blocker-fix child phase `plan:m365-persona-action-p1-notebook-evidence-scope-correction` is complete and published the phase-specific notebook-backed evidence surface required before `P1` code repair can begin truthfully.
- The `L89` dead-route remediation evidence chain is now in place and the blocked `P1` file-edit validation reopened under child-plan authority.
- `P1` is complete. The first dead-route remediation wave resolved all `21` previously dead-routed unique aliases in the certified backlog by converting `12` aliases to truthful mapped handlers (`sites.provision`, `teams.add_channel`, the Planner aliases, the schedule aliases, and the HR update/offboard aliases) and converting `9` aliases to explicit legacy-stubbed truth instead of leaving them dead-routed (`deployment.production`, `content.create`, `content.update`, `analytics.read`, `seo.update`, `policy.create`, `review.initiate`, `followup.create`, `campaign.create`).
- The `P1` validation slice is green:
  - `PYTHONPATH=src .venv/bin/pytest -q tests/test_ops_adapter.py tests/test_policies.py` → `60 passed`
  - `pre-commit run --all-files` → passed
  - `git diff --check` → passed
- The first bounded `P2` code write was blocked by MCP `validate_action(file_edit)` denial `map-2-code-notebook-required` against `src/ops_adapter/actions.py` and `tests/test_ops_adapter.py` for the targeted aliases `task.create`, `follow-up.schedule`, and `reminder.send`.
- The bounded blocker-fix child phase `plan:m365-persona-action-p2-notebook-evidence-scope-correction` is complete and published the required governance notebook `INV-M365-CQ`, generated verification, and the future `L90` legacy-stub evidence chain.
- The blocked `P2` file-edit validation has been reopened under child-plan authority.
- The first bounded `P2` legacy-stub implementation wave is complete. The `L90` target aliases now dispatch through truthful handlers in `src/ops_adapter/actions.py`: `task.create -> planner_create_task`, `follow-up.schedule -> calendar_create`, and `reminder.send -> mail_send`.
- This first wave removes `3` unique aliases and `4` active persona/action pairs from the legacy-stub bucket without widening permissions or policy.
- Validation passed with `PYTHONPATH=src .venv/bin/pytest -q tests/test_ops_adapter.py` (`59 passed`).
- The bounded second-wave `P2` code-write probe is blocked by MCP `validate_action(file_edit)` denial `map-2-code-notebook-required` against `src/ops_adapter/actions.py` and `tests/test_ops_adapter.py` for the targeted aliases `followup.create`, `client.follow-up`, `satisfaction.survey`, and `interview.schedule`.
- The bounded blocker-fix child phase `plan:m365-persona-action-p2-second-wave-notebook-evidence-scope-correction` is complete and published the required governance notebook `INV-M365-CS`, generated verification, and the future `L91` legacy-stub evidence chain.
- The blocked second-wave `P2` file-edit validation has been reopened under child-plan authority.
- The bounded second-wave `P2` legacy-stub implementation wave is complete. The `L91` target aliases now dispatch through truthful handlers in `src/ops_adapter/actions.py`: `followup.create -> calendar_create`, `client.follow-up -> calendar_create`, `satisfaction.survey -> mail_send`, and `interview.schedule -> calendar_create`.
- This second wave removes `4` unique aliases and `6` active persona/action pairs from the legacy-stub bucket without widening permissions or policy.
- Validation passed with `PYTHONPATH=src .venv/bin/pytest -q tests/test_ops_adapter.py` (`66 passed`).
- The bounded third-wave `P2` code-write probe is blocked by MCP `validate_action(file_edit)` denial `map-2-code-notebook-required` against `src/ops_adapter/actions.py` and `tests/test_ops_adapter.py` for the targeted aliases `archive-project`, `system.health-check`, and `alerts.respond`.
- The bounded blocker-fix child phase `plan:m365-persona-action-p2-third-wave-notebook-evidence-scope-correction` is complete and published the required governance notebook `INV-M365-CU`, generated verification, and the future `L92` legacy-stub evidence chain.
- The blocked third-wave `P2` file-edit validation has been reopened under child-plan authority.
- The bounded third-wave `P2` legacy-stub implementation wave is complete. The `L92` target aliases now dispatch through truthful handlers in `src/ops_adapter/actions.py`: `archive-project -> teams_archive`, `system.health-check -> health_overview`, and `alerts.respond -> security_alert_update`.
- This third wave removes `3` unique aliases and `3` active persona/action pairs from the legacy-stub bucket without widening permissions or policy.
- Validation passed with `PYTHONPATH=src .venv/bin/pytest -q tests/test_ops_adapter.py` (`72 passed`).
- The bounded blocker-fix child phase `plan:m365-persona-action-p2-fourth-wave-notebook-evidence-scope-correction` is complete and published governance notebook `INV-M365-CW`, generated verification, and the future `L93` evidence chain for `task.assign`, `deadline.track`, `status.update`, and `report.generate`.
- The blocked fourth-wave `P2` file-edit validation has been reopened under child-plan authority.
- The bounded fourth-wave `P2` legacy-stub implementation wave is complete. The `L93` target aliases now dispatch through truthful internal workforce handlers in `src/ops_adapter/actions.py`: `task.assign -> create_persona_task`, `deadline.track -> list_persona_tasks`, `status.update -> update_persona_task`, and `report.generate -> build_persona_work_history` plus `build_persona_accountability`.
- This fourth wave removes `4` unique aliases and `8` active persona/action pairs from the legacy-stub bucket without widening permissions or policy.
- Validation passed with `PYTHONPATH=src .venv/bin/pytest -q tests/test_ops_adapter.py` (`80 passed`).
- The bounded blocker-fix child phase `plan:m365-persona-action-p2-fifth-wave-notebook-evidence-scope-correction` is complete and published governance notebook `INV-M365-CY`, generated verification, and the future `L94` evidence chain for `infrastructure.monitor`, `backup.verify`, and `security.scan`.
- The blocked fifth-wave `P2` file-edit validation has been reopened under child-plan authority.
- The bounded fifth-wave `P2` legacy-stub implementation wave is complete. The `L94` target aliases now dispatch through truthful IT-operations outcomes in `src/ops_adapter/actions.py`: `infrastructure.monitor -> health_overview`, `security.scan -> security_secure_score`, and `backup.verify -> explicit unsupported M365-only failure`.
- This fifth wave removes `3` unique aliases and `3` active persona/action pairs from the legacy-stub bucket without widening permissions or policy.
- Validation passed with `PYTHONPATH=src .venv/bin/pytest -q tests/test_ops_adapter.py` (`86 passed`).
- The bounded blocker-fix child phase `plan:m365-persona-action-p2-sixth-wave-notebook-evidence-scope-correction` is complete and published governance notebook `INV-M365-DA`, generated verification, and the future `L95` evidence chain for the website/non-M365 aliases `deployment.production`, `website.deploy`, `cdn.purge`, `dns.update`, `ssl.renew`, `performance.optimize`, and `backup.restore`.
- The blocked sixth-wave `P2` file-edit validation has been reopened under child-plan authority.
- The bounded sixth-wave `P2` legacy-stub implementation wave is complete. The `L95` target aliases now fail closed explicitly in `src/ops_adapter/actions.py`: `deployment.production`, `website.deploy`, `cdn.purge`, `dns.update`, `ssl.renew`, `performance.optimize`, and `backup.restore` all raise `unsupported_m365_only_action` instead of returning fake success.
- This sixth wave removes `7` unique aliases and `7` active persona/action pairs from the legacy-stub bucket without widening permissions or policy.
- Validation passed with `PYTHONPATH=src .venv/bin/pytest -q tests/test_ops_adapter.py` (`92 passed`).
- The bounded seventh-wave `P2` legacy-stub implementation wave is complete. The remaining literal stub aliases now fail closed explicitly in `src/ops_adapter/actions.py`: `content.create`, `content.update`, `analytics.read`, `seo.update`, `policy.create`, `review.initiate`, and `campaign.create` all raise `unsupported_m365_only_action` instead of returning fake success.
- This seventh wave removes `7` unique aliases and `7` active persona/action pairs from the legacy-stub bucket without widening permissions or policy.
- Validation passed with `PYTHONPATH=src .venv/bin/pytest -q tests/test_ops_adapter.py` (`92 passed`).
- The bounded final `P2` legacy-stub implementation wave is complete. The remaining synthetic helper aliases now fail closed explicitly in `src/ops_adapter/actions.py`: `update-project-status`, `deprovision-client-services`, `get-client-status`, `email.classify`, `conflict.resolve`, `feedback.analyze`, `relationship.score`, `engagement.plan`, `compliance.check`, `policy.validate`, `audit.prepare`, `violation.report`, `remediation.plan`, `candidate.screen`, `feedback.collect`, `offer.prepare`, `onboarding.initiate`, `invoice.process`, `expense.approve`, `budget.track`, `forecast.update`, `document.index`, `search.optimize`, `content.curate`, `training.recommend`, and `expert.connect` all raise `unsupported_m365_only_action` instead of returning fabricated business logic.
- This final wave exhausts the frozen `G2` legacy-stub perimeter. `src/ops_adapter/actions.py` now contains no literal `status: "stubbed"` handlers, and the frozen `legacy_stubbed_unique_actions` set from `artifacts/diagnostics/m365_persona_action_certification.json` has zero remaining members after the completed `P2` waves.
- Validation passed with `PYTHONPATH=src .venv/bin/pytest -q tests/test_ops_adapter.py` (`119 passed`).
- `P2` is complete. `P3` is the active next act.
- The first bounded `P3` permission/alias remediation wave is complete. `src/smarthaus_common/permission_enforcer.py` now normalizes the legacy aliases `create-workspace`, `add-workspace-members`, `create-channels`, `get-team-status`, `email.send_individual`, `email.respond`, `email.forward`, `email.archive`, `meeting.organize`, `availability.check`, and `employee.onboard` onto truthful canonical permission surfaces that already exist in the runtime.
- This first `P3` wave reduces the frozen `permission_blocked_aliases_with_no_tier_support` set from `15` aliases to `4` aliases:
  - `create-project`
  - `deployment.preview`
  - `list-projects`
  - `provision-client-services`
- Validation passed with `PYTHONPATH=src .venv/bin/pytest -q tests/test_ops_adapter.py` (`130 passed`).
- The bounded child blocker phase `plan:m365-persona-action-p3-department-pack-scope-correction` is complete and published governance notebook `INV-M365-DC` with generated verification `configs/generated/persona_action_p3_department_pack_scope_correction_v1_verification.json`.
- The second bounded `P3` retirement wave is complete. The final non-M365 aliases `create-project`, `deployment.preview`, `list-projects`, and `provision-client-services` now fail closed explicitly in `src/ops_adapter/actions.py`, and the affected persona surfaces now carry truthful real M365 actions instead:
  - `website-manager` -> `sites.list`, `sites.get`, `lists.list`, `lists.get`, `lists.items`, `lists.create_item`, `files.list`, `files.get`, `files.search`, `files.create_folder`, `files.upload`, `files.share`
  - `project-manager` -> `teams.list`, `teams.get`, `channels.list`, `calendar.list`, `calendar.create`, `calendar.get`, `sites.list`, `lists.list`, `lists.items`, `archive-project`
  - `platform-manager` -> `sites.provision`, `sites.list`, `apps.list`, `apps.get`, `service_principals.list`, `directory.org`
- The affected department-pack authority, commercialization, verifier, and test surfaces now reconcile to the new counts:
  - operations supported actions -> `91`
  - project-management supported actions -> `46`
  - engineering supported actions -> `68`
- Validation passed with:
  - `python3 -m py_compile src/ops_adapter/actions.py scripts/ci/verify_operations_department_pack_v1.py scripts/ci/verify_project_management_department_pack_v1.py scripts/ci/verify_engineering_department_pack_v1.py tests/test_ops_adapter.py tests/test_persona_registry_v2.py tests/test_operations_department_pack_v1.py tests/test_project_management_department_pack_v1.py tests/test_engineering_department_pack_v1.py`
  - `PYTHONPATH=src .venv/bin/pytest -q tests/test_persona_registry_v2.py tests/test_ops_adapter.py tests/test_operations_department_pack_v1.py tests/test_project_management_department_pack_v1.py tests/test_engineering_department_pack_v1.py` (`149 passed`)
- `P3` is complete. `P4` is now the active next act.
- The first read-only `P4` sweep found that repo-local OPA policy truth is severely stale against the current active registry:
  - `54` active personas
  - `53` active personas with at least one repo-local `action_not_allowed` denial
  - `419` denied active persona/action pairs
  - `152` denied unique aliases
- The bounded child blocker phase `plan:m365-persona-action-p4-policy-fence-scope-correction` is now required before `P4` policy edits may begin truthfully because the parent initiative needs notebook-backed scope evidence for the widened policy-remediation surface.
- The bounded child blocker phase `plan:m365-persona-action-p4-policy-fence-scope-correction` is complete. The governance notebook `INV-M365-DD` and generated verification now freeze the exact repo-local policy drift, and the parent initiative is returned to `P4` with notebook-backed authority to edit the repo-local policy and approval-risk surfaces.
- `P4` is complete. `policies/ops.rego` now mirrors the active runtime-backed persona graph instead of the stale micro-surface, the four legacy per-agent policy mirrors are synchronized to the same truth, and `tests/test_policies.py` now carries drift guards that compare the repo-local OPA allow/approval maps against the live active persona graph plus the explicit `unsupported_m365_only_action` runtime perimeter.
- The repo-local OPA drift has collapsed from `419` denied active persona/action pairs across `152` unique aliases to the explicit unsupported perimeter of `35` denied active pairs across `32` unique aliases. The repaired policy surface now allows `410` active persona/action pairs cleanly and denies only the aliases that runtime already fail-closes.
- The `P4` validation slice is green:
  - `PYTHONPATH=src .venv/bin/pytest -q tests/test_policies.py tests/test_ops_adapter.py` → `148 passed`
  - `pre-commit run --all-files` → passed
  - `git diff --check` → passed
- `P5` is blocked by a live-universe shift between the stale published workforce certification artifact and the current post-`P4` runtime truth.
- The bounded child blocker phase `plan:m365-persona-action-p5-recertification-scope-correction` is now created with governance notebook `INV-M365-DE` and generated verification `configs/generated/persona_action_p5_recertification_scope_correction_v1_verification.json`.
- `P5S` is now the active next act before any final `P5` commercialization or diagnostics closeout may begin.
