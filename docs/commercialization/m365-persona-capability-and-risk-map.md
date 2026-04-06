# SMARTHAUS Persona-to-Capability and Risk Map

## Purpose

Bind the authoritative `59`-persona workforce roster to explicit capability families, risk classes, and approval posture so later phases stop treating the workforce as an undifferentiated agent pool.

## Inputs

- authoritative roster: [ai_team.json](/Users/smarthaus/Projects/GitHub/M365/registry/ai_team.json)
- workload and capability taxonomy: [m365-capability-taxonomy-and-feasibility-map.md](/Users/smarthaus/Projects/GitHub/M365/docs/commercialization/m365-capability-taxonomy-and-feasibility-map.md)
- runtime action surface: [agents.yaml](/Users/smarthaus/Projects/GitHub/M365/registry/agents.yaml)
- structured H3 mapping output: [persona_capability_map.yaml](/Users/smarthaus/Projects/GitHub/M365/registry/persona_capability_map.yaml)

## Core Rule

The authoritative workforce map is now:

`PersonaScope = Department × Persona × WorkloadFamilies × CapabilityFamilies × CurrentRiskTier × ApprovalProfile × CoverageStatus`

No later phase may claim that a persona can do work unless that work fits the persona's mapped capability families and approval posture.

## Approval Profiles

| Approval profile | Meaning |
| --- | --- |
| `low-observe-create` | No approval for read, research, draft, or internal-prep work; department-owner approval for outbound publication, canonical asset changes, or external sharing. |
| `medium-operational` | Department-owner approval for routine internal mutations; dual control for destructive, cross-department, or externally visible changes. |
| `high-impact` | Human approval for all mutating actions with tenant, identity, public-facing, financial, or organization-wide impact; dual control for destructive or privileged changes. |
| `critical-regulated` | Dual human approval and explicit sign-off for regulated, personnel-state, legal, security, or compliance-sensitive mutations. |

## Coverage Findings

- `59/59` personas in [ai_team.json](/Users/smarthaus/Projects/GitHub/M365/registry/ai_team.json) are now authoritative in the workforce map.
- `34/59` personas are currently `registry-backed`.
- `25/59` personas are authoritative but remain `persona-contract-only` until later activation phases.
- The previous `20`-agent overflow set has been cleared from the authoritative summary; `non_authoritative_registry_agents = 0`.

## Department Summary

| Department | Personas | Primary workload families | Current coverage | Approval profile mix |
| --- | --- | --- | --- | --- |
| `operations` | `10` | Identity, directory, and tenant administration, Content, intranet, and files, Collaboration, meetings, and communities, Media, publishing, and extended communications | `2 registry-backed / 8 contract-only` | `critical-regulated`, `high-impact`, `low-observe-create`, `medium-operational` |
| `hr` | `2` | Identity, directory, and tenant administration, Documents, notes, and workspace productivity, Tasks, scheduling, and work management, Security, compliance, and data governance | `1 registry-backed / 1 contract-only` | `critical-regulated`, `high-impact` |
| `communication` | `4` | Mail, calendar, contacts, and bookings, Collaboration, meetings, and communities, Media, publishing, and extended communications, Tasks, scheduling, and work management | `1 registry-backed / 3 contract-only` | `high-impact`, `low-observe-create`, `medium-operational` |
| `engineering` | `8` | Low-code, workflow, and analytics, Documents, notes, and workspace productivity, Content, intranet, and files, Devices, endpoint management, and adjacent Windows admin surfaces | `7 registry-backed / 1 contract-only` | `low-observe-create`, `medium-operational` |
| `marketing` | `8` | Media, publishing, and extended communications, Low-code, workflow, and analytics, Documents, notes, and workspace productivity, Knowledge, search, and employee experience | `2 registry-backed / 6 contract-only` | `low-observe-create`, `medium-operational` |
| `product` | `3` | Tasks, scheduling, and work management, Knowledge, search, and employee experience, Low-code, workflow, and analytics | `3 registry-backed / 0 contract-only` | `low-observe-create` |
| `project-management` | `5` | Tasks, scheduling, and work management, Collaboration, meetings, and communities, Documents, notes, and workspace productivity | `3 registry-backed / 2 contract-only` | `low-observe-create`, `medium-operational` |
| `studio-operations` | `9` | Low-code, workflow, and analytics, Security, compliance, and data governance, Devices, endpoint management, and adjacent Windows admin surfaces, Mail, calendar, contacts, and bookings | `5 registry-backed / 4 contract-only` | `critical-regulated`, `high-impact`, `low-observe-create`, `medium-operational` |
| `testing` | `5` | Low-code, workflow, and analytics, Tasks, scheduling, and work management, Knowledge, search, and employee experience | `5 registry-backed / 0 contract-only` | `low-observe-create`, `medium-operational` |
| `design` | `5` | Media, publishing, and extended communications, Content, intranet, and files, Documents, notes, and workspace productivity, Knowledge, search, and employee experience | `5 registry-backed / 0 contract-only` | `low-observe-create` |

