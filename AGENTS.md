# SmartHaus M365 AI Workforce - AI Agent Specifications

This document defines the mandatory operating rules and workflow for all AI assistants (Codex, Composer, GPT-5, and external agents) working on the SmartHaus M365 AI Workforce repository.

---

## 🚨 MANDATORY: All Agents Must Follow This Workflow

**CRITICAL:** Before ANY work, ALL agents MUST follow the complete mandatory workflow defined in `.cursor/rules/agent-workflow-mandatory.mdc`.

**CRITICAL:** ALL agents MUST follow ALL rules in `.cursor/rules/*.mdc`. These rules are MANDATORY and apply to all work.

### Quick Reference

1. **Read North Star:** `Operations/NORTHSTAR.md` - EVERYTHING must align
2. **Check Execution Plan:** `Operations/EXECUTION_PLAN.md` - Work must be in plan
3. **Follow Workflow:** `.cursor/rules/agent-workflow-mandatory.mdc` - Complete workflow
4. **Follow All Rules:** `.cursor/rules/*.mdc` - ALL rules are MANDATORY
5. **Log Actions:** `Operations/ACTION_LOG.md` - Every action must be logged
6. **Update Progress:** `Operations/EXECUTION_PLAN.md` - Update when tasks complete

---

## Mandatory Rules (All Agents)

**CRITICAL:** ALL rules in `.cursor/rules/*.mdc` are MANDATORY. Codex and all AI assistants MUST follow every rule file in that directory. No exceptions.

**All .mdc Rules Apply:**

- `.cursor/rules/agent-workflow-mandatory.mdc` - Complete workflow (START HERE)
- `.cursor/rules/north-star-alignment.mdc` - North Star alignment check
- `.cursor/rules/plan-first-execution.mdc` - Plan-first execution
- `.cursor/rules/action-log-requirement.mdc` - Action log updates
- `.cursor/rules/post-work-enforcement.mdc` - Post-work checklist verification
- `.cursor/rules/rsf-change-approval.mdc` - Change approval protocol
- `.cursor/rules/ma-process-mandatory.mdc` - Mathematical Autopsy process (v2+ only - for algorithms/matching)
- `.cursor/rules/pre-commit-workflow.mdc` - Pre-commit validation
- `.cursor/rules/codex-prompt-creation.mdc` - Codex prompt creation
- `.cursor/rules/identify-document-plan-approve.mdc` - Identify, document, plan, approve
- `.cursor/rules/fix-problems-no-workarounds.mdc` - Fix root causes
- `.cursor/rules/testing-no-workarounds.mdc` - Test real implementations (Firebase emulators acceptable)
- `.cursor/rules/no-unsolicited-execution.mdc` - DO NOT execute commands/tests without explicit permission
- `.cursor/rules/question-answer-protocol.mdc` - Answer questions first, then ask about action (MANDATORY)
- `.cursor/rules/long-running-test-setup.mdc` - Progress monitoring for long-running tests (may not apply to v1)
- `.cursor/rules/notebook-first-mandatory.mdc` - Notebook-first development (v2+ only - for algorithms)
- `.cursor/rules/notebook-error-fix-protocol.mdc` - Notebook error fix protocol (v2+ only)
- `.cursor/rules/project-file-index-enforcement.mdc` - Project file index enforcement (MANDATORY)
- All other `.cursor/rules/*.mdc` files

**Codex MUST:** Read and follow ALL `.cursor/rules/*.mdc` files. These rules are not optional.

### 1. North Star Alignment (MANDATORY)

**Rule:** `.cursor/rules/north-star-alignment.mdc`

**Requirements:**

- ✅ Read `Operations/NORTHSTAR.md` BEFORE starting ANY work
- ✅ Verify work aligns with North Star vision, goals, and metrics
- ✅ STOP if misaligned - explain and propose alternatives
- ✅ Document alignment check in action log

**North Star Document:** `Operations/NORTHSTAR.md`

**Key Metrics:**

- 39 AI agent personas managing Microsoft 365 operations
- M365-only tooling (SharePoint, Teams, Power Automate, Power BI, Outlook, Azure AD)
- Self-service platform (SMARTHAUS maintenance-only)
- Zero extra software cost (M365 tools only)
- Department-based organization (10 departments, 39 agents)
- Automation targets: 90% task automation, 50% manual reduction
- Quality metrics: 99.9% uptime, <2s response time, 100% security compliance

---

### 2. Plan-First Execution (MANDATORY)

**Rule:** `.cursor/rules/plan-first-execution.mdc`

**Requirements:**

- ✅ Check `Operations/EXECUTION_PLAN.md` FIRST before any work
- ✅ Verify work is in execution plan (`Operations/EXECUTION_PLAN.md` is PRIMARY; `/plans/` is OPTIONAL - only for large initiatives)
- ✅ Reference plan item: `plan:{plan-id}:{requirement-id}`
- ✅ STOP if no plan exists - create plan and get approval

**Execution Plan:** `Operations/EXECUTION_PLAN.md`

