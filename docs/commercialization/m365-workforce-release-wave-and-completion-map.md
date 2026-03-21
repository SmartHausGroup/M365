# SMARTHAUS Workforce Release-Wave and Completion Map

## Purpose

Turn the phase list into an executable release sequence so the workforce program can grow in bounded waves instead of becoming one giant undeliverable backlog.

## Inputs

- roster authority: [m365-department-persona-census.md](/Users/smarthaus/Projects/GitHub/M365/docs/commercialization/m365-department-persona-census.md)
- workload universe: [m365-workload-universe-inventory.md](/Users/smarthaus/Projects/GitHub/M365/docs/commercialization/m365-workload-universe-inventory.md)
- capability taxonomy: [m365-capability-taxonomy-and-feasibility-map.md](/Users/smarthaus/Projects/GitHub/M365/docs/commercialization/m365-capability-taxonomy-and-feasibility-map.md)
- persona map: [m365-persona-capability-and-risk-map.md](/Users/smarthaus/Projects/GitHub/M365/docs/commercialization/m365-persona-capability-and-risk-map.md)
- structured wave authority: [workforce_release_wave_map.yaml](/Users/smarthaus/Projects/GitHub/M365/registry/workforce_release_wave_map.yaml)

## Core Rule

The workforce is complete only when all waves from `W0` through `W10` are complete.

`WorkforceComplete = W0 ∧ W1 ∧ W2 ∧ W3 ∧ W4 ∧ W5 ∧ W6 ∧ W7 ∧ W8 ∧ W9 ∧ W10`

Any lower wave may unlock the next wave. It may not be used to claim completion of the waves above it.

## Current Position

- `W0` is complete.
- `W1` is the current active wave.
- No release claim may exceed `W0` authority lock plus the already closed standalone v1 slice until later waves actually turn green.

## Wave Summary

| Wave | Title | Scope | Current status | What it unlocks |
| --- | --- | --- | --- | --- |
| `W0` | Universe Authority Lock | `E0A` through `E0E` | `complete` | `W1` |
| `W1` | Universal Control Plane v2 | `E1A` through `E1E` | `ready` | `W2`, `W3`, `W4`, `W5` |
| `W2` | Core Admin and Collaboration Workloads | `E2A` through `E2D` | `pending` | `W6`, `W7`, `W8` |
| `W3` | Productivity, Workflow, and Analytics Expansion | `E2E`, `E3A` through `E3E` | `pending` | `W6`, `W7`, `W8` |
| `W4` | Enterprise Governance and Admin Expansion | `E4A` through `E4E` | `pending` | `W6`, `W8`, `W9` |
| `W5` | Digital Employee Runtime | `E5A` through `E5E` | `pending` | `W6`, `W7`, `W8` |
| `W6` | Department Packs Wave A | `E6A` through `E6E` | `pending` | `W7`, `W8` |
| `W7` | Department Packs Wave B | `E6F` through `E6J` | `pending` | `W8`, `W9` |
| `W8` | Claude and UCP Workforce Experience | `E7A` through `E7E` | `pending` | `W9` |
| `W9` | Live Validation and Certification | `E8A` through `E8E` | `pending` | `W10` |
| `W10` | Launch, Packaging, and Operating Closure | `E9A` through `E9E` | `pending` | final release |

## Wave Details

### W0 — Universe Authority Lock

- Acts:
  - `E0A`, `E0B`, `E0C`, `E0D`, `E0E`
- Exit criteria:
  - authoritative roster locked
  - workload universe locked
  - capability taxonomy locked
  - persona-to-capability map locked
  - release-wave map locked
- Allowed claim:
  - the program boundary is explicit
- Forbidden claim:
  - the full workforce exists in runtime

### W1 — Universal Control Plane v2

- Acts:
  - `E1A`, `E1B`, `E1C`, `E1D`, `E1E`
- Exit criteria:
  - universal action contract v2
  - executor routing v2
  - auth model v2
  - approval/risk matrix v2
  - unified audit schema v2
- Allowed claim:
  - the control-plane contract for broad expansion is ready
- Forbidden claim:
  - broad workload coverage is done

### W2 — Core Admin and Collaboration Workloads

