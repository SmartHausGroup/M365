# MATHS Prompt: P4A Packaging, Install, and Bootstrap

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-commercialization-readiness:P4A`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-COMM-P4A-C0` -> `M365-COMM-P4A-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:M365-COMM-P4A STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-COMM-P4A`
- Run ID: `p4a-packaging-install-bootstrap`
- Commit SHA: `<fill at execution time>`
- Plan refs in scope:
  - `plan:m365-enterprise-commercialization-readiness:R5`
  - `plan:m365-enterprise-commercialization-readiness:P4A`
- Invariant IDs in scope: `N/A unless an approved scope change introduces MA-governed runtime work`
- Lemma IDs in scope: `N/A unless an approved scope change introduces MA-governed runtime work`
- Owners: `operations`, `engineering`, `delivery`

## Context

- Task name: `P4A Packaging, Install, and Bootstrap`
- Domain: `docs`
- Dependencies: current launcher docs, server app docs, licensed-module model
- Allowlist:
  - `plans/m365-enterprise-commercialization-readiness/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `docs/M365_SERVER_APP.md`
  - `docs/LOCAL_TEST_LICENSED_RUNTIME.md`
  - `docs/TAI_LICENSED_MODULE_MODEL.md`
  - `src/m365_server/__main__.py`
  - `docs/commercialization/m365-packaging-install-bootstrap.md`
- Denylist:
  - `src/**` 
  - `tests/**`
  - `docs/prompts/**`

## M - Model

- Problem: enterprise buyers need one canonical installation and bootstrap path for the standalone module.
- Goal: define package variants, install path, bootstrap flow, and prerequisites.
- Success criteria:
  - packaging variants are explicit
  - install and bootstrap steps are explicit
  - prerequisites and dependencies are explicit
- Out of scope:
  - implementing packaging changes
  - running installers

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `docs/commercialization/m365-packaging-install-bootstrap.md` with sections `Package Variants`, `Install Path`, `Bootstrap Flow`, `Environment Setup`, and `Prerequisites`
- Runtime/test evidence:
  - `rg -n "m365-server|M365_APP_ROOT|M365_SERVER_PORT|.env" docs src/m365_server`
- Governance evidence:
  - plan and log synchronization
- Determinism evidence:
  - repeated package-path classification yields the same canonical install path

## T - Tie

- Dependency ties:
  - server launcher docs -> standalone packaging path
  - licensed-module docs -> TAI-hosted packaging compatibility
- Known failure modes:
  - multiple install paths are presented as equally canonical
  - bootstrap prerequisites are implicit
- GO criteria:
  - one canonical install/bootstrap path is explicit
- NO-GO criteria:
  - installation remains ambiguous

## H - Harness (ordered checks)

- `M365-COMM-P4A-C0` Preflight.
- `M365-COMM-P4A-C1` Baseline inventory of current install and bootstrap surfaces.
- `M365-COMM-P4A-C2` Draft package-variant and install-path sections.
- `M365-COMM-P4A-C3` Draft bootstrap-flow and prerequisites sections.
- `M365-COMM-P4A-C4` Schema/artifact contract validation.
- `M365-COMM-P4A-C5` Gate logic hardening: ensure there is exactly one canonical install path.
- `M365-COMM-P4A-C6` Execute targeted `rg` validations.
- `M365-COMM-P4A-C7` Strict artifact validation.
- `M365-COMM-P4A-C8` Deterministic replay of canonical path selection.
- `M365-COMM-P4A-C9` Hard gates (strict order):
  1. `rg -n "Package Variants|Install Path|Bootstrap Flow|Environment Setup|Prerequisites" docs/commercialization/m365-packaging-install-bootstrap.md`
  2. `rg -n "plan:m365-enterprise-commercialization-readiness:P4A" plans/m365-enterprise-commercialization-readiness docs/commercialization`
  3. `git diff --check`
- `M365-COMM-P4A-C10` Governance synchronization and final decision.

## S - Stress-test

- Adversarial checks:
  - define more than one canonical install path
  - omit bootstrap prerequisites and environment assumptions
- Replay checks:
  - canonical packaging and install-path decisions must match across repeated runs

## Output Contract

- Deliverables:
  - `docs/commercialization/m365-packaging-install-bootstrap.md`
- Validation results:
  - `M365-COMM-P4A-C0..C10`
- Evidence links:
  - file paths and commands only
- Residual risks:
  - packaging implementation remains later work
- Final decision lines:
  - `GATE:M365-COMM-P4A STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Install path is ambiguous.
- Bootstrap assumptions are implicit.
- Scope drifts into implementation or deployment execution.
