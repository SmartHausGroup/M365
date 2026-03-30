# Plan: M365 Service-Mode Token Acquisition Remediation

**Plan ID:** `m365-service-mode-token-acquisition-remediation`
**Status:** 🟢 Active (`P0A` is next; plan/package creation is complete, implementation has not started)
**Date:** 2026-03-23
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-service-mode-token-acquisition-remediation:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — restore truthful, self-service, M365-only execution by fixing the remaining M365 service runtime and token-acquisition path inside the M365 repository.
**Historical lineage:** follows `plans/m365-ucp-live-activation-repair/m365-ucp-live-activation-repair.md` (the canonical M365-local predecessor). The sibling UCP repo is historical implementation lineage only and is not the governing authority for this initiative.

**Prompt discipline:** Maintain one detailed MATHS prompt and one short kickoff prompt for every execution phase under `docs/prompts/`, using `docs/governance/MATHS_PROMPT_TEMPLATE.md` and the repo two-file prompt rule. No phase may advance until its active validation gate is green.

**Draft vs Active semantics:** This parent initiative is **Active** and declares a "current next act" (the first pending child phase). Each child phase plan starts in **Draft** status. A child phase transitions to **Active** only when (1) its predecessor phase gate is green, (2) the operator presents the approval packet and receives an explicit "go", and (3) the operator has not advanced any other child phase concurrently. A child phase transitions to **Complete** only after its own gate emits GO. This means the parent can be Active while all remaining child phases are still Draft — the parent's Active status reflects the initiative's liveness, not any child's execution state.

**Predecessor authority:** The canonical predecessor for this initiative is the M365-local artifact `plans/m365-ucp-live-activation-repair/m365-ucp-live-activation-repair.md`. The sibling UCP repo is historical implementation lineage only and must not be treated as the governing authority for any remaining work in this initiative.

## Objective

Move the remaining service-mode runtime, token-acquisition, and downstream Microsoft-classification work into a single M365-governed execution program so Claude can execute one bounded phase at a time and Codex can review those results without repo-authority drift.

## Decision Rule

`ServiceRuntimeReady = SupportedPython AND RequiredDependenciesPresent AND HealthReachable`

`TokenPathKnown = ServiceRuntimeReady AND CredentialSourceResolved AND AuthModeResolved AND ProviderPathObserved`

`TokenAcquisitionHealthy = TokenPathKnown AND (TokenGranted OR TruthfulDownstreamFailure)`

`LiveM365Ready = TokenAcquisitionHealthy AND SitesRootGreen AND (DirectoryOrgGreen OR RealGraphPermissionError)`

`RemediationReady = LiveM365Ready`

If any term is false, the remaining M365 work is still `NO-GO`.

## Intent Definition

### What are we building

We are building the M365-native remediation program for the remaining service-runtime and token-acquisition defect on the live Claude -> UCP -> M365 path.

### Why are we building it

The UCP-side blocker is already repaired. The unresolved work now belongs to the M365 repo because the remaining failure is in the M365 runtime, token-provider path, or downstream Microsoft token/permission boundary.

### What problem does it solve

It removes the cross-repo ambiguity where the remaining work is governed by UCP planning artifacts even though the live fix now belongs to the M365 runtime and auth path.

### Boundaries and non-goals

This plan governs only the remaining M365-side runtime/token work. It does not re-open completed UCP-side repair work, it does not hide Microsoft permission errors, and it does not permit skipping phase gates.

### Required guarantees

- The M365 repo becomes the governing authority for the remaining work.
- Every phase is independently testable and must stay green before the next phase starts.
- Token-acquisition outcomes are classified truthfully as local-runtime, invalid-credential, or Microsoft-side permission behavior.
- The final acceptance decision is explicit GO or NO-GO.

### Success criteria

- A parent M365 plan exists and is registered in governance.
- Each phase has its own governed prompt pair.
- The future execution path is strictly sequential and test-gated.
- The remaining work can be handed to Claude without repo-authority ambiguity.

### Determinism definition

For fixed code, runtime configuration, credential inputs, and live tenant posture, repeated execution of the active phase must produce the same outcome class and the same phase gate result.

## Plain-English Failure Summary

### What we know now

- The UCP-side activation/admission blocker is repaired.
- The remaining failure is no longer “UCP cannot see credentials.”
- The unresolved issue is now in the M365 service runtime, token-provider path, or downstream Microsoft auth/permission behavior.
- The formal plan for that remaining work was sitting in the wrong repo.

### What this means

The next implementation work must be governed from M365, not UCP.

## Scope

### In scope

- create the M365-governed master plan for the remaining service-mode/token work
- create phased child-plan authority for runtime authority lock, readiness, diagnosis, repair, live classification, and final acceptance
- create one detailed prompt and one kickoff prompt per phase
- register the initiative in M365 governance and index every new file

### Out of scope

- runtime implementation in this planning slice
- edits to the sibling UCP repo
- credential rotation or tenant permission changes
- claiming the M365 service path is fixed before the execution phases are completed

## Requirements

