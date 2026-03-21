# SMARTHAUS M365 Department and Persona Census

## Purpose

Lock the authoritative workforce roster for the expansion program so all later capability, routing, and certification work uses one department and persona census.

## Authority

- Primary roster source: `registry/ai_team.json`
- Runtime cross-check source: `registry/agents.yaml`
- Plan reference: `plan:m365-ai-workforce-expansion-master-plan:E0A`

## Locked Census

- Department count: `10`
- Persona count: `39`
- Source-of-truth roster version: `registry/ai_team.json` as corrected on `2026-03-20`

## Validation Findings

- The roster now matches the North Star target of `39` personas across `10` departments.
- All `39` roster agent IDs resolve in `registry/agents.yaml`.
- The prior `bonus` department block was removed because it inflated the roster to `41`, created an eleventh department, and included `studio-coach` plus `joker`, neither of which exists in the runtime registry.

## Department Roster

### operations

- `Marcus Chen` — `m365-administrator` — `Senior IT Administrator`
- `Elena Rodriguez` — `website-manager` — `Website Manager`

### hr

- `Sarah Williams` — `hr-generalist` — `HR Director`

### communication

- `David Park` — `outreach-coordinator` — `Communications Manager`

### engineering

- `Alex Thompson` — `ai-engineer` — `ML Engineer`
- `Jordan Kim` — `backend-architect` — `Principal Backend Engineer`
- `Casey Johnson` — `devops-automator` — `DevOps Engineer`
- `Riley Martinez` — `frontend-developer` — `UI/UX Developer`
- `Taylor Brown` — `mobile-app-builder` — `Mobile Engineer`
- `Ethan Rivera` — `rapid-prototyper` — `Prototype Engineer`
- `Grace Lee` — `test-writer-fixer` — `Test Engineer`

### marketing

- `Jake Thompson` — `app-store-optimizer` — `ASO Specialist`
- `Taylor Swift` — `content-creator` — `Content Strategist`
- `Morgan Davis` — `growth-hacker` — `Growth Lead`
- `Zoe Martinez` — `instagram-curator` — `Visual Content Specialist`
- `Priya Singh` — `reddit-community-builder` — `Community Manager`
- `Ryan O'Connor` — `tiktok-strategist` — `Short-form Video Expert`
- `Jamie Lee` — `twitter-engager` — `Social Media Director`

### product

- `Sam Chen` — `sprint-prioritizer` — `Product Manager`
- `Maya Patel` — `feedback-synthesizer` — `User Research Lead`
- `Chris Wong` — `trend-researcher` — `Market Analyst`

### project-management

- `Emily Carter` — `experiment-tracker` — `Experimentation PM`
- `Ben Foster` — `project-shipper` — `Release Manager`
- `Olivia Park` — `studio-producer` — `Studio Producer`

### studio-operations

- `Amanda Foster` — `analytics-reporter` — `Data Scientist`
- `Lisa Chang` — `finance-tracker` — `Chief Financial Officer`
- `Jennifer Liu` — `infrastructure-maintainer` — `Site Reliability Engineer`
- `Robert Kim` — `legal-compliance-checker` — `Legal Counsel`
- `Mike Rodriguez` — `support-responder` — `Customer Success Manager`

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

`E0B` is now the next act. It must inventory the full M365 workload universe and bind that universe to this locked department and persona census.
