# SMARTHAUS Persona-to-Capability and Risk Map

## Purpose

Bind the locked `39`-persona workforce roster to explicit capability families, risk classes, and approval posture so later phases stop treating the workforce as an undifferentiated agent pool.

## Inputs

- locked roster: [m365-department-persona-census.md](/Users/smarthaus/Projects/GitHub/M365/docs/commercialization/m365-department-persona-census.md)
- workload and capability taxonomy: [m365-capability-taxonomy-and-feasibility-map.md](/Users/smarthaus/Projects/GitHub/M365/docs/commercialization/m365-capability-taxonomy-and-feasibility-map.md)
- registry action surface: [agents.yaml](/Users/smarthaus/Projects/GitHub/M365/registry/agents.yaml)
- structured E0D mapping output: [persona_capability_map.yaml](/Users/smarthaus/Projects/GitHub/M365/registry/persona_capability_map.yaml)

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

- `39/39` personas in [ai_team.json](/Users/smarthaus/Projects/GitHub/M365/registry/ai_team.json) resolve cleanly in [agents.yaml](/Users/smarthaus/Projects/GitHub/M365/registry/agents.yaml).
- Only `4/39` personas are currently `registry-backed` with explicit allowed-action surfaces:
  - `m365-administrator`
  - `website-manager`
  - `hr-generalist`
  - `outreach-coordinator`
- The remaining `35/39` personas are now bound at the contract level but still require later action-surface implementation.
- The broader action registry still contains `20` non-authoritative agents outside the locked workforce roster. They remain runtime inventory, not workforce authority, until a later plan explicitly promotes them.

## Department Summary

| Department | Personas | Primary workload families | Current coverage | Approval profile mix |
| --- | --- | --- | --- | --- |
| `operations` | `2` | identity/admin, content/files, collaboration, publishing | `2 registry-backed / 0 contract-only` | `high-impact`, `medium-operational` |
| `hr` | `1` | identity/admin, documents, work management, compliance | `1 registry-backed / 0 contract-only` | `critical-regulated` |
| `communication` | `1` | mail/calendar, collaboration, publishing, work management | `1 registry-backed / 0 contract-only` | `high-impact` |
| `engineering` | `7` | low-code/analytics, documents, files, devices/admin | `0 registry-backed / 7 contract-only` | `medium-operational`, `low-observe-create` |
| `marketing` | `7` | publishing, analytics, docs, knowledge | `0 registry-backed / 7 contract-only` | `medium-operational`, `low-observe-create` |
| `product` | `3` | work management, knowledge, analytics | `0 registry-backed / 3 contract-only` | `low-observe-create` |
| `project-management` | `3` | work management, collaboration, docs | `0 registry-backed / 3 contract-only` | `medium-operational`, `low-observe-create` |
| `studio-operations` | `5` | analytics, compliance, devices/admin, mail | `0 registry-backed / 5 contract-only` | `high-impact`, `critical-regulated`, `medium-operational`, `low-observe-create` |
| `testing` | `5` | analytics, work management, knowledge | `0 registry-backed / 5 contract-only` | `medium-operational`, `low-observe-create` |
| `design` | `5` | publishing, files, docs, knowledge | `0 registry-backed / 5 contract-only` | `low-observe-create` |

## Department-to-Persona Mapping

### Operations

- `Marcus Chen / m365-administrator`
  - capability families: user lifecycle and licensing, groups/workspace administration, SharePoint site/list/file administration, directory/app governance
  - approval posture: `high-impact`
- `Elena Rodriguez / website-manager`
  - capability families: website publishing, deployment coordination, analytics and SEO changes
  - approval posture: `medium-operational`

### HR

- `Sarah Williams / hr-generalist`
  - capability families: onboarding/offboarding, employee record updates, review orchestration, HR policy lifecycle
  - approval posture: `critical-regulated`

### Communication

- `David Park / outreach-coordinator`
  - capability families: outbound email and mailbox campaigns, meeting coordination, follow-up orchestration, campaign launch coordination
  - approval posture: `high-impact`

### Engineering

- `Alex Thompson / ai-engineer`
  - capability families: automation and agent workflow design, model evaluation, internal knowledge synthesis
  - approval posture: `medium-operational`
- `Jordan Kim / backend-architect`
  - capability families: service architecture, API/data-model design, governed integration planning
  - approval posture: `medium-operational`
- `Casey Johnson / devops-automator`
  - capability families: environment automation, CI/CD, infrastructure and release automation
  - approval posture: `medium-operational`
- `Riley Martinez / frontend-developer`
  - capability families: dashboard/UI implementation, component-system changes, frontend release preparation
  - approval posture: `low-observe-create`
- `Taylor Brown / mobile-app-builder`
  - capability families: mobile workflow implementation, packaging/release prep, device-facing experience changes
  - approval posture: `low-observe-create`
- `Ethan Rivera / rapid-prototyper`
  - capability families: prototype assembly, quick workflow validation, concept demonstration
  - approval posture: `low-observe-create`