**Plan Format:**

- Main plan: `Operations/EXECUTION_PLAN.md`
- Detailed plans: `/plans/{plan-name}/` (Markdown, YAML, JSON)

---

### 3. Action Log Requirement (MANDATORY)

**Rule:** `.cursor/rules/action-log-requirement.mdc`

**Requirements:**

- ✅ Update `Operations/ACTION_LOG.md` after EVERY action
- ✅ Include North Star alignment check result
- ✅ Include execution plan reference
- ✅ Update `Operations/EXECUTION_PLAN.md` if milestone-related

**Action Log:** `Operations/ACTION_LOG.md`

**Log Format:**

```
YYYY-MM-DD HH:MM:SS TZ — Brief description: detailed explanation with plan reference and North Star alignment.
```

**Time Zone Requirement:**

- **MUST use local machine's timezone** for date/time stamping
- Use the timezone abbreviation from the local machine (e.g., EST, PST, UTC, etc.)
- Do NOT hardcode a specific timezone; use the actual local timezone where the action is being performed

**Example:**

```
2025-01-06 14:30:00 EST — Completed user service implementation: plan:execution_plan:user-service; aligned with North Star app-first goals; created user-service with Firebase integration; updated Operations/EXECUTION_PLAN.md to mark service complete.
```

**Note:** The timezone in the example (EST) is shown for illustration. Use your local machine's actual timezone when creating log entries.

---

### 4. Change Approval Protocol (MANDATORY for Write Operations)

**Rule:** `.cursor/rules/rsf-change-approval.mdc`

**Requirements:**

- ✅ **North Star Alignment:** Explicit statement of alignment check result
- ✅ **Plan Verification:** Explicit statement of plan verification result with plan references
- ✅ **Explain:** Root cause, impact, scope
- ✅ **Propose:** Planned edits (with plan references in format `plan:[plan-id]:[req-id]`), risks, validation plan, rollback
- ✅ **Await approval:** Explicitly ask "If you're good with this plan, reply 'go'..." - NO changes until user replies "go"
- ✅ **Implement:** Apply edits exactly as approved
- ✅ **Validate:** Run tests/checks; report results
- ✅ **Report:** Short summary of changes and outcomes

**Format:** Must use explicit section headers and follow the complete example format in `.cursor/rules/rsf-change-approval.mdc`

**Note:** Read-only operations skip this step.

---

### 5. Mathematical Autopsy (MA) Process (MANDATORY for Math/Algorithm Changes)

**Rule:** `.cursor/rules/ma-process-mandatory.mdc`

**Requirements:**

- ✅ Complete MA Phases 1-5 BEFORE code implementation (for matching algorithms, pricing models, recommendation engines)
- ✅ Phase 1: Intent & Description
- ✅ Phase 2: Mathematical Foundation
- ✅ Phase 3: Lemma Development (Invariant + Lemma)
- ✅ Phase 4: Verification (Notebook-first)
- ✅ Phase 5: CI Enforcement

**Exception:** Trivial bugfixes, UI changes, and non-algorithmic features don't require MA process.

**Reference:** `.cursor/rules/ma-process-mandatory.mdc` for complete details

---

### 6. Pre-Commit Workflow (MANDATORY)

**Rule:** `.cursor/rules/pre-commit-workflow.mdc`

**Requirements:**

- ✅ Run `pre-commit run --all-files` before committing
- ✅ Or run `make lint-all && make test` if pre-commit not available
- ✅ Fix all issues before committing
- ✅ Never skip validation for code changes

---

### 7. Question-Answer Protocol (MANDATORY)

**Rule:** `.cursor/rules/question-answer-protocol.mdc`

**Requirements:**

- ✅ When user asks a question: Answer it completely, then STOP
- ✅ DO NOT take any action (no code changes, no file edits, no commands)
- ✅ Ask explicitly: "Would you like me to [action]?" before taking any action
- ✅ Distinguish questions (information requests) from action requests (direct instructions)

**Purpose:**

- Prevents taking action when user only wants information
- Gives user control over when actions happen
- Respects user intent: questions = information, not action requests

**Reference:** `.cursor/rules/question-answer-protocol.mdc` for complete details and examples

---

### 8. Codex Prompt Creation (MANDATORY)

**Rule:** `.cursor/rules/codex-prompt-creation.mdc`

**Requirements:**

- ✅ Create detailed prompt document: `docs/prompts/codex-{plan-name}.md` (full implementation guide)
- ✅ Create short kick-off text: `docs/prompts/codex-{plan-name}-prompt.txt` (brief pointer to detailed prompt)
- ✅ Kick-off text must be brief (5-10 lines) and only point to detailed prompt
- ✅ Never duplicate detailed instructions in kick-off text
- ✅ Kick-off text includes plan reference and approval statement

**Purpose:**

- Detailed prompt = implementation guide (read by Codex)
- Kick-off text = execution trigger (copy-pasted by user to Codex)

**Reference:** `.cursor/rules/codex-prompt-creation.mdc` for complete process and template

---