## Department-to-Persona Mapping

### Operations

- `Marcus Chen / m365-administrator`
  - capability families: user lifecycle and licensing, groups and workspace administration, SharePoint site, list, and file administration, directory and app governance
  - approval posture: `high-impact`
  - coverage status: `registry-backed`
- `Elena Rodriguez / website-manager`
  - capability families: website publishing and content lifecycle, production deployment coordination, analytics and SEO changes
  - approval posture: `medium-operational`
  - coverage status: `registry-backed`
- `Naomi Brooks / audit-operations`
  - capability families: directory audit review, sign-in evidence review, provisioning audit tracking
  - approval posture: `high-impact`
  - coverage status: `persona-contract-only`
- `Farah Alvi / compliance-monitoring-agent`
  - capability families: compliance assessment coordination, policy validation, violation reporting and remediation planning
  - approval posture: `critical-regulated`
  - coverage status: `persona-contract-only`
- `Connor Walsh / device-management`
  - capability families: managed device inventory, device compliance review, endpoint action coordination
  - approval posture: `medium-operational`
  - coverage status: `persona-contract-only`
- `Amara Okoye / identity-security`
  - capability families: conditional access governance, named location governance, identity hardening change control
  - approval posture: `critical-regulated`
  - coverage status: `persona-contract-only`
- `Peter Novak / it-operations-manager`
  - capability families: infrastructure monitoring, health-check coordination, alert and backup response
  - approval posture: `high-impact`
  - coverage status: `persona-contract-only`
- `Tunde Adeyemi / security-operations`
  - capability families: security alert triage, incident investigation, secure score monitoring
  - approval posture: `high-impact`
  - coverage status: `persona-contract-only`
- `Chloe Martin / service-health`
  - capability families: service health monitoring, message center tracking, escalation coordination
  - approval posture: `low-observe-create`
  - coverage status: `persona-contract-only`
- `Omar El-Masry / ucp-administrator`
  - capability families: tier administration, tenant config governance, audit-log review
  - approval posture: `critical-regulated`
  - coverage status: `persona-contract-only`

### Hr

- `Sarah Williams / hr-generalist`
  - capability families: onboarding and offboarding, employee record updates, review orchestration, HR policy lifecycle
  - approval posture: `critical-regulated`
  - coverage status: `registry-backed`
- `Camila Torres / recruitment-assistance-agent`
  - capability families: candidate screening, interview coordination, offer and onboarding preparation
  - approval posture: `high-impact`
  - coverage status: `persona-contract-only`

### Communication

- `David Park / outreach-coordinator`
  - capability families: outbound email and mailbox campaigns, meeting coordination, follow-up orchestration, campaign launch coordination
  - approval posture: `high-impact`
  - coverage status: `registry-backed`
- `Mateo Alvarez / calendar-management-agent`
  - capability families: calendar triage and scheduling, availability and meeting coordination, conflict resolution and reminder management
  - approval posture: `low-observe-create`
  - coverage status: `persona-contract-only`
- `Hannah Kim / email-processing-agent`
  - capability families: mail triage and classification, response drafting and routing, follow-up scheduling
  - approval posture: `medium-operational`
  - coverage status: `persona-contract-only`
- `Alicia Nguyen / teams-manager`
  - capability families: teams workspace governance, channel lifecycle administration, chat and collaboration coordination
  - approval posture: `medium-operational`
  - coverage status: `persona-contract-only`

### Engineering

- `Alex Thompson / ai-engineer`
  - capability families: automation and agent workflow design, model evaluation and experiment analysis, internal knowledge synthesis
  - approval posture: `medium-operational`
  - coverage status: `registry-backed`