- `Grace Lee / test-writer-fixer`
  - capability families: test authoring/remediation, regression harness changes, workflow validation support
  - approval posture: `low-observe-create`

### Marketing

- `Jake Thompson / app-store-optimizer`
  - capability families: store listing optimization, metadata experiments, performance analysis
  - approval posture: `low-observe-create`
- `Taylor Swift / content-creator`
  - capability families: content drafting, asset preparation, publication support
  - approval posture: `low-observe-create`
- `Morgan Davis / growth-hacker`
  - capability families: growth experiment design, campaign analysis, funnel automation
  - approval posture: `medium-operational`
- `Zoe Martinez / instagram-curator`
  - capability families: social content curation, asset scheduling, outbound publishing preparation
  - approval posture: `low-observe-create`
- `Priya Singh / reddit-community-builder`
  - capability families: community engagement planning, post drafting, feedback harvesting
  - approval posture: `low-observe-create`
- `Ryan O'Connor / tiktok-strategist`
  - capability families: short-form content planning, asset experimentation, channel performance analysis
  - approval posture: `low-observe-create`
- `Jamie Lee / twitter-engager`
  - capability families: social response drafting, channel monitoring, outbound posting support
  - approval posture: `low-observe-create`

### Product

- `Sam Chen / sprint-prioritizer`
  - capability families: backlog prioritization, sprint planning, cross-team task sequencing
  - approval posture: `low-observe-create`
- `Maya Patel / feedback-synthesizer`
  - capability families: feedback synthesis, customer signal consolidation, insight brief preparation
  - approval posture: `low-observe-create`
- `Chris Wong / trend-researcher`
  - capability families: market scanning, trend analysis, opportunity briefs
  - approval posture: `low-observe-create`

### Project Management

- `Emily Carter / experiment-tracker`
  - capability families: experiment tracking, KPI logging, status reporting
  - approval posture: `low-observe-create`
- `Ben Foster / project-shipper`
  - capability families: release coordination, handoff orchestration, launch checklist management
  - approval posture: `medium-operational`
- `Olivia Park / studio-producer`
  - capability families: cross-functional production planning, schedule coordination, creative delivery tracking
  - approval posture: `low-observe-create`

### Studio Operations

- `Amanda Foster / analytics-reporter`
  - capability families: dashboard/report generation, metric review, reporting pack creation
  - approval posture: `low-observe-create`
- `Lisa Chang / finance-tracker`
  - capability families: budget/expense tracking, invoice/report preparation, finance control updates
  - approval posture: `high-impact`
- `Jennifer Liu / infrastructure-maintainer`
  - capability families: system upkeep, backup/restore coordination, environment reliability tracking
  - approval posture: `medium-operational`
- `Robert Kim / legal-compliance-checker`
  - capability families: policy validation, compliance review, legal risk checks
  - approval posture: `critical-regulated`
- `Mike Rodriguez / support-responder`
  - capability families: support triage, response drafting, case coordination
  - approval posture: `low-observe-create`

### Testing

- `Nina Shah / api-tester`
  - capability families: API validation, service certification, regression execution
  - approval posture: `low-observe-create`
- `Omar Haddad / performance-benchmarker`
  - capability families: performance measurement, benchmark reporting, workload comparison
  - approval posture: `low-observe-create`
- `Sofia Alvarez / test-results-analyzer`
  - capability families: test evidence synthesis, failure clustering, QA reporting
  - approval posture: `low-observe-create`
- `Liam Nguyen / tool-evaluator`
  - capability families: tool comparison, workflow-fit evaluation, adoption recommendations
  - approval posture: `low-observe-create`
- `Ava Johnson / workflow-optimizer`
  - capability families: process analysis, workflow tuning, automation opportunity mapping
  - approval posture: `medium-operational`

### Design

- `Isabella Rossi / brand-guardian`
  - capability families: brand policy review, asset approval, outward-facing consistency checks
  - approval posture: `low-observe-create`
- `Noah Anderson / ui-designer`
  - capability families: interface design, component specs, interaction polishing
  - approval posture: `low-observe-create`
- `Mila Novak / ux-researcher`
  - capability families: user research synthesis, insight capture, interview/study coordination
  - approval posture: `low-observe-create`
- `Diego Alvarez / visual-storyteller`
  - capability families: visual narrative creation, presentation/story asset production, campaign visual design
  - approval posture: `low-observe-create`
- `Luna Park / whimsy-injector`
  - capability families: delight/tone improvements, polish passes, creative variation generation
  - approval posture: `low-observe-create`

## What E0D Resolves

`E0D` closes the first workforce-specific gap left after the taxonomy work:

- every authoritative persona now has explicit workload and capability boundaries
- every persona now has a deterministic approval profile
- the workforce no longer depends on the broader `59`-agent runtime registry as its authority surface

## What E0D Does Not Yet Resolve

- executor-domain ownership per capability family
- canonical action contract v2
- exact delegated vs app-only routing per capability family
- release-wave sequencing

Those remain for:

- `E0E` release-wave and completion mapping
- `E1A` through `E1E` control-plane expansion

