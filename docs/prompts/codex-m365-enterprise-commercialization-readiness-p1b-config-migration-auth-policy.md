# MATHS Prompt: P1B Config Migration and Auth and Secret Policy

## Governance Ack

- `GOVERNANCE_ACK: READ`
- `GOVERNANCE_ACK: UNDERSTOOD`
- `GOVERNANCE_ACK: WILL_FOLLOW`
- `PLAN_REF_ACK: plan:m365-enterprise-commercialization-readiness:P1B`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`
- `RULES_ACK: .cursor/rules/**/*.mdc`

## Execution Rules

- Run checks `M365-COMM-P1B-C0` -> `M365-COMM-P1B-C10` in strict order.
- Stop on first `FAIL` or `BLOCKED`.
- Output each check exactly:
  - `CHECK:<id> STATUS:<PASS|FAIL|BLOCKED> EVIDENCE:<path/command> NOTE:<one line>`
- Final outputs exactly:
  - `GATE:M365-COMM-P1B STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## Prompt Run Metadata

- Prompt version: `1.0`
- Task ID: `M365-COMM-P1B`
- Run ID: `p1b-config-migration-auth-policy`
- Commit SHA: `<fill at execution time>`
- Plan refs in scope:
  - `plan:m365-enterprise-commercialization-readiness:R2`
  - `plan:m365-enterprise-commercialization-readiness:P1B`
- Invariant IDs in scope: `N/A unless an approved scope change introduces MA-governed runtime work`
- Lemma IDs in scope: `N/A unless an approved scope change introduces MA-governed runtime work`
- Owners: `engineering`, `security`, `operations`

## Context

- Task name: `P1B Config Migration and Auth and Secret Policy`
- Domain: `docs`
- Dependencies: P1A canonical target contract
- Allowlist:
  - `plans/m365-enterprise-commercialization-readiness/*`
  - `Operations/EXECUTION_PLAN.md`
  - `Operations/ACTION_LOG.md`
  - `Operations/NORTHSTAR.md`
  - `docs/ENV.md`
  - `docs/M365_SERVER_APP.md`
  - `src/smarthaus_common/tenant_config.py`
  - `docs/commercialization/m365-config-migration-and-auth-policy.md`
- Denylist:
  - `tests/**`
  - `configs/generated/**`
  - `docs/prompts/**`

## M - Model

- Problem: even with a target contract, commercialization fails if the migration path, secret policy, and auth posture stay ambiguous.
- Goal: define a deterministic migration and policy set for config, auth, and secrets.
- Success criteria:
  - migration path is staged and explicit
  - auth-mode decision matrix is explicit
  - secret-management policy is explicit
- Out of scope:
  - implementing migration
  - live secret-store integration

## A - Annotate

Required measurable evidence:

- Artifact/schema evidence:
  - `docs/commercialization/m365-config-migration-and-auth-policy.md` with sections `Migration Path`, `Auth Mode Policy`, `Secret Policy`, `Certificate Guidance`, and `Deprecation Map`
- Runtime/test evidence:
  - `rg -n "client_secret|client_certificate_path|delegated|app_only|hybrid" src/smarthaus_common/tenant_config.py`
- Governance evidence:
  - plan and log synchronization
- Determinism evidence:
  - repeated policy classification produces the same migration steps and auth recommendations

## T - Tie

- Dependency ties:
  - `P1A` -> target contract constrains migration options
  - `tenant_config.py` -> auth mode and secret options currently available
- Known failure modes:
  - migration path leaves production `.env` as a de facto primary mechanism
  - auth recommendations conflict with target operator model
- GO criteria:
  - one migration path, one secret policy, one auth recommendation matrix
- NO-GO criteria:
  - conflicting production guidance remains

## H - Harness (ordered checks)

- `M365-COMM-P1B-C0` Preflight.
- `M365-COMM-P1B-C1` Baseline inventory of existing auth and secret options.
- `M365-COMM-P1B-C2` Draft migration-path section.
- `M365-COMM-P1B-C3` Draft auth and secret policy sections.
- `M365-COMM-P1B-C4` Schema/artifact contract validation.
- `M365-COMM-P1B-C5` Gate logic hardening: ensure policy is singular, not branching by ambiguity.
- `M365-COMM-P1B-C6` Execute targeted `rg` validations.
- `M365-COMM-P1B-C7` Strict artifact validation: fail if production guidance conflicts internally.
- `M365-COMM-P1B-C8` Deterministic replay of the migration decision model.
- `M365-COMM-P1B-C9` Hard gates (strict order):
  1. `rg -n "Migration Path|Auth Mode Policy|Secret Policy|Certificate Guidance|Deprecation Map" docs/commercialization/m365-config-migration-and-auth-policy.md`
  2. `rg -n "plan:m365-enterprise-commercialization-readiness:P1B" plans/m365-enterprise-commercialization-readiness docs/commercialization`
  3. `git diff --check`
- `M365-COMM-P1B-C10` Governance synchronization and final decision.

## S - Stress-test

- Adversarial checks:
  - recommend both client-secret and certificate auth as equal production defaults
  - leave deprecated loading behavior without a retirement path
- Replay checks:
  - migration stages and policy choices must match across repeated runs

## Output Contract

- Deliverables:
  - `docs/commercialization/m365-config-migration-and-auth-policy.md`
- Validation results:
  - `M365-COMM-P1B-C0..C10`
- Evidence links:
  - file paths and commands only
- Residual risks:
  - runtime implementation work is deferred to later approved execution
- Final decision lines:
  - `GATE:M365-COMM-P1B STATUS:<GO|NO-GO>`
  - `FINAL_DECISION:<GO|NO-GO>`

## No-Go Triggers

- Production auth posture remains ambiguous.
- Secret-management guidance is incomplete.
- Migration path leaves direct production `.env` dependence as primary without explicit approval.
