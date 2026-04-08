# M365 Power Platform Executor Auth Remediation

## Status

`R1` is complete. The root-cause audit is now frozen: the direct repo Power Platform path is not blocked by missing product capability, but by executor-identity drift and a non-canonical credential chain.

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

## Next Act

`R2` is now the active next act. It must define the canonical Power Platform executor identity and auth model, including:

- whether Power Platform becomes its own bounded executor in the active tenant contract
- whether certificate auth remains preferred while client secret stays transitional for the Power Platform admin modules
- how repo-local credential resolution must behave so Power Platform reads cannot silently inherit SharePoint or tenant-wide Graph credentials
