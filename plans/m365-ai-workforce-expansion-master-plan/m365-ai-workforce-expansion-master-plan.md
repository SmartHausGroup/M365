# Plan: M365 Repo — AI Workforce Expansion Master Plan

**Plan ID:** `m365-ai-workforce-expansion-master-plan`
**Status:** Active (`E0A` through `E2E` are complete; `E3A` is the active next act; `E3` through `E9E` are planned and blocked by predecessor work)
**Date:** 2026-03-20
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-ai-workforce-expansion-master-plan:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — complete SMARTHAUS AI workforce across all departments using M365-only tooling, UCP delegation, and zero extra software cost.
**Historical lineage:** follows the closed `m365-enterprise-readiness-master-plan` as the next active program on 2026-03-20.

**Prompt discipline:** Every grouped phase and every child act in this plan must have a formal MATHS prompt pair under `docs/prompts/`, and every prompt pair must follow `docs/governance/MATHS_PROMPT_TEMPLATE.md` plus the repo two-file prompt rule.

**MA process:** MATHS prompts are mandatory for every act. Notebook-first MA phases remain mandatory whenever an act introduces new algorithmic behavior, runtime proofs, or notebook-governed extraction beyond the current contract surface.

## Objective

Define and execute the full SMARTHAUS agentic workforce expansion program so Claude can delegate through UCP into a governed M365 pack that covers the full explicitly-inventoried Microsoft 365 capability universe across all departments and personas.

## Decision Rule

`WorkforceReady = PersonaUniverseLocked ∧ CapabilityUniverseLocked ∧ AuthAndExecutorArchitectureComplete ∧ ActionSurfaceImplemented ∧ DepartmentPacksOperational ∧ ClaudeUCPDelegationOperational ∧ LiveCertificationGreen ∧ LaunchDecisionClosed`

`CapabilityUniverseLocked = ∀ c ∈ GovernableM365Capabilities : Enumerated(c) ∧ Taxonomized(c) ∧ AuthModeMapped(c) ∧ LicenseBoundaryMapped(c) ∧ ExecutorDomainMapped(c) ∧ PersonaPolicyMapped(c)`

`ExecutableAct = Planned ∧ Prompted ∧ Approved ∧ Logged ∧ Validated`

If any term is false, the workforce remains `NO-GO` for complete-release claims.

## Program Targets

- Department count target: `10`
- Persona count target: `39`
- Source roster authority: `registry/ai_team.json`
- Department set:
  - `operations`
  - `hr`
  - `communication`
  - `engineering`
  - `marketing`
  - `product`
  - `project-management`
  - `studio-operations`
  - `testing`
  - `design`
- Workload universe target:
  - `Identity, directory, and tenant administration`
  - `Mail, calendar, contacts, and bookings`
  - `Collaboration, meetings, and communities`
  - `Content, intranet, and files`
  - `Tasks, scheduling, and work management`
  - `Documents, notes, and workspace productivity`
  - `Knowledge, search, and employee experience`
  - `Low-code, workflow, and analytics`
  - `Security, compliance, and data governance`
  - `Devices, endpoint management, and adjacent Windows admin surfaces`
  - `Media, publishing, and extended communications`

## Execution Status

- `E0A` is complete.
- `E0B` is complete.
- `E0C` is complete.
- `E0D` is complete.
- `E0E` is complete.
- `E1A` is complete.
- `E1B` is complete.
- `E1C` is complete.
- `E1D` is complete.
- `E1E` is complete.
- `E2A` is complete.
- `E2B` is complete.
- `E2C` is complete.
- `E2D` is complete.
- `E2E` is complete.
- `E3A` is the active next act.
- `E3` through `E9E` are prepared but blocked by prerequisite work.
- No implementation or certification act beyond the old standalone v1 surface may proceed until `E0` closes the authoritative universe and release-wave map.

## Open Expansion Blockers

