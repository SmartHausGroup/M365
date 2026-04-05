# SMARTHAUS M365 Department and Persona Census

## Purpose

Lock the staged authoritative workforce roster so all capability, certification, release-gate, and activation work uses one department and persona census.

## Authority

- Primary roster source: `registry/ai_team.json`
- Authoritative registry source: `registry/persona_registry_v2.yaml`
- Runtime cross-check source: `registry/agents.yaml`
- Plan reference: `plan:m365-authoritative-persona-certification-and-count-rebase:R3`

## Locked Census

- Department count: `10`
- Persona count: `59`
- Active personas: `34`
- Planned personas: `25`
- Source-of-truth roster version: `registry/ai_team.json` as rebased through H3 and preserved by H4 on `2026-04-05`

## Validation Findings

- The authoritative census now reflects `59` named digital employees across the existing `10`-department model.
- The staged activation boundary remains `34` active personas and `25` planned personas until H5 closes the activation gate.
- All `59` authoritative persona IDs resolve in `registry/agents.yaml`.
- Department totals reconcile to the rebased H4S department-pack authority and the H4 certification contracts.

## Department Roster

### operations

- `Marcus Chen` — `m365-administrator` — `Senior IT Administrator`
- `Elena Rodriguez` — `website-manager` — `Website Manager`
- `Naomi Brooks` — `audit-operations` — `Audit Operations Lead`
- `Farah Alvi` — `compliance-monitoring-agent` — `Compliance Monitoring Lead`
- `Connor Walsh` — `device-management` — `Endpoint Operations Administrator`
- `Amara Okoye` — `identity-security` — `Identity Security Administrator`
- `Peter Novak` — `it-operations-manager` — `IT Operations Manager`
- `Tunde Adeyemi` — `security-operations` — `Security Operations Lead`
- `Chloe Martin` — `service-health` — `Service Reliability Coordinator`
- `Omar El-Masry` — `ucp-administrator` — `UCP Control Plane Administrator`

### hr

- `Sarah Williams` — `hr-generalist` — `HR Director`
- `Camila Torres` — `recruitment-assistance-agent` — `Recruiting Coordinator`

### communication

- `David Park` — `outreach-coordinator` — `Communications Manager`
- `Mateo Alvarez` — `calendar-management-agent` — `Calendar Operations Coordinator`
- `Hannah Kim` — `email-processing-agent` — `Email Operations Specialist`
- `Alicia Nguyen` — `teams-manager` — `Teams Collaboration Administrator`

### engineering

- `Alex Thompson` — `ai-engineer` — `ML Engineer`
- `Jordan Kim` — `backend-architect` — `Principal Backend Engineer`
- `Casey Johnson` — `devops-automator` — `DevOps Engineer`
- `Riley Martinez` — `frontend-developer` — `UI/UX Developer`
- `Taylor Brown` — `mobile-app-builder` — `Mobile Engineer`
- `Ethan Rivera` — `rapid-prototyper` — `Prototype Engineer`
- `Grace Lee` — `test-writer-fixer` — `Test Engineer`
- `Andre Baptiste` — `platform-manager` — `Platform Engineering Manager`

### marketing

- `Jake Thompson` — `app-store-optimizer` — `ASO Specialist`
- `Taylor Swift` — `content-creator` — `Content Strategist`
- `Morgan Davis` — `growth-hacker` — `Growth Lead`
- `Zoe Martinez` — `instagram-curator` — `Visual Content Specialist`
- `Priya Singh` — `reddit-community-builder` — `Community Manager`
- `Ryan O'Connor` — `tiktok-strategist` — `Short-form Video Expert`
- `Jamie Lee` — `twitter-engager` — `Social Media Director`
- `Lucia Fernandez` — `website-operations-specialist` — `Website Operations Specialist`

### product

- `Sam Chen` — `sprint-prioritizer` — `Product Manager`
- `Maya Patel` — `feedback-synthesizer` — `User Research Lead`
- `Chris Wong` — `trend-researcher` — `Market Analyst`

### project-management

- `Emily Carter` — `experiment-tracker` — `Experimentation PM`
- `Ben Foster` — `project-shipper` — `Release Manager`
- `Olivia Park` — `studio-producer` — `Studio Producer`
- `Sofia Petrova` — `project-coordination-agent` — `Project Coordinator`
- `Haruto Tanaka` — `project-manager` — `Project Manager`

### studio-operations

- `Amanda Foster` — `analytics-reporter` — `Data Scientist`
- `Lisa Chang` — `finance-tracker` — `Chief Financial Officer`
- `Jennifer Liu` — `infrastructure-maintainer` — `Site Reliability Engineer`
- `Robert Kim` — `legal-compliance-checker` — `Legal Counsel`
- `Mike Rodriguez` — `support-responder` — `Customer Success Manager`
- `Priya Mehta` — `client-relationship-agent` — `Client Relationship Manager`
- `Luis Carvalho` — `financial-operations-agent` — `Financial Operations Manager`
- `Leah Goldstein` — `knowledge-management-agent` — `Knowledge Operations Lead`
- `Youssef Haddad` — `reports` — `Reporting and KPI Analyst`

### testing

- `Nina Shah` — `api-tester` — `QA Automation Lead`
- `Omar Haddad` — `performance-benchmarker` — `Performance Engineer`
- `Sofia Alvarez` — `test-results-analyzer` — `Quality Analyst`
- `Liam Nguyen` — `tool-evaluator` — `Dev Tools Strategist`
- `Ava Johnson` — `workflow-optimizer` — `Process Engineer`

### design

- `Isabella Rossi` — `brand-guardian` — `Brand Guardian`
- `Noah Anderson` — `ui-designer` — `UI Designer`
- `Mila Novak` — `ux-researcher` — `UX Researcher`
- `Diego Alvarez` — `visual-storyteller` — `Visual Storyteller`
- `Luna Park` — `whimsy-injector` — `Delight Designer`

## Next Dependency

`H5` is the next governed act. It may not activate the `25` planned personas until the staged H4 count and certification truth remains green.
