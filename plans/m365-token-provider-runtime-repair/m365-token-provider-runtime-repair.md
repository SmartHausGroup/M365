# Plan: M365 Service Auth / Runtime Repair

## Section 1: Plan Header

- **Plan ID:** `plan:m365-token-provider-runtime-repair`
- **Parent Plan ID:** `plan:m365-service-mode-token-acquisition-remediation`
- **Title:** `Repair the M365 service-auth/runtime boundary in the active repair path`
- **Version:** `2.0`
- **Status:** `draft`
- **Owner:** `SMARTHAUS`
- **Date Created:** `2026-03-23`
- **Date Updated:** `2026-03-31`
- **North Star Ref:** `Operations/NORTHSTAR.md`
- **Execution Plan Ref:** `Operations/EXECUTION_PLAN.md § Initiative: M365 Service-Mode Token Acquisition Remediation`
- **Domain:** `infrastructure`
- **Math/Algorithm Scope:** `false`

## Section 2: North Star Alignment

- **Source:** `Operations/NORTHSTAR.md`
- **Principles served:**
  - `M365-only tooling with truthful governed execution`
  - `Self-service posture without repo-authority drift`
  - `Fail-closed security and actor-identity enforcement on governed action paths`
- **Anti-alignment:**
  - `Does NOT weaken the M365 JWT-backed actor identity requirement`
  - `Does NOT relabel local service-auth failures as Microsoft-side failures`
  - `Does NOT execute the sibling UCP consumer-side validation or acceptance acts`

## Section 3: Intent Capture

- **User's stated requirements:**
  - `Set up the M365 integration path the correct way per Microsoft standards`
  - `Align UCP to that contract instead of probing blindly from both ends`
  - `Make the next proper implementation step formal and governed before execution`
- **Intent doc ref:** `captured in this plan`
- **Intent verification:** `R1 through R5 capture the bounded M365-side repair needed before UCP can rerun consumer-side validation truthfully.`

## Section 4: Objective

- **Objective:** Repair the bounded M365-side service-auth/runtime defect on governed `/actions/*` calls so the M365 service can enforce JWT-backed actor identity correctly and pass truthful downstream outcomes back to UCP.
- **Current state:** UCP now reaches the M365 service reliably, but the service fail-closes at the local JWT gate with `401 missing_bearer_token` before Graph token acquisition. The historical child package exists, but it was sparse and framed too narrowly around token-provider behavior instead of the now-proven service-auth/runtime boundary.
- **Target state:** One bounded M365-side repair phase can execute against the real service-auth/runtime boundary, preserve fail-closed JWT enforcement, and stop with truthful live-classification readiness rather than speculative success claims.

## Section 5: Scope

### In scope (conceptual)

- repair the bounded M365-side service-auth/runtime defect in the active repair path
- preserve the governed actor-identity contract on `/actions/*`
- update focused regressions and repair diagnostics
- stop at the point where live classification is the next dependency boundary

### Out of scope (conceptual)

- UCP-side caller alignment
- Microsoft tenant permission changes
- final live classification
- final end-to-end acceptance
- weakening bearer/JWT requirements to force green

### File allowlist (agent MAY touch these)

- `plans/m365-token-provider-runtime-repair/**`
- `docs/prompts/codex-m365-token-provider-runtime-repair.md`
- `docs/prompts/codex-m365-token-provider-runtime-repair-prompt.txt`
- `src/ops_adapter/main.py`
- `src/ops_adapter/app.py`
- `src/ops_adapter/actions.py`
- `src/smarthaus_common/auth_model.py`
- `src/provisioning_api/auth.py`
- `tests/test_ops_adapter.py`
- `tests/test_graph_client.py`
- `tests/test_env_loading.py`
- `docs/commercialization/m365-token-provider-runtime-repair.md`
- `artifacts/diagnostics/m365_token_provider_runtime_repair.json`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist (agent MUST NOT touch these)

- `../UCP/src/**`
- `../UCP/tests/**`
- `registry/**`
- `Any path not listed in the allowlist`

### Scope fence rule

Agent must STOP and re-scope if the repair requires UCP-side caller changes, Microsoft tenant permission changes, or any file outside the allowlist.

## Section 6: Requirements

- **R1 — Repair the diagnosed M365 service-auth/runtime defect**
  - Governed `/actions/*` requests must stop failing locally with `missing_bearer_token` once the repair is correctly applied.
- **R2 — Preserve fail-closed JWT actor identity**
  - The repair must keep bearer/JWT enforcement explicit and fail-closed.
- **R3 — Prove the repaired boundary with focused regressions**
  - Focused tests must cover missing-bearer, valid-bearer, and actor-identity-required paths.
- **R4 — Preserve truthful downstream Microsoft behavior**
  - Local repair must not mask real Microsoft-side invalid-credential or permission outcomes.
