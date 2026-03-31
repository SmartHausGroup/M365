# MATHS Prompt: UCP Live Activation Repair

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-ucp-live-activation-repair:R1`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-UCP-ACTIVATION-C0` -> `M365-UCP-ACTIVATION-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:M365-UCP-ACTIVATION STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-UCP-ACTIVATION`
- Run ID: `ucp-live-activation-repair`
- Commit SHA: `<fill-at-run-time>`
- Plan refs in scope:
  - `plan:m365-ucp-live-activation-repair:R1`
  - `plan:m365-ucp-live-activation-repair:R2`
  - `plan:m365-ucp-live-activation-repair:R3`
  - `plan:m365-ucp-live-activation-repair:R4`
  - `plan:m365-ucp-live-activation-repair:R5`
  - `plan:m365-ucp-live-activation-repair:R6`
  - `plan:m365-ucp-live-activation-repair:P0A`
  - `plan:m365-ucp-live-activation-repair:P1A`
  - `plan:m365-ucp-live-activation-repair:P1B`
  - `plan:m365-ucp-live-activation-repair:P2A`
  - `plan:m365-ucp-live-activation-repair:P3A`
  - `plan:m365-ucp-live-activation-repair:P3B`
- Invariant IDs in scope: `<define during execution>`
- Lemma IDs in scope: `<define during execution>`
- Owners: `product`, `engineering`, `MA`

## Context

- Task name: `Repair live Claude -> UCP -> M365 activation and first-hop execution`
- Domain: `runtime`
- Dependencies: `the earlier UCP tenant-context repair is already in place; this act starts from the observed policy_pack activation rejection and session_not_activated cascade`
- Allowlist:
  - `/Users/smarthaus/Projects/GitHub/UCP/src/ucp/server.py`
  - `/Users/smarthaus/Projects/GitHub/UCP/src/ucp/cli.py`
  - `/Users/smarthaus/Projects/GitHub/UCP/src/ucp/api/routes_v1.py`
  - `/Users/smarthaus/Projects/GitHub/UCP/packs/policy_pack/contracts.py`
  - `/Users/smarthaus/Projects/GitHub/UCP/packs/m365_pack/client.py`
  - `/Users/smarthaus/Projects/GitHub/UCP/tests/test_m365_pack_client.py`
  - `/Users/smarthaus/Projects/GitHub/UCP/tests/test_server_pack_activation.py`
  - `/Users/smarthaus/Projects/GitHub/UCP/notebooks/runtime_contracts/*`
  - `/Users/smarthaus/Projects/GitHub/M365/plans/m365-ucp-live-activation-repair/*`
  - `/Users/smarthaus/Projects/GitHub/M365/Operations/EXECUTION_PLAN.md`
  - `/Users/smarthaus/Projects/GitHub/M365/Operations/ACTION_LOG.md`
- Denylist:
  - `Microsoft tenant permission changes unless needed only for truthful downstream classification`
  - `reopening fixed tenant-context work without regression evidence`
  - `any workaround that hides activation or policy failures behind credentials_missing`

## M - Model

- Problem: `The live runtime exposes m365 tools while policy admission blocks activate_session, which cascades into session_not_activated for real M365 calls.`
- Goal: `Make activation, session-state, and first-hop M365 execution agree on one truthful runtime state across the live Claude-compatible path.`
- Success criteria:
  - `activate_session(confirm=true) succeeds on the repaired live path`
  - `session_status, constraint_status, and validate_action remain callable after activation`
  - `m365_sites action=sites.root executes live`
  - `m365_action agent=m365-administrator action=directory.org reaches real Graph auth and returns either success or a real Graph permission error`
- Out of scope:
  - `loosening Graph permissions to hide activation defects`
  - `shipping a surface that works only in one transport while another remains contradictory`

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `The UCP runtime contracts show activation bypass, policy admission, and tool registration aligned after repair.`
- Runtime/test evidence:
  - `Retained live transcripts exist for activate_session, session_status, validate_action, m365_sites sites.root, and m365_action directory.org.`
