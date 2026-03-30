# Plan: M365 Repo — UCP Live Activation Repair

**Plan ID:** `m365-ucp-live-activation-repair`
**Status:** 🟢 Active (`P0A` is next; this repair is now the active live-integration recovery slice for Claude -> UCP -> M365)
**Date:** 2026-03-23
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-ucp-live-activation-repair:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — restore truthful, policy-gated, self-service M365 execution so Claude -> UCP -> M365 remains auditable, deterministic, and commercially honest.
**Historical lineage:** follows the closed Section 7 Claude / UCP workforce contract work and the closed `m365-enterprise-readiness-master-plan` live-certification track; this is a post-certification repair slice for a newly observed live regression.

**Prompt discipline:** Maintain a formal prompt pair under `docs/prompts/`, following the repo two-file prompt rule and the MATHS prompt template. The M365 repo is the planning authority; the sibling UCP repo is the implementation target for the runtime repair.

## Objective

Repair the live activation path so a user-approved Claude/Codex MCP session can activate truthfully, admit governed tools consistently, and execute real M365 actions without collapsing into contradictory `policy_pack`, `session_not_activated`, or fake-credentials failure states.

## Decision Rule

`ActivationPathHealthy = PackEnabled AND ActivationAllowed AND SessionStateReachable`

`LiveToolPathHealthy = ActivationPathHealthy AND ToolRegistrationConsistent AND PolicyAdmissionConsistent`

`LiveM365Callable = LiveToolPathHealthy AND TenantContextReachable AND (SitesRootGreen) AND (DirectoryOrgGreen OR RealGraphPermissionError)`

`RepairReady = LiveM365Callable`

If any term is false, the live Claude -> UCP -> M365 path remains `NO-GO`.

## Intent Definition

### What are we building

We are building a bounded repair for the live Claude -> UCP -> M365 control plane so activation, governance admission, and tool execution agree on the same session state.

### Why are we building it

The current runtime says M365 tools exist while simultaneously blocking `activate_session`, which then causes `m365_action` and `m365_sites` to fail with `session_not_activated`. That contradiction prevents honest live SharePoint and M365 usage.

### What problem does it solve

It removes the broken state machine where discovery says "available," policy says "forbidden," and execution says "not activated."

### Boundaries and non-goals

This plan repairs the activation and tool-surface path. It does not loosen Microsoft tenant permissions, invent alternate auth flows, or relabel downstream Graph authorization failures as connector bugs.

### Required guarantees

- User-approved activation must succeed or fail with the true blocking reason.
- The stdio and HTTP execution surfaces must not disagree about whether the M365 pack is callable.
- `sites.root` must execute live once activation is green.
- `directory.org` must either execute successfully or fail with a real Microsoft permission error, never `credentials_missing` or `session_not_activated` after activation.

### Success criteria

- `activate_session(confirm=true)` succeeds on the live path.
- `session_status` reports active immediately afterward.
- `validate_action` and `constraint_status` remain callable after activation.
- `m365_sites action=sites.root` executes live.
- `m365_action agent=m365-administrator action=directory.org` reaches real Graph auth and returns either success or a real Graph-side permission error.

### Determinism definition

For fixed runtime config, license, tenant contract, and client identity, repeated activation and first-hop M365 calls must produce the same admission decisions and the same class of outcome.

## Plain-English Failure Summary

### What we observed

- The live UCP server reports `m365_pack` enabled.
- A fresh MCP stdio session lists `m365_action` and `m365_sites`.
- The same session rejects `activate_session` because `policy_pack` says the tool is not allowed.
- Because activation is blocked, subsequent M365 calls fail with `session_not_activated`.
- The generic HTTP `/api/v1/tools/{tool_id}` route does not currently expose `validate_action` and has shown parity gaps for M365 tool IDs.

### What this means

The earlier tenant-context repair is no longer the active blocker. The live problem has moved up into the activation and policy admission layer.

## Scope

### In scope

- capture the exact live failure baseline for activation, session-state, and first-hop M365 calls
- repair activation admission in the sibling UCP runtime
- repair or document stdio and HTTP tool-surface parity so the live path is truthful
- reprove live `activate_session`, `session_status`, `validate_action`, `sites.root`, and `directory.org`
- synchronize M365 governance docs and prompt artifacts

### Out of scope

- changing Microsoft Graph tenant permissions except to truthfully classify downstream failures
- reopening already-fixed tenant-context work unless regression evidence proves it
- adding non-M365 execution channels
- claiming live parity is green before retained evidence exists

## Requirements

- **R1 — Formal repair-plan authority**
- **R2 — Formal MATHS prompt pair**
- **R3 — Activation admission repair**
- **R4 — Session-state and tool-surface parity**
- **R5 — Live M365 reproof**
- **R6 — Governance synchronization**

## Execution Stack

### P0 — Failure Baseline and Intent Lock

**Status:** 🟢 Active

**Goal:** Freeze the observed live failure signatures, exact boundaries, and deterministic success criteria before implementation.

**Outputs:**

- retained activation and session-state error signatures
- explicit activation-state decision rule
- bounded implementation target list

**Child Acts:**

#### P0A — Baseline capture and repair intent lock

**Status:** 🟢 Active

**Goal:** Record the exact `policy_pack` activation rejection and `session_not_activated` cascade as the authoritative starting state.

### P1 — Activation Admission Repair

**Status:** ⏳ Pending

**Goal:** Repair the live activation path so user-approved session activation is admitted consistently through the actual runtime.

**Outputs:**

- repaired activation path
- consistent `activate_session` and `session_status` behavior
- bounded policy admission logic

**Child Acts:**

#### P1A — Policy-pack admission repair

**Status:** ⏳ Pending

**Goal:** Fix the policy/allowlist path so activation bypass tools are not contradicted by pack-level admission.

#### P1B — Session-state projection repair

**Status:** ⏳ Pending

**Goal:** Ensure activation state is visible and consistent to the governed tools immediately after activation.

### P2 — Tool-Surface Parity Repair

**Status:** ⏳ Pending

**Goal:** Ensure stdio and HTTP surfaces project the same callable reality for the M365 runtime.

**Outputs:**

- consistent tool registration
- documented or repaired HTTP parity
- bounded live smoke contract

**Child Acts:**

#### P2A — HTTP and stdio parity

**Status:** ⏳ Pending

**Goal:** Remove or document the mismatch where the pack is enabled but some live tool surfaces do not expose the same callable IDs.

### P3 — Live M365 Reproof

**Status:** ⏳ Pending

**Goal:** Re-run the live first-hop M365 proofs after activation and parity are repaired.

**Outputs:**

- green activation transcript
- green `sites.root` transcript
- truthful `directory.org` transcript

**Child Acts:**

#### P3A — Live activation and governance reproof

**Status:** ⏳ Pending

**Goal:** Reprove `activate_session`, `session_status`, `constraint_status`, and `validate_action` on the repaired runtime.

#### P3B — Live M365 first-hop reproof

**Status:** ⏳ Pending

**Goal:** Reprove `m365_sites sites.root` and `m365_action directory.org`, classifying any remaining failure as real downstream Microsoft auth/permission behavior.

### P4 — Governance Closeout

**Status:** ⏳ Pending

**Goal:** Synchronize the retained evidence and final status across M365 and UCP governance surfaces.

**Outputs:**

- updated execution-plan and action-log state
- prompt artifacts aligned to retained evidence
- explicit GO/NO-GO closeout

**Child Acts:**

#### P4A — Repair closeout and operator handoff

**Status:** ⏳ Pending

**Goal:** Close the repair slice with a truthful live-state summary and the next required action, if any.