- **R1 — Formal M365 plan authority**
- **R2 — Runtime authority and baseline lock phase**
- **R3 — Runtime readiness and health phase**
- **R4 — Token-provider diagnosis phase**
- **R5 — Token-provider repair phase**
- **R6 — Live token-acquisition classification phase**
- **R7 — End-to-end acceptance phase**
- **R8 — Per-phase MATHS prompt pairs**
- **R9 — Strict stop-on-red sequencing**
- **R10 — Governance and file-index synchronization**

## Execution Stack

### P0 — Service Runtime Authority and Baseline Lock

**Status:** 🟢 Active

**Goal:** Lock M365 as the governing repo for the remaining work and freeze the current failure baseline before runtime changes start.

**Outputs:**

- M365-native authority boundary
- baseline failure classes
- explicit prerequisites for the repair phases

**Child Acts:**

#### P0A — Authority and baseline lock

**Status:** 🟢 Active

**Goal:** Record the exact remaining failure boundary and make this repo the formal execution authority.

### P1 — Service Runtime Readiness and Health

**Status:** 🟠 Draft

**Goal:** Make the M365 runtime environment, bootstrap posture, and health reporting truthful and testable.

**Ownership boundary:** P1A owns local runtime, bootstrap, dependency, env-loading, and health truth **only**. It must not diagnose or repair credential-source, auth-mode, or provider-path issues. If P1A evidence shows the remaining blocker is credential/auth-related, P1A must stop with NO-GO and declare P2A as the correct owner.

**Outputs:**

- supported runtime envelope
- deterministic health contract
- readiness diagnostics

**Child Acts:**

#### P1A — Runtime readiness and health

**Status:** 🟠 Draft

**Goal:** Repair the local M365 service bootstrap, dependency, and health truth if needed.

**Fail-closed scope rule:** If evidence during P1A shows the issue belongs to the credential-source/auth-mode/provider-path domain (P2A's scope), P1A must emit NO-GO and stop. It must not drift into P2A's scope.

### P2 — Token Provider Path Diagnosis

**Status:** 🟠 Draft

**Goal:** Determine exactly where the token path fails and stop using ambiguous `credentials_missing` conclusions.

**Ownership boundary:** P2A owns credential-source, auth-mode, and provider-path truth **only**. It must not repair runtime bootstrap, dependency, or health issues. If P2A evidence shows the remaining blocker is runtime/bootstrap/health-related, P2A must reopen P1A rather than drift scope.

**Outputs:**

- credential-source truth
- auth-mode truth
- provider-path truth

**Child Acts:**

#### P2A — Token-provider path diagnosis

**Status:** 🟠 Draft

**Goal:** Prove the exact sink/source/path that still blocks live token acquisition.

**Fail-closed scope rule:** If evidence during P2A shows the issue belongs to the runtime/bootstrap/health domain (P1A's scope), P2A must emit NO-GO, reopen P1A, and stop. It must not drift into P1A's scope.

### P3 — Token Provider Runtime Repair

**Status:** 🟠 Draft

**Goal:** Implement the minimal M365-side repair that fixes the diagnosed token-provider/runtime defect without reopening unrelated surfaces.

**Outputs:**

- repaired provider/runtime path
- focused regression coverage
- truthful failure semantics

**Child Acts:**

#### P3A — Token-provider runtime repair

**Status:** 🟠 Draft

**Goal:** Apply the M365-side runtime/auth fix identified in P2A.

### P4 — Live Token Acquisition Classification

**Status:** 🟠 Draft

**Goal:** Re-run the live path and classify the result as success, invalid credentials, or Microsoft-side permission behavior.

**Closure boundary:** P4A **only** classifies the live token-acquisition outcome and decides advance-to-acceptance or reopen-prior-phase. P4A must **not** issue the final remediation GO/NO-GO — that authority belongs exclusively to P5A.

**Outputs:**

- live token-acquisition evidence
- outcome classification artifact
- explicit GO-to-acceptance or reopen decision

**Child Acts:**

#### P4A — Live token-acquisition classification

**Status:** 🟠 Draft

**Goal:** Prove whether the repair reaches real token acquisition and how the live path now fails or succeeds.

**Closure authority limit:** P4A classifies the outcome and decides advance-or-reopen. It does **not** issue the final remediation GO/NO-GO.

### P5 — Service-Mode End-to-End Acceptance

**Status:** 🟠 Draft

**Goal:** Run the final live `sites.root` and `directory.org` acceptance path and close the initiative truthfully.

**Closure boundary:** P5A is the **sole authority** for the final remediation GO/NO-GO. Only P5A may issue that decision, and only after live `sites.root` and `directory.org` acceptance evidence exists. No earlier phase may claim final closure.

**Outputs:**

- end-to-end live acceptance evidence
- explicit GO or NO-GO
- operator handoff and closure status

**Child Acts:**

#### P5A — End-to-end acceptance and closeout

**Status:** 🟠 Draft

**Goal:** Close the service-mode/token-acquisition remediation with a truthful final decision.

**Final authority:** P5A alone issues the remediation GO/NO-GO after live acceptance evidence.