- Governance evidence:
  - `M365 plan, prompt, execution-plan, and action-log surfaces remain synchronized.`
- Determinism evidence:
  - `Repeated live activation and first-hop runs on fixed config produce the same admission decision and the same class of downstream result.`

## T - Tie

- Dependency ties:
  - `Activation must succeed before any governed tool can be called honestly.`
  - `Tool listing is not sufficient; callable admission and execution state must agree.`
  - `sites.root is the first required live M365 proof after activation is repaired.`
- Known failure modes:
  - `policy_pack contradicts the server activation bypass tools`
  - `CLI mode presets silently overwrite pack and allowlist settings`
  - `HTTP and stdio surfaces advertise different tool realities`
  - `directory.org returns a fake connector error instead of a real downstream Graph permission failure`
- GO criteria:
  - `All checks pass and the repaired runtime yields truthful activation plus truthful first-hop M365 behavior.`
- NO-GO criteria:
  - `Any remaining contradiction between activation admission, session-state, and callable tool behavior.`

## H - Harness (ordered checks)

`M365-UCP-ACTIVATION-C0` Preflight

- Verify governance docs, plan refs, and prerequisite closed lineage.

`M365-UCP-ACTIVATION-C1` Baseline inventory

- Capture the current live failure signatures for activate_session, session_status, validate_action, m365_sites, and m365_action.

`M365-UCP-ACTIVATION-C2` Activation admission repair

- Repair the activation path so activation bypass tools are not contradicted by policy admission.

`M365-UCP-ACTIVATION-C3` Session-state projection repair

- Ensure activation state becomes visible immediately to governed tools after activation.

`M365-UCP-ACTIVATION-C4` Tool-surface parity

- Align or document stdio and HTTP tool-surface behavior so advertised availability matches callable reality.

`M365-UCP-ACTIVATION-C5` M365 first-hop truthfulness

- Ensure the repaired path reaches the real M365 connector and does not collapse into fake credentials or session errors.

`M365-UCP-ACTIVATION-C6` Execute targeted validations

- Re-run live activation, governance, sites.root, and directory.org checks.

`M365-UCP-ACTIVATION-C7` Strict artifact validation

- Verify notebook/runtime sync, prompt/plan sync, and retained evidence completeness.

`M365-UCP-ACTIVATION-C8` Deterministic replay

- Repeat the live checks on fixed config and require consistent admission and outcome-class results.

`M365-UCP-ACTIVATION-C9` Hard gates (strict order)

1. `targeted UCP tests and contract checks`
2. `live repaired activation and first-hop M365 smoke`
3. `git diff --check`

`M365-UCP-ACTIVATION-C10` Governance synchronization and final decision

- Update required docs and emit GO or NO-GO lines.

## S - Stress-test

- Adversarial checks:
  - `If activation works only when policy_pack is bypassed artificially, fail.`
  - `If HTTP and stdio still disagree about callable tools, fail.`
- Replay checks:
  - `Activation admission and first-hop result class must remain stable between run 1 and run 2 for fixed repo and tenant state.`

## Output Contract

- Deliverables:
  - `repaired activation path`
  - `retained live evidence for activation and first-hop M365 calls`
  - `truthful final live-state summary`
- Validation results:
  - `M365-UCP-ACTIVATION-C0..C10 statuses`
- Evidence links:
  - `file paths and commands only`
- Residual risks:
  - `state any remaining downstream Microsoft permission issue explicitly or use none`
- Final decision lines:
  - `GATE:M365-UCP-ACTIVATION STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Any path where `activate_session` is still blocked after user approval.
- Any path where `m365_sites` or `m365_action` still fail with `session_not_activated` after activation.
- Any path where the repair hides a downstream Microsoft permission failure behind a fake connector error.
- Any missing governance synchronization between M365 and UCP artifacts.