- The implemented action surface is now broader than the old standalone v1 slice, but most workload families beyond directory, messaging, SharePoint / files, collaboration / Planner, and bounded Office productivity remain unimplemented.
- No department pack beyond the standalone v1 surface has been certified or released.

## Scope

### In scope

- Inventory the full M365 capability universe workload by workload.
- Bind all departments and personas to explicit capability, risk, and approval requirements.
- Expand the control plane, executor model, and runtime to support the full workforce target.
- Implement department packs and the Claude/UCP delegation layer.
- Live-certify the expanded workforce before making complete-release claims.
- Keep `Operations/NORTHSTAR.md`, `Operations/EXECUTION_PLAN.md`, `Operations/ACTION_LOG.md`, `Operations/PROJECT_FILE_INDEX.md`, and the MATHS prompt inventory synchronized as the active critical path changes.

### Out of scope

- Pretending the previously certified standalone `9`-action surface already equals the full workforce vision.
- Granting monolithic god-mode Microsoft identities instead of bounded executors.
- Expanding outside Microsoft 365, UCP, and repo-owned integration boundaries.
- Making complete-product or complete-capability claims without live evidence and release closure.

## Requirements

- **R1 — Integrated workforce-expansion control plane**
- **R2 — Authoritative department and persona census**
- **R3 — Full M365 workload and capability universe inventory**
- **R4 — Canonical capability, licensing, API, and auth taxonomy**
- **R5 — Universal action contract and bounded executor routing**
- **R6 — Core workload expansion across identity, messaging, files, and collaboration**
- **R7 — Power Platform, analytics, and connector expansion**
- **R8 — Enterprise admin, security, and compliance expansion**
- **R9 — Digital-employee runtime completion**
- **R10 — Department-pack implementation**
- **R11 — Claude and UCP workforce experience**
- **R12 — Live validation, certification, and release closure**
- **R13 — Governance synchronization and prompt inventory completeness**

## Execution Act Model

- Every grouped phase and every child act below is an explicit executable unit.
- Open acts require active plan presence, a formal MATHS prompt pair, explicit approval before write-effect execution, action-log synchronization, execution-plan synchronization, and validation evidence.
- `E8` is a grouped certification phase and may not be executed as one opaque step; it must proceed through `E8A` -> `E8E` in order.

## Integrated Execution Stack

### E0 — Universe Definition and Boundary Lock

**Status:** ✅ Complete

**Goal:** Inventory the full M365 capability universe, lock the department and persona census, and define what complete workforce coverage actually means before implementation expands.

**Outputs:**
- department and persona census
- workload universe inventory
- capability taxonomy
- persona-to-capability map
- release-wave map

**Child Acts:**

#### E0A — Department and Persona Census

**Status:** ✅ Complete

**Goal:** Lock the authoritative department roster and all digital-employee personas that the workforce must support.

#### E0B — M365 Workload Universe Inventory

**Status:** ✅ Complete

**Goal:** Enumerate every M365 workload and adjacent Microsoft admin surface relevant to the workforce target.

#### E0C — Capability Taxonomy and Feasibility Map

**Status:** ✅ Complete

**Goal:** Normalize all identified capabilities into one taxonomy with implementation feasibility, licensing, and exposure status.

#### E0D — Persona-to-Capability and Risk Mapping

**Status:** ✅ Complete

**Goal:** Bind personas and departments to required capabilities, risk classes, and approval posture.

#### E0E — Release-Wave and Completion Map

**Status:** ✅ Complete

**Goal:** Define the executable wave structure and completion criteria for the full workforce program.

### E1 — Universal M365 Control Plane

**Status:** ✅ Complete

**Goal:** Extend the control plane so the pack can absorb the full M365 capability universe through deterministic action contracts, executor routing, and unified audit/governance rules.

**Outputs:**
- universal action schema
- executor routing v2
- auth model v2
- approval/risk matrix
- unified audit schema

