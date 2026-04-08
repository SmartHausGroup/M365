# M365 Power Platform Executor Auth Remediation

## Status

`R0` through `R6` are complete. The direct repo Power Platform path now authenticates through an explicit Power Platform credential chain instead of drifting onto the SharePoint executor, and the live repo probe returns a truthful zero-environment result instead of `AADSTS7000215`.

## Purpose

This initiative exists to make Power Apps and Power Automate admin reads truthful in the direct repo runtime. The requirement is stronger than "make the error go away." The runtime must authenticate with the correct bounded executor identity, use one explicit credential source, and prove that the live read path is green without falling back onto SharePoint or other mixed auth surfaces.

## Frozen `R1` Evidence

### Live failure

The fresh repo-direct probe to `list_powerapp_environments` still fails live on `2026-04-08`, but the failure is now frozen with enough precision to drive the repair:

- repo instruction response: `ok=false`
- Microsoft error id: `AADSTS7000215`
- failing app id: `fe34434f-0de8-4807-a239-9ee093d4780c`
- response trace id: `22501e6a-9fff-4685-a906-4f2f6e821952`
- Microsoft trace id: `9ef86b83-22f6-45d5-8930-372df8faaa00`
- Microsoft correlation id: `4aea70f0-4b77-4b5a-9915-60c05253a2b7`
- Microsoft timestamp: `2026-04-08 15:10:36Z`

The bounded-executor contract in `docs/commercialization/m365-executor-domain-routing-and-minimum-permission-model.md` identifies that app id as the SharePoint executor, not a Power Platform executor.

### Runtime resolution chain

The selected-tenant runtime state proves that the direct repo path is still projecting Power Platform onto the wrong executor:

- selected tenant is active through `UCP_TENANT`
- tenant display name: `SMARTHAUS`
- default executor: `sharepoint`
- available executors: `collaboration`, `directory`, `sharepoint`
- routed action: `list_powerapp_environments`
- route key: `powerplatform`
- resolved executor name: `sharepoint`
- resolved executor domain: `sharepoint`
- resolved executor client id: `fe34434f-0de8-4807-a239-9ee093d4780c`
- resolved executor has client secret: `false`
- resolved executor has certificate: `true`

This matches the current repo contract in `src/smarthaus_common/tenant_config.py`, where logical `powerplatform` is still aliased to `sharepoint`.

### Credential-source contradiction

The Power Apps client currently resolves credentials only from the projected tenant `azure` block or the legacy graph config. In the direct client probe, that projected config had:

- the SharePoint executor client id
- no client secret
- a certificate path

The direct client therefore failed closed with:

- `AuthConfigurationError`
- `Power Apps admin not configured: client_secret is required for Add-PowerAppsAccount service-principal auth.`

But the live instruction path produced a different result for the same action and app id:

- `AADSTS7000215`
- `Invalid client secret provided`

That contradiction is the key `R1` finding. The runtime is not operating from one canonical Power Platform credential source yet. One code path sees no secret and fails closed locally; the live instruction path still reaches PowerShell with a secret-bearing auth attempt. Until that ambiguity is removed, the repo cannot claim Power Platform auth is deterministic.

## Root-Cause Decision

`R1` proves three things:

1. there is no dedicated Power Platform executor in the active selected-tenant executor registry
2. logical `powerplatform` actions still resolve onto the SharePoint executor
3. the Power Platform admin clients do not yet enforce one canonical credential source

So the current blocker is not "Power Automate is unsupported." The blocker is:

`PowerPlatformAuthDrift = WrongExecutorProjection AND MixedCredentialResolution`

## What `R1` Did Not Do

`R1` did not repair runtime code, rotate credentials, change tenant YAML, or change any secret material. It only froze the failure truthfully so `R2` through `R5` can fix the model and prove the live path afterward.

## `R2` Canonical Executor Model

The canonical Power Platform executor model is now:

- never project logical `powerplatform` onto the SharePoint executor
- prefer an explicit `powerplatform` executor when the selected tenant contract defines one
- otherwise resolve a bounded Power Platform admin identity from explicit `SMARTHAUS_PP_*` bootstrap settings
- keep certificate auth as the preferred long-term posture for executor administration
- allow a transitional client secret only because the Power Platform admin module path still requires service-principal secret auth for `Add-PowerAppsAccount`

