### Cursor CLI Autonomous Agent Rollout Plan (M365 Project)

Reference: [Cursor CLI](https://cursor.com/cli)

This plan enables agents to autonomously perform scoped code changes via Cursor CLI, triggered by CI events or Microsoft Teams messages, with strict guardrails, auditability, and quality gates. Use the checkboxes to track execution.

---

## Phase 0 — Scope, Ownership, and Risk Model

- [ ] Define primary use-cases and scope
  - [ ] Low-risk website edits in `smarthaus.ai/app/**`
  - [ ] Docs updates in `docs/**`
  - [ ] Small Node changes in `api/**` guarded by tests
  - [ ] Python service edits in `src/**` guarded by tests
- [ ] Establish owners and escalation
  - [ ] Product owner
  - [ ] Tech reviewer(s) per area (CODEOWNERS)
  - [ ] On-call rotational approver
- [ ] Risk classification and deployment policy
  - [ ] PR-only mode; no direct merges to protected branches
  - [ ] Mandatory CI checks for all agent PRs
  - [ ] Auto-merge allowed only for low-risk paths and green checks
- [ ] Define measurable success metrics
  - [ ] Mean time from request-to-PR
  - [ ] PR acceptance rate without human edits
  - [ ] Incidents/regressions attributable to agent changes

Acceptance criteria:
- [ ] Written scope doc approved in repo
- [ ] CODEOWNERS align with intended review routing
- [ ] Metrics defined and dashboarded (stub acceptable)

---

## Phase 1 — Foundations and Environment

- [ ] Install Cursor CLI in CI and dev environments
  - [ ] Add install step: `curl https://cursor.com/install -fsS | bash` (headless)
  - [ ] Verify `cursor-agent --help` and version output
- [ ] Runtime prerequisites
  - [ ] Node.js version aligned with `package.json`/`engines` (nvm pin)
  - [ ] Python version per `pyproject.toml`/`requirements.txt`
  - [ ] `gh` CLI installed and authenticated (for PR creation)
  - [ ] Git configured with bot identity (name/email)
- [ ] Repository protections
  - [ ] Protect `main` and release branches
  - [ ] Require PR reviews from CODEOWNERS
  - [ ] Require status checks (tests, lint, OPA policy)
  - [ ] Enforce signed commits (if policy)
- [ ] Credentials and secrets
  - [ ] Configure CI with least-privilege tokens
  - [ ] Store any required API keys as CI secrets (never in repo)
  - [ ] Limit token scopes to repo content/PRs only

Acceptance criteria:
- [ ] CI runner can execute `cursor-agent` in a dry-run
- [ ] Protected branch rules active; unprotected merges blocked
- [ ] Bot identity appears on test commits to a sandbox branch

---

## Phase 2 — CI Integration and Agent Wrapper

- [ ] Add an agent wrapper script `scripts/agent_wrapper.sh`
  - [ ] Creates ephemeral branch (`agent/<id>-<timestamp>`)
  - [ ] Invokes `cursor-agent` with strict constraints (paths, deliverables)
  - [ ] Captures run output to artifact (e.g., `cursor-run.txt`)
  - [ ] Runs tests and lints; summarizes results
  - [ ] Pushes branch and creates PR with labels and template
- [ ] Add GitHub Actions workflow `.github/workflows/agent-task.yml`
  - [ ] Triggers:
    - [ ] `workflow_dispatch` with `task` input
    - [ ] `issue_comment` for `/agent <instruction>` commands
    - [ ] Optional trigger on CI failures for “auto-fix attempt” (opt-in)
  - [ ] Steps:
    - [ ] Checkout, tool install, environment setup
    - [ ] Run `scripts/agent_wrapper.sh` with prompt
    - [ ] Upload artifacts (`cursor-run.txt`, diff summary)
  - [ ] Concurrency and timeouts:
    - [ ] `concurrency: group: agent-${{ github.ref }}`
    - [ ] Job timeout (e.g., 20–30 min)
  - [ ] Labels: `agent`, `automated`, area labels per path
- [ ] PR Template `.github/pull_request_template.md` (What/Why/Tests/Risks)
- [ ] Commit message convention for agent commits (e.g., `agent: …`)

Acceptance criteria:
- [ ] Manual dispatch produces a PR with proper summary and artifacts
- [ ] All PR checks run automatically and block merge on failure
- [ ] Wrapper prevents edits outside allowlisted paths

---

## Phase 3 — Microsoft Teams Command Ingestion

- [ ] Bot/App Registration in Azure AD
  - [ ] Register app, permissions for receiving messages
  - [ ] Configure webhook endpoint and secrets
- [ ] Teams channel and governance
  - [ ] Dedicated channel (e.g., `#agent-requests`)
  - [ ] Allow only authorized users to issue commands
  - [ ] Retain message history for audit
- [ ] Message → Task translation service
  - [ ] Implement handler in `src/ops_adapter/`:
    - [ ] Parse command: `Agent Website: <instruction>`
    - [ ] Validate intent and map to allowed path set
    - [ ] Expand into canonical prompt with constraints and acceptance tests
    - [ ] Invoke GitHub Action `agent-task.yml` with the prompt
  - [ ] Include request correlation ID in PR and logs
- [ ] Response back to Teams
  - [ ] Post PR link, diff summary, test status
  - [ ] Post final outcome (merged/closed) with changelog snippet

Acceptance criteria:
- [ ] Teams command creates a PR within minutes
- [ ] Response includes links and artifacts
- [ ] Unauthorized or out-of-scope requests are rejected with explanation

---

## Phase 4 — Guardrails and Policy Enforcement

- [ ] Path allowlist
  - [ ] Website: `smarthaus.ai/app/**`
  - [ ] Docs: `docs/**`
  - [ ] Node: `api/**` (minor/low-risk only)
  - [ ] Python: `src/**` (minor/low-risk only)
- [ ] Change constraints
  - [ ] Max changed files per PR (e.g., 10)
  - [ ] Max diff size (e.g., 2,000 lines)
  - [ ] Block binary/large files unless explicitly allowed
- [ ] Command constraints for `cursor-agent`
  - [ ] Set execution timeouts
  - [ ] Forbid shelling out to network/package install outside CI step
  - [ ] Disallow secret file reads
- [ ] Policy checks
  - [ ] OPA policy in `policies/agents/*.rego` enforced in CI (use `bin/opa`)
  - [ ] License and secret scanners run on PR
  - [ ] DLP/PII scanning for docs changes

Acceptance criteria:
- [ ] Unsafe attempts fail fast with clear error
- [ ] OPA and scanners are required checks on PRs
- [ ] Audit logs capture reasons for blocks

---

## Phase 5 — Quality Gates and Testing

- [ ] Tests
  - [ ] Python: `pytest` targeting `tests/`
  - [ ] JS/TS: lint/tests as applicable (add if missing)
  - [ ] Snapshot/visual checks where feasible for website
- [ ] Static analysis
  - [ ] ESLint/Prettier for JS/TS
  - [ ] Flake8/ruff/mypy for Python (as applicable)
- [ ] Documentation
  - [ ] Require changelog entry `CHANGELOG.md`
  - [ ] Require doc updates under `docs/` when user-facing
- [ ] PR gates
  - [ ] All above must pass or PR is blocked

Acceptance criteria:
- [ ] Red-to-green loop runs automatically in agent PRs
- [ ] Missing tests or lints are reported with guidance

---

## Phase 6 — Observability, Audit, and Reporting

- [ ] Logging
  - [ ] Append to `logs/ops_audit.log` (include request ID, actor, scope)
  - [ ] Upload run artifacts on every PR
- [ ] Monitoring
  - [ ] KQL queries in `monitoring/kql/` extended for agent runs
  - [ ] Alert on high failure rate or repeated blocks
- [ ] Reporting
  - [ ] Weekly summary: #requests, PRs opened, merged, blocked, MTTR
  - [ ] Post summary to Teams and store in repo `data/agent_logs_*.json`

Acceptance criteria:
- [ ] Dashboards or saved queries exist and are documented
- [ ] Alerts verified in a test scenario

---

## Phase 7 — Rollout and Change Management

- [ ] PoC (read-only/dry-run)
  - [ ] Diff-only PRs for website text changes
  - [ ] Manual review by owners
- [ ] Limited pilot
  - [ ] Enable PR creation for allowlisted paths
  - [ ] No auto-merge
- [ ] Gradual expansion
  - [ ] Add more paths after stable success metrics
  - [ ] Consider auto-merge for trivial content with green checks

Acceptance criteria:
- [ ] PoC PRs show correct diffs and summaries
- [ ] Pilot PRs merged without regressions

---

## Phase 8 — Security and Compliance

- [ ] Secrets hygiene
  - [ ] All secrets in CI store; no plaintext in repo
  - [ ] Rotate tokens periodically; least-privilege permissions
- [ ] Supply chain
  - [ ] Dependabot/renovate enabled
  - [ ] Pin dependencies and lockfiles
- [ ] Compliance
  - [ ] Audit trail retained (messages, artifacts, PRs)
  - [ ] Optional commit signing

Acceptance criteria:
- [ ] Security review approved
- [ ] Dependency and secret scans pass

---

## Phase 9 — Reliability, SLOs, and Runbooks

- [ ] SLOs
  - [ ] PR creation within X minutes of request (e.g., 10 min)
  - [ ] Success rate ≥ Y% for low-risk tasks (e.g., 80%)
- [ ] Runbooks
  - [ ] Build broken: revert branch, comment on PR, notify Teams
  - [ ] Stuck jobs: cancel with concurrency key and retry
  - [ ] Rollback: revert or close PR; open follow-up issue
  - [ ] Rate limits: back-off and notify requester
- [ ] Emergency stop
  - [ ] Toggle/feature flag to disable agent workflows

Acceptance criteria:
- [ ] Runbooks documented in `docs/`
- [ ] Tabletop exercise completed

---

## Phase 10 — Auto-Merge for Trivial Changes (Optional)

- [ ] Define trivial change criteria
  - [ ] Only text/content edits under `smarthaus.ai/app/**` or `docs/**`
  - [ ] All checks green; small diff; no code owners warnings
- [ ] Configure auto-merge
  - [ ] Label-based auto-merge (e.g., `automerged:trivial`)
  - [ ] Enforce size and path policy before applying label

Acceptance criteria:
- [ ] Auto-merged PRs meet criteria and pass checks
- [ ] No policy violations observed in audit

---

## Operational Details (Prompts, Conventions, and Templates)

- [ ] Prompt contract (skeleton)

```text
You are a repo-aware coding agent.
Task: <user instruction>
Constraints:
- Edit only under the following paths: <allowlist>
- Update CHANGELOG.md for user-facing changes.
- Run tests and fix failures; do not disable checks.
- Keep diffs minimal; explain rationale in PR.
Deliverables:
- Committed changes with descriptive messages.
- Open a PR titled "Agent: <task>" with summary and test results.
Context:
- Coding standards: see docs/.
- Tests: see tests/.
```

- [ ] Branch naming: `agent/<short-scope>/<req-id>-<timestamp>`
- [ ] Commit prefix: `agent: <summary>`
- [ ] PR template sections: What / Why / Tests / Risks / Screenshots (if UI)
- [ ] Labels: `agent`, area label, `automated`, optional risk label

---

## Implementation Checklist Snapshot

- [ ] Phase 0 complete
- [ ] Phase 1 complete
- [ ] Phase 2 complete
- [ ] Phase 3 complete
- [ ] Phase 4 complete
- [ ] Phase 5 complete
- [ ] Phase 6 complete
- [ ] Phase 7 complete
- [ ] Phase 8 complete
- [ ] Phase 9 complete
- [ ] Phase 10 (optional) complete

---

## Appendix — File/Component Touchpoints in This Repo

- Website: `smarthaus.ai/app/**`
- Node APIs: `api/**`
- Python services: `src/**`
- Policies: `policies/agents/*.rego`, `bin/opa`
- Monitoring & Logs: `monitoring/kql/**`, `logs/ops_audit.log`
- Scripts: `scripts/**` (add `agent_wrapper.sh`)
- Workflows: `.github/workflows/agent-task.yml`
- Teams setup helpers: `add_teams_webhooks.ps1`, `api/` and `src/ops_adapter/`

---

## Notes

- Cursor CLI is headless and script-friendly; install via:

```bash
curl https://cursor.com/install -fsS | bash
```

- Start in PR-only mode, expand scope gradually, and keep guardrails strict.