**Child Acts:**

#### E1A — Universal Action Contract v2

**Status:** ✅ Complete

**Goal:** Define the canonical action contract that can represent the expanded workforce action surface.

#### E1B — Executor Routing v2

**Status:** ✅ Complete

**Goal:** Route actions by workload and domain through bounded executors instead of monolithic identities.

#### E1C — Auth Model v2

**Status:** ✅ Complete

**Goal:** Define app-only, delegated, and hybrid execution rules per capability and workload.

#### E1D — Approval and Risk Matrix v2

**Status:** ✅ Complete

**Goal:** Classify the expanded action universe into deterministic approval and risk classes.

#### E1E — Unified Audit Schema v2

**Status:** ✅ Complete

**Goal:** Normalize actor, persona, executor, approval, and result evidence across the expanded workforce.

### E2 — Core M365 Workload Expansion

**Status:** 🟢 Active

**Goal:** Implement the foundational business and admin workloads that make the workforce broadly useful across identity, communication, files, and collaboration.

**Outputs:**
- directory expansion
- messaging expansion
- file and site expansion
- collaboration expansion
- document productivity expansion

**Child Acts:**

#### E2A — Entra / Directory Expansion

**Status:** ✅ Complete

**Goal:** Expand identity, group, license, and directory administration capabilities.

#### E2B — Outlook / Exchange Expansion

**Status:** ✅ Complete

**Goal:** Expand mail, calendar, shared mailbox, contact, and messaging operations.

#### E2C — SharePoint / OneDrive / Files Expansion

**Status:** ✅ Complete

**Goal:** Expand site, list, library, file, record, and permission operations.

#### E2D — Teams / Groups / Planner Expansion

**Status:** ✅ Complete

**Goal:** Expand team, channel, membership, group, and task-management operations.

#### E2E — Documents / Spreadsheets / Presentations Expansion

**Status:** 🟢 Ready

**Goal:** Expand Word, Excel, and PowerPoint workflows through deterministic generation and update paths.

### E3 — Power Platform and Analytics Expansion

**Status:** ⏳ Pending

**Goal:** Bring workflow automation, app surfaces, forms, and analytics into the same governed workforce control plane.

**Outputs:**
- Power Automate expansion
- Power Apps expansion
- Power BI expansion
- Forms/connectors expansion
- cross-workload recipes

**Child Acts:**

#### E3A — Power Automate Expansion

**Status:** ⏳ Pending

**Goal:** Add governed automation-flow discovery, invocation, lifecycle, and monitoring.

#### E3B — Power Apps Expansion

**Status:** ⏳ Pending

**Goal:** Add governed Power Apps interaction and administration surfaces.

#### E3C — Power BI Expansion

**Status:** ⏳ Pending

**Goal:** Add governed report, dataset, workspace, and analytics surfaces.

#### E3D — Forms / Approvals / Connectors Expansion

**Status:** ⏳ Pending

**Goal:** Bring forms, connector-backed workflow triggers, and approval integrations into the canonical action surface.

#### E3E — Cross-Workload Automation Recipes

**Status:** ⏳ Pending

**Goal:** Define reusable end-to-end recipes spanning multiple M365 workloads.

### E4 — Enterprise Admin and Security Expansion

**Status:** ⏳ Pending

**Goal:** Extend the workforce to the enterprise-control workloads that require the strictest governance, approvals, and minimum-permission boundaries.

**Outputs:**
- device management expansion
- security expansion
- compliance expansion
- conditional access expansion
- admin/governance expansion

**Child Acts:**

#### E4A — Intune / Devices Expansion

**Status:** ⏳ Pending

**Goal:** Add governed device inventory, compliance, and lifecycle operations.

#### E4B — Security / Defender Expansion

**Status:** ⏳ Pending

**Goal:** Add governed security alert, incident, score, and response operations.

#### E4C — Compliance / Retention / eDiscovery Expansion

