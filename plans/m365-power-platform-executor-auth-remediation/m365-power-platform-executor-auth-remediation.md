# Plan: M365 Power Platform Executor Auth Remediation

**Plan ID:** `plan:m365-power-platform-executor-auth-remediation`
**Parent Plan ID:** `none`
**Status:** `in_progress`
**Date:** `2026-04-08`
**Owner:** `SMARTHAUS`
**Execution plan reference:** `plan:m365-power-platform-executor-auth-remediation:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — keep the repo-local M365 runtime truthful, fail-closed, and self-service by making the Power Platform executor authenticate with the correct bounded identity instead of drifting onto the wrong app registration.
**Governance evidence:** `notebooks/m365/INV-M365-DG-power-platform-executor-auth-package-governance-alignment-v1.ipynb`, `configs/generated/power_platform_executor_auth_package_governance_alignment_v1_verification.json`

## Objective

Repair the Power Platform executor identity and credential chain so direct repo Power Apps and Power Automate admin actions authenticate with the correct executor identity, use the canonical credential source, and pass live validation truthfully.

## Problem Statement

The direct repo Power Platform probe is currently blocked by configuration drift, not by missing product capability.

- On `2026-04-08`, the live repo-direct call to `list_powerapp_environments` failed with Microsoft error `AADSTS7000215: Invalid client secret provided`.
- The failing app id in the live error was `fe34434f-0de8-4807-a239-9ee093d4780c`.
- [m365-executor-domain-routing-and-minimum-permission-model.md](/Users/smarthaus/Projects/GitHub/M365/docs/commercialization/m365-executor-domain-routing-and-minimum-permission-model.md) identifies that app id as the `sharepoint` executor, not a Power Platform executor.
- [tenant_config.py](/Users/smarthaus/Projects/GitHub/M365/src/smarthaus_common/tenant_config.py) currently aliases logical `powerplatform` routes to `sharepoint`.
- [power_apps_client.py](/Users/smarthaus/Projects/GitHub/M365/src/smarthaus_common/power_apps_client.py) and [power_automate_client.py](/Users/smarthaus/Projects/GitHub/M365/src/smarthaus_common/power_automate_client.py) currently resolve credentials from the tenant-wide Azure block or the legacy graph config instead of a dedicated `powerplatform` executor identity.

That means the repo can route Power Platform actions, but it cannot yet prove that those actions are bound to the correct executor identity or secret source. This is exactly the kind of auth drift the repo is supposed to fail closed on.

## Decision Rule

`PPExecutorTruth = DedicatedExecutor(powerplatform) AND CanonicalCredentialSource(powerplatform)`

`PPAuthTruth = PPExecutorTruth AND ValidCredentialMaterial(powerplatform)`

`PPLiveReadTruth = list_powerapp_environments succeeds AND list_flows_admin succeeds AND list_http_flows succeeds`

`GO = PPAuthTruth AND PPLiveReadTruth`

If `GO` is false, the initiative must stay open and report the remaining blocker truthfully.

## Scope

### In scope

- create the governed remediation package and governance notebook backing
- audit the current Power Platform executor identity chain and credential resolution path
- define the canonical Power Platform executor auth model
- correct repo-local credential resolution and executor mapping drift
- add or adjust focused tests for tenant-config and Power Platform auth behavior
- rerun live repo-direct Power Platform validation
- publish a closeout note and diagnostics artifact if the live path becomes truthful

### Out of scope

- UCP runtime changes
- unrelated SharePoint, Teams, Outlook, or persona-surface work
- committing live secrets, secret values, or certificate private keys
- pretending auth is fixed without live repo-direct proof

### File allowlist

- `plans/m365-power-platform-executor-auth-remediation/**`
- `docs/prompts/codex-m365-power-platform-executor-auth-remediation.md`
- `docs/prompts/codex-m365-power-platform-executor-auth-remediation-prompt.txt`
- `notebooks/m365/INV-M365-DG-power-platform-executor-auth-package-governance-alignment-v1.ipynb`
- `configs/generated/power_platform_executor_auth_package_governance_alignment_v1_verification.json`
- `docs/commercialization/m365-config-migration-and-auth-policy.md`
- `docs/commercialization/m365-executor-domain-routing-and-minimum-permission-model.md`
- `docs/commercialization/m365-direct-full-surface-certification.md`
- `docs/commercialization/m365-power-platform-executor-auth-remediation.md`
- `artifacts/diagnostics/m365_power_platform_executor_auth_remediation.json`
- `src/smarthaus_common/tenant_config.py`
- `src/smarthaus_common/power_apps_client.py`
- `src/smarthaus_common/power_automate_client.py`
- `src/provisioning_api/routers/m365.py`
- `tests/test_power_apps_expansion_v2.py`
- `tests/test_power_automate_expansion_v2.py`
- `tests/test_executor_routing_v2.py`
- `tests/test_auth_model_v2.py`
- `tests/test_tenant_config_powerplatform.py`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `.env`
- `../UCP/**`
- any tenant secret store, live certificate private key, or secret-bearing local file
- any path not listed in the allowlist

## Requirements

### R0 — Governed package activation

- create the remediation plan triplet, prompt pair, and tracker activation
- include notebook-backed governance evidence so tracker edits are admissible

### R1 — Root-cause audit

- freeze the current auth failure, the wrong app-id evidence, and the current credential-resolution chain

### R2 — Canonical Power Platform executor model

- define the single truthful executor identity for Power Platform actions
- keep certificate auth as the preferred long-term posture
- keep client secret as transitional only when explicitly required by the Power Platform admin modules

### R3 — Repo-local runtime hardening

- correct credential resolution so Power Platform clients do not drift onto the tenant-wide or SharePoint executor identity
- remove or reduce any fallback behavior that masks executor-auth ambiguity

### R4 — Tenant/runtime enablement proof

- verify the Power Platform management-app registration and the active credential source actually match the runtime target model

### R5 — Live repo-direct certification

- prove the corrected path with direct repo calls to:
  - `list_powerapp_environments`
  - `list_flows_admin`
  - `list_http_flows`
- if flows exist, also certify at least one deeper read such as `get_flow_admin`, `list_flow_owners`, or `list_flow_runs`

### R6 — Truthful closeout

- publish the remediation result in diagnostics, commercialization notes, and trackers
- if the path still is not green, leave the package open with the exact remaining blocker

## Execution Order

1. `R0` package activation
2. `R1` root-cause audit
3. `R2` canonical auth model
4. `R3` repo-local hardening
5. `R4` tenant/runtime enablement proof
6. `R5` live repo-direct certification
7. `R6` closeout

## Success Criteria

- Power Platform repo-direct reads no longer authenticate as the SharePoint executor
- the runtime uses one explicit credential source for Power Platform admin actions
- no secret values are added to version control
- `list_powerapp_environments` succeeds
- `list_flows_admin` succeeds
- `list_http_flows` succeeds
- the final state is documented truthfully as green or blocked

## Validation

- parse checks for the plan triplet, prompt pair, notebook, and verification artifact
- focused tests:
  - `PYTHONPATH=src .venv/bin/pytest -q tests/test_power_apps_expansion_v2.py tests/test_power_automate_expansion_v2.py tests/test_executor_routing_v2.py tests/test_auth_model_v2.py tests/test_tenant_config_powerplatform.py`
- live repo-direct proof:
  - `list_powerapp_environments`
  - `list_flows_admin`
  - `list_http_flows`
- `pre-commit run --all-files`
- `git diff --check`

## Execution Status

- `R0` is complete in the package-creation slice.
- `R1` is complete. The root-cause audit is frozen in:
  - `docs/commercialization/m365-power-platform-executor-auth-remediation.md`
  - `artifacts/diagnostics/m365_power_platform_executor_auth_remediation.json`
  - `notebooks/m365/INV-M365-DG-power-platform-executor-auth-package-governance-alignment-v1.ipynb`
  - `configs/generated/power_platform_executor_auth_package_governance_alignment_v1_verification.json`
- The audit proved:
  - `powerplatform` still resolves onto `sharepoint`
  - the live failing app id is still the SharePoint executor app id
  - the direct client sees no secret while the instruction path still reaches an invalid-secret auth attempt
- No runtime code, tenant configuration, or secret material has been changed yet.
- The next governed act is `R2`, the canonical Power Platform executor model.