- `Jordan Kim / backend-architect`
  - capability families: service architecture and integration contracts, API and data-model design, governance-aware backend change planning
  - approval posture: `medium-operational`
  - coverage status: `registry-backed`
- `Casey Johnson / devops-automator`
  - capability families: environment automation, CI/CD orchestration, infrastructure and release automation
  - approval posture: `medium-operational`
  - coverage status: `registry-backed`
- `Riley Martinez / frontend-developer`
  - capability families: dashboard and UI implementation, component and design-system changes, frontend release preparation
  - approval posture: `low-observe-create`
  - coverage status: `registry-backed`
- `Taylor Brown / mobile-app-builder`
  - capability families: mobile workflow implementation, app packaging and release preparation, device-facing experience changes
  - approval posture: `low-observe-create`
  - coverage status: `registry-backed`
- `Ethan Rivera / rapid-prototyper`
  - capability families: prototype assembly, quick workflow validation, concept demonstration
  - approval posture: `low-observe-create`
  - coverage status: `registry-backed`
- `Grace Lee / test-writer-fixer`
  - capability families: test authoring and remediation, regression harness changes, workflow validation support
  - approval posture: `low-observe-create`
  - coverage status: `registry-backed`
- `Andre Baptiste / platform-manager`
  - capability families: client service provisioning, platform lifecycle governance, tenant status coordination
  - approval posture: `medium-operational`
  - coverage status: `persona-contract-only`

### Marketing

- `Jake Thompson / app-store-optimizer`
  - capability families: store listing optimization, metadata experiments, performance analysis
  - approval posture: `low-observe-create`
  - coverage status: `persona-contract-only`
- `Taylor Swift / content-creator`
  - capability families: content drafting, asset preparation, publication support
  - approval posture: `low-observe-create`
  - coverage status: `registry-backed`
- `Morgan Davis / growth-hacker`
  - capability families: growth experiment design, campaign analysis, funnel automation
  - approval posture: `medium-operational`
  - coverage status: `registry-backed`
- `Zoe Martinez / instagram-curator`
  - capability families: social content curation, asset scheduling, outbound publishing preparation
  - approval posture: `low-observe-create`
  - coverage status: `persona-contract-only`
- `Priya Singh / reddit-community-builder`
  - capability families: community engagement planning, post drafting, feedback harvesting
  - approval posture: `low-observe-create`
  - coverage status: `persona-contract-only`
- `Ryan O'Connor / tiktok-strategist`
  - capability families: short-form content planning, asset experimentation, channel performance analysis
  - approval posture: `low-observe-create`
  - coverage status: `persona-contract-only`
- `Jamie Lee / twitter-engager`
  - capability families: social response drafting, channel monitoring, outbound posting support
  - approval posture: `low-observe-create`
  - coverage status: `persona-contract-only`
- `Lucia Fernandez / website-operations-specialist`
  - capability families: website deployment operations, cdn and dns change coordination, performance optimization and rollback readiness
  - approval posture: `medium-operational`
  - coverage status: `persona-contract-only`

### Product

- `Sam Chen / sprint-prioritizer`
  - capability families: backlog prioritization, sprint planning, cross-team task sequencing
  - approval posture: `low-observe-create`
  - coverage status: `registry-backed`
- `Maya Patel / feedback-synthesizer`
  - capability families: feedback synthesis, customer signal consolidation, insight brief preparation
  - approval posture: `low-observe-create`
  - coverage status: `registry-backed`
- `Chris Wong / trend-researcher`
  - capability families: market scanning, trend analysis, opportunity briefs
  - approval posture: `low-observe-create`
  - coverage status: `registry-backed`

### Project Management

- `Emily Carter / experiment-tracker`
  - capability families: experiment tracking, KPI logging, status reporting
  - approval posture: `low-observe-create`
  - coverage status: `registry-backed`
- `Ben Foster / project-shipper`
  - capability families: release coordination, handoff orchestration, launch checklist management
  - approval posture: `medium-operational`
  - coverage status: `registry-backed`
- `Olivia Park / studio-producer`
  - capability families: cross-functional production planning, schedule coordination, creative delivery tracking
  - approval posture: `low-observe-create`
  - coverage status: `registry-backed`
- `Sofia Petrova / project-coordination-agent`
  - capability families: plan and task orchestration, deadline tracking, status reporting
  - approval posture: `medium-operational`
  - coverage status: `persona-contract-only`
