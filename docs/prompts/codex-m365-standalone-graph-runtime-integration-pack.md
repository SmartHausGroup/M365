# Execution Prompt - M365 Standalone Graph Runtime Integration Pack

Plan Reference: `plan:m365-standalone-graph-runtime-integration-pack`
Parent Plan: `plan:m365-marketplace-bundle-packaging-conformance`
North Star: `Operations/NORTHSTAR.md`
Execution Plan: `Operations/EXECUTION_PLAN.md`
Detailed Plan: `plans/m365-standalone-graph-runtime-integration-pack/m365-standalone-graph-runtime-integration-pack.md`

## Mission

Build the governed path for a real standalone M365 Integration Pack: an installed marketplace artifact that contains the Microsoft Graph runtime service, auth setup, secure token handling, health/readiness contracts, UCP-facing contracts, read-only Graph action execution, packaging evidence, and operations/rollback support.

The current artifact is not enough. Treat it as a client/contract-only baseline. Do not claim a real Microsoft integration until the installed artifact can launch and operate without the M365 source repo.

## Mandatory Reads

Before any write, command, or test:

- `AGENTS.md`
- `.cursor/rules/*.mdc`
- `Operations/NORTHSTAR.md`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`
- `plans/m365-standalone-graph-runtime-integration-pack/m365-standalone-graph-runtime-integration-pack.md`
- `plans/m365-standalone-graph-runtime-integration-pack/m365-standalone-graph-runtime-integration-pack.yaml`
- `src/ucp_m365_pack/contracts.py`
- `src/ucp_m365_pack/client.py`
- `src/ucp_m365_pack/setup_schema.json`
- `src/m365_server/__main__.py`
- `src/smarthaus_graph/client.py`

## Governance Lock

- Present the Phase `P0` intent packet first.
- Wait for explicit CTO approval before implementation.
- Call MCP `validate_action` before every mutating action and obey the verdict.
- Keep each execution slice inside the approved phase allowlist.
- Stop on first failed invariant, failed scorecard, missing approval, source-repo dependency, or readiness over-claim.
- Update `Operations/ACTION_LOG.md`, `Operations/EXECUTION_PLAN.md`, and `Operations/PROJECT_FILE_INDEX.md` whenever the governed state changes.

## Required Recommendation Format

Use this structure before each parent phase:

```text
🥇 Decision Summary
- Short statement of choice

📊 Options Considered
- Option A with pros/cons
- Option B with pros/cons
- Option C if relevant

📈 Evaluation Criteria
- Mathematical soundness
- Deterministic guarantees
- Invariant enforceability
- Maintenance overhead
- Deployment viability

🔍 Why This Choice
- Reasoned justification in context

📌 What Risks Remain
- Explicit limitations or unresolved issues

🛠 Next Steps
- Precise actionable items
```

## Execution Order

Execute parent phases strictly in order:

1. `P0` Intent Definition And Baseline Lock
2. `P1` Governing Formula And Formal Calculus
3. `P2` Lemmas And Machine Invariants
4. `P3` Notebook Proof And Scorecard Gate
5. `P4` Runtime Service And Auth Foundation
6. `P5` Microsoft Graph Action Runtime
7. `P6` UCP Pack Contract And Local Lifecycle
8. `P7` Packaging And Distribution
9. `P8` UCP Marketplace Activation Boundary
10. `P9` Acceptance Evidence And Release
11. `P10` Operations Rollback And Maintenance

Do not auto-advance. Each parent gate needs explicit approval.

## Phase 0 Required Output

Produce the intent definition:

- What are we building?
- Why are we building it?
- What problem does it solve?
- What are boundaries and non-goals?
- What guarantees are required?
- What are success criteria?
- How is determinism defined?

Then stop for CTO approval.

## Mathematical Autopsy Requirements

The runtime implementation must emerge from MA evidence:

- `P1` formula and formal calculus.
- `P2` lemmas and invariant YAML.
- `P3` notebooks with immediate tests/assertions after each code cell.
- `P3` scorecard with notebook hash, invariant pass/fail, seed/replay certification, and extraction readiness.
- Runtime extraction only after green scorecard.

No runtime code may be written directly outside the notebook/extraction path unless the CTO formally changes the MA rule.

## Runtime Requirements

The standalone artifact must include:

- `ucp_m365_pack/` UCP-facing contracts and client.
- A local Microsoft Graph runtime service.
- A launcher or service entrypoint that runs from the installed artifact root.
- Setup schema for tenant, client, auth mode, actor, and secret references.
- Auth contract: start sign-in, check sign-in, clear sign-in, auth status.
- Health contract: service, auth/token, Graph connectivity, permissions, action registry.
- Read-only Graph action contract.
- Secure token storage policy.
- Audit and redaction policy.
- Packaging manifest, payload, checksums, signatures, provenance, and conformance evidence.

## Non-Negotiable Stop Conditions

- Do not store Microsoft usernames/passwords.
- Do not log tokens, client secrets, assertions, refresh tokens, or authorization codes.
- Do not return `Ready=true` if auth, token, Graph, permission, service, or UCP contract state is unknown.
- Do not use `M365_REPO_ROOT`, `../M365`, or sibling repo lookup from installed runtime behavior.
- Do not add write actions before a separate mutation-governance plan.
- Do not move Microsoft Graph implementation into UCP.

## Acceptance Proof

The final release decision requires:

- Installed artifact launches without the M365 source repo.
- `SHA256SUMS` passes in the local Integration Pack store.
- UCP installs and resolves the pack from the marketplace artifact.
- UCP launches the pack service from the installed artifact.
- Setup/auth/health complete through declared contracts.
- Read-only Microsoft Graph action executes through UCP into the installed pack.
- Evidence packet proves readiness without leaking secrets.

Do not implement until explicit owner approval.
