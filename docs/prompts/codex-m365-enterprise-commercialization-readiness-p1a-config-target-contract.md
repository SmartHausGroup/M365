# MATHS Prompt: P1A Config Inventory and Canonical Target Contract

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-commercialization-readiness:P1A`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-COMM-P1A-C0` -> `M365-COMM-P1A-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:M365-COMM-P1A STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-COMM-P1A`
- Run ID: `p1a-config-target-contract`
- Commit SHA: `<fill at execution time>`
- Plan refs in scope:
  - `plan:m365-enterprise-commercialization-readiness:R2`
  - `plan:m365-enterprise-commercialization-readiness:P1A`
- Invariant IDs in scope: `N/A unless an approved scope change introduces MA-governed runtime work`
- Lemma IDs in scope: `N/A unless an approved scope change introduces MA-governed runtime work`
- Owners: `engineering`, `security`, `operations`

## Context

- Task name: `P1A Config Inventory and Canonical Target Contract`
- Domain: `docs`
- Dependencies: current env-loading docs and tenant-config code paths
- Allowlist:
  - `plans/m365-enterprise-commercialization-readiness/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `docs/ENV.md`
  - `docs/M365_SERVER_APP.md`
  - `docs/LOCAL_TEST_LICENSED_RUNTIME.md`
  - `src/smarthaus_common/tenant_config.py`
  - `src/smarthaus_common/config.py`
  - `src/m365_server/__main__.py`
  - `src/provisioning_api/main.py`
  - `docs/commercialization/m365-canonical-config-contract.md`
- Denylist:
  - `tests/**`
  - `configs/generated/**`
  - `docs/prompts/**`

## M - Model

- Problem: M365 production configuration is split between a stronger tenant model and direct `.env` loading paths.
- Goal: inventory the current state and define the one canonical target production contract.
- Success criteria:
  - all configuration entrypoints are inventoried
  - one canonical target contract is defined
  - source precedence is explicit
- Out of scope:
  - implementing migration
  - changing runtime code

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `docs/commercialization/m365-canonical-config-contract.md` with sections `Current Inventory`, `Canonical Contract`, `Source Precedence`, and `Identity Model`
- Runtime/test evidence:
  - `rg -n "load_dotenv|UCP_TENANT|GRAPH_|AZURE_" src docs`
- Governance evidence:
  - plan and log synchronization
- Determinism evidence:
  - repeated inventory of config-loading surfaces yields the same list for fixed repository state

## T - Tie

- Dependency ties:
  - `src/smarthaus_common/tenant_config.py` -> target contract candidate
  - direct `load_dotenv` paths -> current-state ambiguity
  - `docs/ENV.md` -> stated config policy
- Known failure modes:
  - target contract ignores a live runtime entrypoint
  - source precedence remains ambiguous
- GO criteria:
  - complete current-state inventory and single canonical target contract
- NO-GO criteria:
  - more than one canonical production contract remains

## H - Harness (ordered checks)

- `M365-COMM-P1A-C0` Preflight.
- `M365-COMM-P1A-C1` Baseline inventory of current config and identity loading paths.
- `M365-COMM-P1A-C2` Draft current-state inventory section.
- `M365-COMM-P1A-C3` Draft canonical target-contract section.
- `M365-COMM-P1A-C4` Schema/artifact contract validation.
- `M365-COMM-P1A-C5` Gate logic hardening: ensure exactly one production source-precedence model.
- `M365-COMM-P1A-C6` Execute targeted `rg` validations.
- `M365-COMM-P1A-C7` Strict artifact validation: fail if any config surface is unclassified.
- `M365-COMM-P1A-C8` Deterministic replay of the inventory extraction.
- `M365-COMM-P1A-C9` Hard gates (strict order):
  1. `rg -n "Current Inventory|Canonical Contract|Source Precedence|Identity Model" docs/commercialization/m365-canonical-config-contract.md`
  2. `rg -n "plan:m365-enterprise-commercialization-readiness:P1A" plans/m365-enterprise-commercialization-readiness docs/commercialization`
  3. `git diff --check`
- `M365-COMM-P1A-C10` Governance synchronization and final decision.

## S - Stress-test

- Adversarial checks:
  - leave one entrypoint outside the inventory
  - define a target contract that still depends on conflicting sources
- Replay checks:
  - the inventory and canonical-contract summary must match across repeated runs

## Output Contract

- Deliverables:
  - `docs/commercialization/m365-canonical-config-contract.md`
- Validation results:
  - `M365-COMM-P1A-C0..C10`
- Evidence links:
  - file paths and commands only
- Residual risks:
  - migration complexity is handled in P1B, not here
- Final decision lines:
  - `GATE:M365-COMM-P1A STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Any config-loading surface is omitted from the inventory.
- The target contract leaves production source precedence unresolved.
- Scope drifts into implementation.