That model is now encoded in [tenant_config.py](/Users/smarthaus/Projects/GitHub/M365/src/smarthaus_common/tenant_config.py) through `project_powerplatform_executor()`.

## `R3` Repo-Local Runtime Hardening

The repo runtime no longer routes Power Platform calls through the SharePoint executor path.

What changed:

- [tenant_config.py](/Users/smarthaus/Projects/GitHub/M365/src/smarthaus_common/tenant_config.py) now fails closed on unmapped `powerplatform` unless it can resolve either:
  - an explicit `powerplatform` executor, or
  - explicit Power Platform bootstrap credentials from `SMARTHAUS_PP_*`, or
  - the transitional legacy bootstrap path
- [m365.py](/Users/smarthaus/Projects/GitHub/M365/src/provisioning_api/routers/m365.py) now projects Power Apps, Power Automate, and Power BI clients through `project_powerplatform_executor()` instead of the general executor alias path
- [test_env_loading.py](/Users/smarthaus/Projects/GitHub/M365/tests/test_env_loading.py) now proves `powerplatform` is no longer silently aliased to `sharepoint`
- [test_tenant_config_powerplatform.py](/Users/smarthaus/Projects/GitHub/M365/tests/test_tenant_config_powerplatform.py) now proves the new resolution order and fail-closed behavior

Focused runtime validation passed:

- `PYTHONPATH=src .venv/bin/pytest -q tests/test_env_loading.py tests/test_tenant_config_powerplatform.py tests/test_power_apps_expansion_v2.py tests/test_power_automate_expansion_v2.py tests/test_executor_routing_v2.py tests/test_auth_model_v2.py`
- result: `44 passed`

## `R4` Tenant / Runtime Enablement Proof

The live tenant-side blocker turned out to be real and external: the legacy Power Platform executor app path had no password credentials at all.

The readback proof for app `720788ac-1485-4073-b0c8-1a6294819a87` showed:

- display name: `SMARTHAUS Legacy M365 Executor`
- `passwordCredentials: []`
- one certificate credential only

That meant the old bootstrap secret path could never succeed. To restore a truthful service-principal path for the Power Platform admin modules, the runtime was enabled with:

- an added transitional password credential on the legacy executor app
- explicit repo-local bootstrap variables `SMARTHAUS_PP_TENANT_ID`, `SMARTHAUS_PP_CLIENT_ID`, `SMARTHAUS_PP_CLIENT_SECRET`, and `SMARTHAUS_PP_CLIENT_CERTIFICATE_PATH`

No secret material was committed to git.

## `R5` Live Repo-Direct Certification

After the runtime hardening and tenant-side credential correction, the direct repo probe changed from auth failure to truthful live success.

Final live result on `2026-04-08`:

- `list_powerapp_environments`
  - `http_status=200`
  - `ok=true`
  - `count=0`
  - `trace_id=538f73b8-fc52-4624-be18-595262d97280`
- `list_flows_admin`
  - not run
  - reason: no environment name was available because the environment inventory returned `0`
- `list_http_flows`
  - not run
  - reason: no environment name was available because the environment inventory returned `0`

This is the key closeout truth: the repo no longer fails on Power Platform authentication. The remaining boundary is not bad auth or wrong executor routing. The selected tenant simply returned zero accessible Power Platform environments to enumerate flows from.

## `R6` Closeout

This package is complete.

What is fixed:

- wrong SharePoint executor projection is gone
- mixed credential resolution is gone
- Power Platform auth now uses an explicit bounded source
- the live repo path now authenticates truthfully
- the previous `AADSTS7000215` failure is eliminated

What remains true:

- there are currently zero accessible Power Platform environments for the selected runtime identity
- so deeper flow-list reads are not applicable until an environment exists or becomes visible to that identity

## Next Act

None for this remediation package. Power Platform auth drift is resolved. Any future work would be a separate tenant-surface enablement or sample-environment certification package, not more executor-auth repair.
