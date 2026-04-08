# Codex Prompt: M365 Power Platform Executor Auth Remediation

Plan reference: `plan:m365-power-platform-executor-auth-remediation`

## Objective

Repair the direct repo Power Platform auth chain so Power Apps and Power Automate admin actions authenticate with the correct bounded executor identity, use the canonical credential source, and pass live validation truthfully.

## Required reads before any mutating action

- `AGENTS.md`
- applicable `.cursor/rules/**/*.mdc`
- `Operations/NORTHSTAR.md`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`
- `plans/m365-power-platform-executor-auth-remediation/m365-power-platform-executor-auth-remediation.md`
- `docs/commercialization/m365-config-migration-and-auth-policy.md`
- `docs/commercialization/m365-executor-domain-routing-and-minimum-permission-model.md`
- `docs/commercialization/m365-direct-full-surface-certification.md`
- `src/smarthaus_common/tenant_config.py`
- `src/smarthaus_common/power_apps_client.py`
- `src/smarthaus_common/power_automate_client.py`
- `src/provisioning_api/routers/m365.py`

## Required outputs

- repaired Power Platform executor auth model and runtime behavior
- truthful live proof for `list_powerapp_environments`, `list_flows_admin`, and `list_http_flows`
- synchronized closeout docs and diagnostics

## Hard constraints

- no UCP work
- no committed secrets or certificate private keys
- certificate remains the preferred long-term posture
- client secret is transitional only where the Power Platform admin modules require it
- fail closed if the runtime cannot prove which executor identity is being used

## Execution order

1. `R1` root-cause audit
2. `R2` canonical executor model
3. `R3` repo-local hardening
4. `R4` tenant/runtime enablement proof
5. `R5` live repo-direct certification
6. `R6` truthful closeout

## Required validations

- focused Power Platform and routing tests
- live repo-direct Power Platform reads
- `pre-commit run --all-files`
- `git diff --check`

## Stop conditions

- stop if the fix requires UCP edits
- stop if the only way forward is committing secret material
- stop if live validation shows tenant policy or permission blockers outside the repo allowlist and report them exactly