- **R5 — Stop at live-classification readiness**
  - This phase ends when M365 is ready for live classification, not when the whole cross-repo flow is closed.

## Section 7: Execution Sequence

- `T1 -> T2 -> T3 -> T4 -> T5`
- Stop on first red.

## Section 8: Tasks

- **T1 — Root-cause lock**
  - Restate the current live truth boundary from the M365 auth gate and the cross-repo contract note.
- **T2 — Bounded service-auth/runtime repair**
  - Implement the minimal M365-side repair required by the diagnosed `/actions/*` auth boundary.
- **T3 — Focused regression coverage**
  - Add or update bounded regression tests and repair diagnostics.
- **T4 — Repair gate**
  - Run the bounded validation suite and confirm the boundary is ready for live classification.
- **T5 — Governance closeout**
  - Synchronize action log, execution plan, file index, and plan status without auto-advancing the next phase.

## Section 9: Gates

- **CHECK:C0 — Root-cause remains explicit**
  - The phase must still target the local M365 service-auth/runtime boundary, not a UCP-side caller change.
- **CHECK:C1 — Fail-closed auth gate preserved**
  - The repair must preserve JWT-backed actor identity and explicit fail-closed error classes.
- **CHECK:C2 — Focused regressions green**
  - Targeted ops/graph/env tests must pass.
- **CHECK:C3 — Downstream truth preserved**
  - Microsoft-side failures must remain distinguishable from local service-auth failures.
- **CHECK:C4 — Diff hygiene**
  - `git diff --check` must pass.

## Section 10: Determinism Requirements

- `N/A — this phase is bounded service-auth/runtime repair, not math/algorithm work. Determinism is enforced through repeatable focused regressions rather than seeded numerical computation.`

## Section 11: Artifacts

- `plans/m365-token-provider-runtime-repair/m365-token-provider-runtime-repair.md`
- `plans/m365-token-provider-runtime-repair/m365-token-provider-runtime-repair.yaml`
- `plans/m365-token-provider-runtime-repair/m365-token-provider-runtime-repair.json`
- `docs/prompts/codex-m365-token-provider-runtime-repair.md`
- `docs/prompts/codex-m365-token-provider-runtime-repair-prompt.txt`
- `notebooks/m365/INV-M365-BS-service-mode-repair-package-governance-alignment.ipynb`
- `configs/generated/service_mode_repair_package_governance_alignment_verification.json`
- `docs/commercialization/m365-token-provider-runtime-repair.md`
- `artifacts/diagnostics/m365_token_provider_runtime_repair.json`

## Section 12: Environment

- **Python version:** `3.14.3`
- **Venv:** `.venv/bin/python`
- **Additional dependencies:**
  - `fastapi`
  - `PyJWT`
  - `httpx`
- **Hardware:** `N/A — local developer workstation`
- **External data:**
  - `local M365 tenant configuration`
- **Pre-notebook check:** `N/A — runtime/auth repair execution stays notebook-backed only for the package-normalization governance prerequisite`

## Section 13: Implementation Approach

- **Option A:** Repair the bounded M365 service-auth/runtime defect inside the existing M365 service.
  - **Pros:** matches the current live failure location at the M365 `/actions/*` JWT gate; preserves the correct cross-repo order; keeps the phase bounded to the resident FastAPI / ops-adapter runtime.
  - **Cons:** still requires careful scope control to avoid drifting into UCP-side work.
- **Option B:** Shift the next repair into UCP-side caller alignment first.
  - **Pros:** could reduce future caller/service mismatch if the M365 service contract were already green.
  - **Cons:** inverts the current contract order and ignores the fact that the local M365 service gate is the first failing boundary.
- **Chosen:** `Option A`
- **Rationale:** the current live failure is local to the M365 service JWT gate before Graph token acquisition, so the next repair must stay inside the M365 service boundary.
- **Rejected rationale:** `Option B` would reintroduce middle-out probing and weaken the cross-repo contract order locked by the current service-auth note.
- **ADR ref:** `N/A`

## Section 14: Risks and Mitigations

- **Risk:** the repair could drift into UCP-side caller work instead of staying M365-local.
  - **Impact:** `high`
  - **Mitigation:** fail closed if the change requires UCP-side files or caller alignment.
  - **Status:** `open`
- **Risk:** the repair could weaken JWT enforcement instead of satisfying the contract correctly.
  - **Impact:** `high`
  - **Mitigation:** require explicit fail-closed checks and missing-bearer / actor-identity regressions.
  - **Status:** `open`
- **Risk:** the repair could hide downstream Microsoft auth or permission failures behind local success claims.
  - **Impact:** `high`
  - **Mitigation:** keep a dedicated downstream-truth gate in diagnostics and final classification.
  - **Status:** `open`
- **Hard blockers:** `none currently`