- `Haruto Tanaka / project-manager`
  - capability families: project lifecycle governance, milestone status oversight, archive and closeout control
  - approval posture: `medium-operational`
  - coverage status: `persona-contract-only`

### Studio Operations

- `Amanda Foster / analytics-reporter`
  - capability families: dashboard and report generation, metric review, reporting pack creation
  - approval posture: `low-observe-create`
  - coverage status: `registry-backed`
- `Lisa Chang / finance-tracker`
  - capability families: budget and expense tracking, invoice and report preparation, finance control updates
  - approval posture: `high-impact`
  - coverage status: `registry-backed`
- `Jennifer Liu / infrastructure-maintainer`
  - capability families: system upkeep, backup and restore coordination, environment reliability tracking
  - approval posture: `medium-operational`
  - coverage status: `registry-backed`
- `Robert Kim / legal-compliance-checker`
  - capability families: policy validation, compliance review, legal risk checks
  - approval posture: `critical-regulated`
  - coverage status: `registry-backed`
- `Mike Rodriguez / support-responder`
  - capability families: support triage, response drafting, case coordination
  - approval posture: `low-observe-create`
  - coverage status: `registry-backed`
- `Priya Mehta / client-relationship-agent`
  - capability families: client follow-up orchestration, relationship health scoring, feedback and satisfaction analysis
  - approval posture: `medium-operational`
  - coverage status: `persona-contract-only`
- `Luis Carvalho / financial-operations-agent`
  - capability families: invoice processing coordination, expense and budget control tracking, forecast update preparation
  - approval posture: `critical-regulated`
  - coverage status: `persona-contract-only`
- `Leah Goldstein / knowledge-management-agent`
  - capability families: document indexing, search optimization, training and expert routing
  - approval posture: `low-observe-create`
  - coverage status: `persona-contract-only`
- `Youssef Haddad / reports`
  - capability families: usage reporting, activity analytics, kpi reporting packs
  - approval posture: `low-observe-create`
  - coverage status: `persona-contract-only`

### Testing

- `Nina Shah / api-tester`
  - capability families: API validation, service certification, regression execution
  - approval posture: `low-observe-create`
  - coverage status: `registry-backed`
- `Omar Haddad / performance-benchmarker`
  - capability families: performance measurement, benchmark reporting, workload comparison
  - approval posture: `low-observe-create`
  - coverage status: `registry-backed`
- `Sofia Alvarez / test-results-analyzer`
  - capability families: test evidence synthesis, failure clustering, QA reporting
  - approval posture: `low-observe-create`
  - coverage status: `registry-backed`
- `Liam Nguyen / tool-evaluator`
  - capability families: tool comparison, workflow-fit evaluation, adoption recommendations
  - approval posture: `low-observe-create`
  - coverage status: `registry-backed`
- `Ava Johnson / workflow-optimizer`
  - capability families: process analysis, workflow tuning, automation opportunity mapping
  - approval posture: `medium-operational`
  - coverage status: `registry-backed`

### Design

- `Isabella Rossi / brand-guardian`
  - capability families: brand policy review, asset approval, outward-facing consistency checks
  - approval posture: `low-observe-create`
  - coverage status: `registry-backed`
- `Noah Anderson / ui-designer`
  - capability families: interface design, component specs, interaction polishing
  - approval posture: `low-observe-create`
  - coverage status: `registry-backed`
- `Mila Novak / ux-researcher`
  - capability families: user research synthesis, insight capture, interview and study coordination
  - approval posture: `low-observe-create`
  - coverage status: `registry-backed`
- `Diego Alvarez / visual-storyteller`
  - capability families: visual narrative creation, presentation and story asset production, campaign visual design
  - approval posture: `low-observe-create`
  - coverage status: `registry-backed`
- `Luna Park / whimsy-injector`
  - capability families: delight and tone improvements, polish passes, creative variation generation
  - approval posture: `low-observe-create`
  - coverage status: `registry-backed`

## What H3 Resolves

- all `20` promoted personas now exist inside the authoritative workforce map
- the capability map and risk posture now cover all `59` authoritative personas
- the old non-authoritative overflow summary is cleared
- the promoted personas remain bounded and non-active until H5

## What H3 Does Not Yet Resolve

- final activation of the `20` promoted personas
- final active-surface commercialization truth
- workforce packaging and final release claims

Those remain for H4 and H5.