**Status:** ⏳ Pending

**Goal:** Add governed compliance, policy, and discovery operations.

#### E4D — Conditional Access / Identity Protection Expansion

**Status:** ⏳ Pending

**Goal:** Add governed identity-protection and conditional-access administration.

#### E4E — Admin and Governance Surface Expansion

**Status:** ⏳ Pending

**Goal:** Unify remaining admin-center and governance controls into the workforce plane.

### E5 — Digital Employee Runtime

**Status:** ⏳ Pending

**Goal:** Turn the persona model into an actual digital workforce runtime that can own work, hold queues, preserve state, and act like a managed staff layer.

**Outputs:**
- persona registry completion
- delegation UX
- task queues
- KPIs/escalation
- memory/work history

**Child Acts:**

#### E5A — Persona Registry Completion

**Status:** ⏳ Pending

**Goal:** Complete the authoritative persona registry with all required fields, constraints, and runtime projections.

#### E5B — Humanized Delegation Interface

**Status:** ⏳ Pending

**Goal:** Support natural requests like talking to Elena Rodriguez instead of targeting raw agents.

#### E5C — Persona Task Queues and State

**Status:** ⏳ Pending

**Goal:** Give personas deterministic task queues, state, and lifecycle management.

#### E5D — Persona KPIs, Ownership, and Escalation

**Status:** ⏳ Pending

**Goal:** Bind performance, ownership, accountability, and escalation into the runtime contract.

#### E5E — Persona Memory and Work History

**Status:** ⏳ Pending

**Goal:** Define bounded, auditable persona memory and work-history semantics.

### E6 — Department Packs

**Status:** ⏳ Pending

**Goal:** Package the workforce into department-operable capability sets so each department has its own governed digital team and workflows.

**Outputs:**
- department capability packs
- department workflow maps
- department approval models
- department KPIs

**Child Acts:**

#### E6A — Operations Department Pack

**Status:** ⏳ Pending

**Goal:** Build the Operations department capability pack.

#### E6B — HR Department Pack

**Status:** ⏳ Pending

**Goal:** Build the HR department capability pack.

#### E6C — Communication Department Pack

**Status:** ⏳ Pending

**Goal:** Build the Communication department capability pack.

#### E6D — Engineering Department Pack

**Status:** ⏳ Pending

**Goal:** Build the Engineering department capability pack.

#### E6E — Marketing Department Pack

**Status:** ⏳ Pending

**Goal:** Build the Marketing department capability pack.

#### E6F — Product Department Pack

**Status:** ⏳ Pending

**Goal:** Build the Product department capability pack.

#### E6G — Project Management Department Pack

**Status:** ⏳ Pending

**Goal:** Build the Project Management department capability pack.

#### E6H — Studio Operations Department Pack

**Status:** ⏳ Pending

**Goal:** Build the Studio Operations department capability pack.

#### E6I — Testing Department Pack

**Status:** ⏳ Pending

**Goal:** Build the Testing department capability pack.

#### E6J — Design Department Pack

**Status:** ⏳ Pending

**Goal:** Build the Design department capability pack.

### E7 — Claude / UCP Workforce Experience

**Status:** ⏳ Pending

**Goal:** Make the full workforce actually usable through Claude and UCP with humanized delegation, orchestration, and executive control.

**Outputs:**
- Claude/UCP delegation contract
- persona selection
- multi-step orchestration
- cross-persona collaboration
- executive controls

**Child Acts:**

#### E7A — Claude to UCP Universal Delegation Contract

**Status:** ⏳ Pending

**Goal:** Define the top-level delegation contract between Claude, UCP, and the workforce runtime.

#### E7B — Persona Discovery and Selection

**Status:** ⏳ Pending

**Goal:** Make it easy to find and target the right digital employee for a request.

#### E7C — Multi-Step Task Orchestration

**Status:** ⏳ Pending