## Section 15: Rollback

- **Procedure:**
  - revert only the bounded allowlist files changed by this phase
  - restore the prior child-package wording if the normalized package cannot be validated honestly
  - delete `configs/generated/service_mode_repair_package_governance_alignment_verification.json` if produced for a failed normalization attempt
  - update governance trackers to record the rollback state truthfully
- **Files to revert:**
  - `plans/m365-token-provider-runtime-repair/m365-token-provider-runtime-repair.md`
  - `plans/m365-token-provider-runtime-repair/m365-token-provider-runtime-repair.yaml`
  - `plans/m365-token-provider-runtime-repair/m365-token-provider-runtime-repair.json`
  - `docs/prompts/codex-m365-token-provider-runtime-repair.md`
  - `docs/prompts/codex-m365-token-provider-runtime-repair-prompt.txt`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
- **Artifacts to delete:**
  - `configs/generated/service_mode_repair_package_governance_alignment_verification.json`
- **Governance updates on rollback:**
  - `Operations/ACTION_LOG.md`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/PROJECT_FILE_INDEX.md`

## Section 16: Prompt References

- **MATHS template:** `docs/governance/MATHS_PROMPT_TEMPLATE.md`
- **Prompt doc:** `docs/prompts/codex-m365-token-provider-runtime-repair.md`
- **Prompt kickoff:** `docs/prompts/codex-m365-token-provider-runtime-repair-prompt.txt`
- **Per-task prompts:** `N/A`

## Section 17: Traceability

- `plan:m365-token-provider-runtime-repair:R1` -> bounded `/actions/*` service-auth/runtime repair
- `plan:m365-token-provider-runtime-repair:R2` -> fail-closed JWT actor-identity contract
- `plan:m365-token-provider-runtime-repair:R3` -> focused regression proof
- `plan:m365-token-provider-runtime-repair:R4` -> truthful downstream Microsoft classification
- `plan:m365-token-provider-runtime-repair:R5` -> stop at live-classification readiness
- **Files created / used for normalization evidence:**
  - notebook: `notebooks/m365/INV-M365-BS-service-mode-repair-package-governance-alignment.ipynb`
  - generated verification artifact: `configs/generated/service_mode_repair_package_governance_alignment_verification.json`
- **Index updates:** `Operations/PROJECT_FILE_INDEX.md`

## Section 18: Governance Closure

- [ ] `Operations/ACTION_LOG.md` updated
- [ ] `Operations/EXECUTION_PLAN.md` updated
- [ ] `Operations/PROJECT_FILE_INDEX.md` updated for any new or reclassified files
- [ ] Plan artifacts synchronized (`.md/.yaml/.json`)
- [ ] Phase status updated truthfully without auto-advancing the next act

## Section 19: Execution Outcome

- **Task checklist:** `pending`
- **Gate checklist:** `pending`
- **Final decision:** `pending`
- **Approved by:** `pending`
- **Completion timestamp:** `pending`

## Section 20: When Blocked

- **Format:** `STATUS: BLOCKED / TASK: {id} / REASON: {desc} / MISSING: {list} / NEXT ALLOWED ACTION: {path}`
- **Escalation primary:** `SMARTHAUS`
- **Escalation secondary:** `CTO`

## Section 21: Agent Constraints

- Do not weaken the M365 JWT requirement just to make the phase pass.
- Do not expand the phase into UCP-side caller alignment.
- Do not call Microsoft-side invalid credentials or permission failures a local success.
- Stop if the next correct act becomes live classification rather than more repair code.

## Section 22: References

- **North Star:** `Operations/NORTHSTAR.md`
- **Execution plan:** `Operations/EXECUTION_PLAN.md`
- **Applicable rules:**
  - `.cursor/rules/agent-workflow-mandatory.mdc`
  - `.cursor/rules/codex-prompt-creation.mdc`
  - `.cursor/rules/rsf-change-approval.mdc`
  - `.cursor/rules/notebook-first-mandatory.mdc`
  - `.cursor/rules/ma-process-mandatory.mdc`
  - `.cursor/rules/project-file-index-enforcement.mdc`
- **Related plans:**
  - `plans/m365-service-mode-token-acquisition-remediation/m365-service-mode-token-acquisition-remediation.md`
  - `plans/m365-token-provider-path-diagnosis/m365-token-provider-path-diagnosis.md`
- **Related docs:**
  - `../UCP/docs/platform/M365_SERVICE_AUTH_CONTRACT_AND_EXECUTION_ORDER.md`
  - `docs/governance/MATHS_PROMPT_TEMPLATE.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/PROJECT_FILE_INDEX.md`
  - `src/ops_adapter/main.py`
  - `tests/test_ops_adapter.py`
- **MATHS prompt template:** `docs/governance/MATHS_PROMPT_TEMPLATE.md`