- Acts:
  - `E2A`, `E2B`, `E2C`, `E2D`
- Exit criteria:
  - identity/admin
  - mail/calendar
  - files/sites
  - teams/groups/tasks
  - all implemented under the v2 control plane
- Allowed claim:
  - core M365 business/admin workloads are implemented
- Forbidden claim:
  - full document, analytics, security, or persona runtime completion

### W3 — Productivity, Workflow, and Analytics Expansion

- Acts:
  - `E2E`, `E3A`, `E3B`, `E3C`, `E3D`, `E3E`
- Exit criteria:
  - document productivity flows are defined
  - Power Platform contracts are defined
  - analytics and connector-backed workflows are defined
- Allowed claim:
  - productivity and workflow workloads are represented in the governed action surface
- Forbidden claim:
  - full enterprise-governance coverage

### W4 — Enterprise Governance and Admin Expansion

- Acts:
  - `E4A`, `E4B`, `E4C`, `E4D`, `E4E`
- Exit criteria:
  - devices, security, compliance, conditional access, and admin-center edges are bounded
  - privileged actions have explicit governance posture
- Allowed claim:
  - enterprise-control workloads are represented under bounded governance
- Forbidden claim:
  - customer-ready release without certification

### W5 — Digital Employee Runtime

- Acts:
  - `E5A`, `E5B`, `E5C`, `E5D`, `E5E`
- Exit criteria:
  - personas become real runtime objects
  - humanized delegation resolves to those personas
  - queues, ownership, escalation, and memory contracts exist
- Allowed claim:
  - digital employees are runtime-real
- Forbidden claim:
  - all department packs are operational

### W6 — Department Packs Wave A

- Acts:
  - `E6A`, `E6B`, `E6C`, `E6D`, `E6E`
- Departments:
  - Operations
  - HR
  - Communication
  - Engineering
  - Marketing
- Exit criteria:
  - each department has a bounded pack with personas, workflows, approvals, and capability boundaries

### W7 — Department Packs Wave B

- Acts:
  - `E6F`, `E6G`, `E6H`, `E6I`, `E6J`
- Departments:
  - Product
  - Project Management
  - Studio Operations
  - Testing
  - Design
- Exit criteria:
  - all `10` departments now have bounded packs

### W8 — Claude and UCP Workforce Experience

- Acts:
  - `E7A`, `E7B`, `E7C`, `E7D`, `E7E`
- Exit criteria:
  - Claude can delegate through UCP into the workforce using humanized persona routing
  - persona discovery, orchestration, collaboration, and executive oversight all exist
- Allowed claim:
  - the workforce is operator-accessible through Claude/UCP
- Forbidden claim:
  - the workforce is fully certified or launched

### W9 — Live Validation and Certification

- Acts:
  - `E8A`, `E8B`, `E8C`, `E8D`, `E8E`
- Exit criteria:
  - workload certification green
  - persona certification green
  - department certification green
  - cross-department certification green
  - workforce release gate green
- Allowed claim:
  - the complete workforce is live-certified
- Forbidden claim:
  - launch closure is finished without `W10`

### W10 — Launch, Packaging, and Operating Closure

- Acts:
  - `E9A`, `E9B`, `E9C`, `E9D`, `E9E`
- Exit criteria:
  - packaging complete
  - onboarding complete
  - rollout model complete
  - support boundary complete
  - final release decision green

## Completion Semantics

The workforce is not complete when:

- only the roster is locked
- only the control plane is redesigned
- only some workloads exist
- only some department packs exist
- only Claude/UCP routing exists without certification

The workforce is complete only when:

1. all waves are complete
2. each of the `39` personas is runtime-real or intentionally bounded by the final workforce contract
3. all declared workload families have a certified implementation or an explicitly bounded no-go decision
4. Claude/UCP delegation works across the completed workforce
5. the live certification and final launch gates are green

## What E0E Resolves

`E0E` closes the last ambiguity inside the authority wave:

- it converts the program from a phase list into a release sequence
- it defines what each wave unlocks
- it defines what each wave does not justify claiming
- it gives the rest of the program a deterministic order

## Next Dependency

`E1A` is now the next act. It must define the universal action contract v2 that the rest of the workforce expansion will use.
