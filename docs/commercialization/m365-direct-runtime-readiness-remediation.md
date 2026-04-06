# M365 Direct Runtime Readiness Remediation

## Outcome

The repo-direct M365 runtime is now usable for representative local function testing without tripping over known local import or routing defects.

This remediation closed the repo-local defects that were making direct testing misleading:

- the top-level provisioning API import path now starts cleanly
- the lower-level governed action path no longer fails because allowed actions are missing from `registry/executor_routing_v2.yaml`
- multi-executor local tenants now preserve the logical route domain even when the physical tenant only exposes three executors

## Repo-Local Repairs Completed

### 1. Provisioning API import and startup repair

Repaired:

- `src/provisioning_api/routers/email_dashboard.py`
- `src/provisioning_api/main.py`

Result:

- the provisioning API now imports cleanly in a repo checkout without a root `static/` directory or installed dashboard templates
- direct endpoint collection is green again

### 2. Executor routing parity repair

Repaired:

- `src/smarthaus_common/tenant_config.py`
- `src/ops_adapter/actions.py`
- `src/ops_adapter/main.py`
- `src/ops_adapter/app.py`
- `registry/executor_routing_v2.yaml`

Result:

- logical domains like `messaging`, `workmanagement`, `reports`, `security`, `identity_security`, `knowledge`, `powerplatform`, and `publishing` now project deterministically onto the bounded physical executor topology
- executor identity now preserves:
  - logical route domain
  - physical executor domain
- routing coverage improved from `99` missing allowed-action routes to `0`

### 3. Focused regression coverage

Added or updated:

- `tests/test_executor_routing_v2.py`
- `tests/test_ops_adapter.py`
- `tests/test_env_loading.py`

Focused validation passed:

- `PYTHONPATH=src .venv/bin/pytest -q tests/test_executor_routing_v2.py tests/test_ops_adapter.py tests/test_env_loading.py tests/test_endpoints.py tests/test_m365_module_entrypoint.py`
- result: `51 passed`

## Direct Runtime Truth After Repair

### Instruction surface

Live direct instruction probes against the local repo version now classify truthfully:

- SharePoint `list_sites`: success
- Teams `list_teams`: success
- Mail `list_messages`: external Graph `ErrorAccessDenied`
- Calendar `list_events`: external Graph `ErrorAccessDenied`
- Power Apps `list_powerapp_environments`: external local module missing

### Governed action surface

Under the documented local-development harness with `OPA_FAIL_OPEN=true` when no local OPA service is running:

- `ucp-administrator/admin.get_tenant_config`: success
- `teams-manager/teams.list`: success
- `m365-administrator/sites.get`: success
- `service-health/health.overview`: external Graph `UnknownError`
- `email-processing-agent/mail.list`: external Graph `ErrorAccessDenied`
- `calendar-management-agent/calendar.availability`: external Graph `ErrorAccessDenied`

## Remaining External Prerequisites

These are no longer repo-runtime bugs:

- mail and calendar actions require tenant permissions that the current live app path does not have
- Power Apps / Power Automate admin commands require the local PowerShell admin modules to be installed
- service-health depends on the tenant-side Graph / service-health surface behaving correctly for the current app registration

## Practical Meaning

Future direct checks can now be requested truthfully from this repo version.

If a direct function fails now, the next question is no longer “is the repo runtime broken?” The next question is whether the tenant, app registration, local admin modules, or operator environment is ready for that specific Microsoft 365 surface.
