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
- The first `P1` dead-route code write is blocked by MCP `validate_action(file_edit)` denial `map-2-code-notebook-required`.
- The bounded blocker-fix child phase `plan:m365-persona-action-p1-notebook-evidence-scope-correction` now exists to publish the phase-specific notebook-backed evidence surface required before `P1` code repair can begin truthfully.
- The next act is `P1S` — execute the notebook-evidence scope correction and reopen the blocked `P1` file-edit validation under child-plan authority.