## Complete Workflow Reference

**Primary Workflow:** `.cursor/rules/agent-workflow-mandatory.mdc`

**Workflow Steps:**

### Pre-Work (MANDATORY):

1. **North Star Alignment Check** - Read `Operations/NORTHSTAR.md`, verify alignment
2. **Execution Plan Verification** - Check `Operations/EXECUTION_PLAN.md`, verify work is in plan
3. **Change Approval** - Get approval if write operations (Step 3)

### During Work:

4. **Execute Work** - Follow plan, maintain North Star alignment

### Post-Work (MANDATORY):

5. **Update Action Log** - Update `Operations/ACTION_LOG.md` with plan reference and alignment
6. **Update Execution Plan** - Update `Operations/EXECUTION_PLAN.md` if milestone-related
7. **Update Execution Plan Progress** - Update `Operations/EXECUTION_PLAN.md` if task completed
8. **Verify Post-Work Checklist** - Explicitly verify all applicable post-work steps are complete

---

## Document Hierarchy (Source of Truth Order)

1. **`Operations/NORTHSTAR.md`** - Vision, goals, metrics (EVERYTHING must align)
2. **`Operations/EXECUTION_PLAN.md`** - Planned work (work must be in plan)
3. **`Operations/ACTION_LOG.md`** - Granular history (every action logged)
4. **`/plans/`** - Detailed execution plans (specific implementations)

**If disagreement: North Star wins.**

---

## Codex-Specific Rules

**Codex Operating Rule:** `codex/CODEX_OPERATING_RULE.mdc`
**Codex Profile:** `codex/CODEX_PROFILE.md`
**Codex Playbook:** `codex/CODEX_PLAYBOOK.md`

Codex agents must also follow:

- Context awareness (read files, never assume)
- Minimal scope / least-diff principle
- Patch-first requirement
- Verification-first principle
- Architecture preservation
- Security & secret handling
- Notebook-first development (for algorithms/matching code)

---

## Enforcement

**MANDATORY:** These rules apply to:

- ✅ All Codex agents (via this file and `codex/CODEX_OPERATING_RULE.mdc`)
- ✅ All Cursor AI assistants (via `.cursor/rules/`)
- ✅ All external agents accessing the repository
- ✅ All automated systems performing work

**Verification Checklist:**

Before work:

- [ ] North Star alignment checked (`Operations/NORTHSTAR.md`)
- [ ] Execution plan verified (`Operations/EXECUTION_PLAN.md`)
- [ ] Plan reference obtained
- [ ] Approval obtained (if write operations)

After work:

- [ ] Action log updated (`Operations/ACTION_LOG.md`) - Step 5 (MANDATORY)
- [ ] Execution plan updated (`Operations/EXECUTION_PLAN.md`) - Step 6 (if milestone-related)
- [ ] Task progress updated (`Operations/EXECUTION_PLAN.md`) - Step 7 (if task completed)
- [ ] Post-work checklist verified - Step 8 (MANDATORY)

**CRITICAL:** Work is NOT complete until Step 8 verification confirms all applicable steps are done.

---

## Related Documents

- **Mandatory Workflow:** `.cursor/rules/agent-workflow-mandatory.mdc` ⭐ **START HERE**
- **North Star:** `Operations/NORTHSTAR.md`
- **Execution Plan:** `Operations/EXECUTION_PLAN.md`
- **Action Log:** `Operations/ACTION_LOG.md`
- **Codex Rules:** `codex/CODEX_OPERATING_RULE.mdc`
- **Codex Profile:** `codex/CODEX_PROFILE.md`
- **Codex Playbook:** `codex/CODEX_PLAYBOOK.md`

---

## Quick Start for New Agents

1. **Read this file** (`AGENTS.md`) - Understand agent requirements
2. **Read North Star** (`Operations/NORTHSTAR.md`) - Understand vision and goals
3. **Read Execution Plan** (`Operations/EXECUTION_PLAN.md`) - Understand planned work
4. **Read Mandatory Workflow** (`.cursor/rules/agent-workflow-mandatory.mdc`) - Understand complete workflow
5. **Follow workflow** - Never skip steps

---

**Last Updated:** 2025-01-06
**Version:** 1.0


---

## MCP Constraint Enforcement (MANDATORY when MCP server available)

Before ANY write or mutating action, call the `validate_action` MCP tool provided by the SmartHaus MCP server.

**Parameters:** `repo`, `action_type`, `target`, `scope`, `plan_ref`, `approval`, `branch`, `metadata`.

**Verdict:** If `allowed` is `false`, STOP immediately and report violations. If `allowed` is `true`, proceed.

**Action types:** `file_edit`, `commit`, `push`, `deploy`, `test_run`, `command_exec`, `config_change`, `governance_edit`.

**Scopes:** `code`, `config`, `docs`, `governance`, `infrastructure`, `math`, `test`.

Use `constraint_status` to inspect loaded constraints before planning changes.

**Rule file:** `.cursor/rules/governance/mcp-constraint-enforcement.mdc`