**Goal:** Support composed multi-step work across workload and persona boundaries.

#### E7D — Cross-Persona Collaboration

**Status:** ⏳ Pending

**Goal:** Allow digital employees to hand off, collaborate, and coordinate within governed bounds.

#### E7E — Executive Oversight and Intervention Controls

**Status:** ⏳ Pending

**Goal:** Give executives visibility and intervention controls across the workforce runtime.

### E8 — Live Validation and Workforce Certification

**Status:** ⏳ Pending

**Goal:** Prove the expanded workforce in the live tenant, by workload, persona, department, and cross-department workflows, before release claims are made.

**Outputs:**
- workload certification
- persona certification
- department certification
- cross-department certification
- release gate v2

**Child Acts:**

#### E8A — Workload Certification

**Status:** ⏳ Pending

**Goal:** Certify each workload surface against the live tenant and the bounded executor model.

#### E8B — Persona Certification

**Status:** ⏳ Pending

**Goal:** Certify each persona class against its allowed domains and approval posture.

#### E8C — Department Certification

**Status:** ⏳ Pending

**Goal:** Certify each department pack against its target workflows and responsibilities.

#### E8D — Cross-Department Workflow Certification

**Status:** ⏳ Pending

**Goal:** Certify cross-functional workflows spanning multiple departments and personas.

#### E8E — Enterprise Release Gate v2

**Status:** ⏳ Pending

**Goal:** Close the formal workforce release gate with live evidence and explicit sign-off.

### E9 — Launch and Operating Model

**Status:** ⏳ Pending

**Goal:** Package, onboard, launch, and support the complete workforce with an explicit commercial and operational model.

**Outputs:**
- workforce packaging
- customer onboarding v2
- pilot/rollout model
- support boundary v2
- release decision

**Child Acts:**

#### E9A — Workforce Packaging

**Status:** ⏳ Pending

**Goal:** Package the full workforce offering and supported capability sets for customers.

#### E9B — Customer Onboarding v2

**Status:** ⏳ Pending

**Goal:** Define the onboarding path for the expanded workforce product.

#### E9C — Pilot and Rollout Model v2

**Status:** ⏳ Pending

**Goal:** Define rollout phases, acceptance, and expansion across customers and departments.

#### E9D — Support Boundary v2

**Status:** ⏳ Pending

**Goal:** Define the final operating, support, and customer-ownership boundaries for the full workforce.

#### E9E — Workforce Expansion Release Decision

**Status:** ⏳ Pending

**Goal:** Issue the final release decision for the full workforce program.

## Next Act

`E2D` is complete. It locked the workload authority at `registry/teams_groups_planner_expansion_v2.yaml`, extended the instruction runtime in `src/provisioning_api/routers/m365.py` plus `src/smarthaus_graph/client.py`, aligned the CAIO, capability, routing, auth, and approval contracts for the team/channel/plan/bucket/task slice, and added the notebook-backed `L31` evidence chain with generated verification at `configs/generated/teams_groups_planner_expansion_verification.json`.

`E2E` is complete. It locked the workload authority at `registry/documents_spreadsheets_presentations_expansion_v2.yaml`, added deterministic DOCX/XLSX/PPTX generation in `src/smarthaus_common/office_generation.py`, extended the instruction runtime in `src/provisioning_api/routers/m365.py` plus `src/smarthaus_graph/client.py`, aligned the CAIO, capability, routing, auth, and approval contracts for `create_document`, `update_document`, `create_workbook`, `update_workbook`, `create_presentation`, and `update_presentation`, and added the notebook-backed `L32` evidence chain with generated verification at `configs/generated/documents_spreadsheets_presentations_expansion_verification.json`. `E3A` is now the active next act and must expand Power Automate on top of the completed v2 control plane and the newly-expanded directory, messaging, SharePoint / files, collaboration / Planner, and bounded Office productivity surfaces.
