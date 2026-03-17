# M365 Canonical Config Contract

**Status:** `P1A` complete
**Date:** 2026-03-17
**Plan refs:** `plan:m365-enterprise-commercialization-readiness:R2`, `plan:m365-enterprise-commercialization-readiness:P1A`

This document defines the current configuration inventory for the M365 repo and locks the one canonical target production contract for standalone M365 commercialization.

Deterministic contract rule for this repository state:

`CanonicalProdConfig = TenantConfig(UCP_TENANT, tenant_yaml) + EnvSecretFallbacks + BootstrapLocators`

Where:

1. `tenant_yaml` is the authoritative structured configuration contract.
2. `EnvSecretFallbacks` may fill missing secret fields and compatibility aliases.
3. `BootstrapLocators` are limited to discovery inputs such as `UCP_TENANT`, `UCP_ROOT`, and `REPOS_ROOT`.
4. `.env` loading surfaces are local bootstrap or compatibility layers, not the canonical production contract.

## Current Inventory

The current repository state contains multiple configuration-loading surfaces. `P1A` classifies each one explicitly.

| Surface | Files | Current behavior | Classification |
| --- | --- | --- | --- |
| Tenant YAML loader | `src/smarthaus_common/tenant_config.py` | Loads tenant identity, auth mode, graph settings, governance, org mappings, data residency, and permission tiers from tenant YAML selected by `UCP_TENANT`, with env fallback for selected Azure credential fields. | Canonical production contract target |
| Env-only Graph config wrapper | `src/smarthaus_common/config.py` | Resolves Graph tenant/client/secret directly from env aliases such as `GRAPH_*`, `AZURE_*`, and `MICROSOFT_*`. | Compatibility surface, not canonical authority |
| Provisioning API repo-root dotenv loaders | `src/provisioning_api/main.py`, `src/provisioning_api/agent_command_center.py`, `src/provisioning_api/agent_workstation.py`, `src/provisioning_api/business_operations.py`, `src/provisioning_api/enterprise_dashboard.py`, `src/provisioning_api/unified_dashboard.py` | Load repo-root `.env` directly with `override=False`. | Legacy local-dev/bootstrap surface |
| Launcher app-root and home dotenv loader | `src/m365_server/__main__.py` | Loads `.env` from `M365_APP_ROOT` or `~/.smarthaus/m365/.env` for launcher/bootstrap convenience. | Operator bootstrap surface, not canonical production identity authority |
| Tenant snapshot and tenant-param actions | `src/ops_adapter/actions.py` | Uses `UCP_TENANT`, `UCP_ROOT`, `REPOS_ROOT`, and tenant YAML lookup for tenant-scoped config inspection and governance paths. | Evidence that tenant-scoped contract already exists |
| Documentation claiming `.env` authority | `docs/ENV.md`, `docs/M365_SERVER_APP.md` | Historically described `.env` as the main config story. | Documentation drift corrected in this phase |
| Local test/export guidance | `docs/LOCAL_TEST_LICENSED_RUNTIME.md` | Shows direct env exports for local testing and live test-tenant validation. | Local test-only surface |

Current ambiguity summary:

1. Production identity and auth semantics are stronger in `tenant_config.py` than in the env-only compatibility layer.
2. Multiple provisioning/dashboard entrypoints still load repo-root `.env` directly.
3. The launcher has its own app-root/home dotenv behavior.
4. Older docs implied `.env` was the canonical configuration model for all contexts.

## Canonical Contract

The canonical target production contract for standalone M365 commercialization is:

1. **Tenant selector:** `UCP_TENANT`
2. **Authoritative configuration document:** tenant YAML loaded by `src/smarthaus_common/tenant_config.py`
3. **Allowed env participation:** secret fallback and bootstrap/discovery inputs only

The tenant YAML contract is authoritative for:

1. `tenant.id`, `tenant.display_name`, `tenant.domain`
2. `auth.mode` and auth sub-configuration
3. `graph` settings
4. `governance` overrides
5. `data_residency`
6. `org` mappings such as SharePoint host/site references
7. `permission_tiers`

Environment variables are not the production contract authority. They are allowed only for:

1. Filling secret-bearing Azure fields when the YAML intentionally omits secret values
2. Selecting the tenant or locating the tenant directory
3. Local launcher/bootstrap behavior
4. Local test and developer convenience flows

Canonical production rule:

If a production deployment can change tenant identity, auth mode, governance mode, or org mappings solely by swapping `.env` values without changing tenant YAML, that deployment is outside the target contract and should be treated as legacy behavior to be migrated in `P1B`.

## Source Precedence

Exactly one target production source-precedence model is allowed after `P1A`.

### Production precedence

1. `UCP_TENANT` selects the active tenant slug.
2. Tenant YAML is resolved using:
   - explicit `tenants_dir` if provided
   - `UCP_ROOT/tenants`
   - `REPOS_ROOT` or `UCP_REPOS_ROOT` tenant path
   - relative fallback path from `tenant_config.py`
3. Within the selected tenant YAML, structured non-secret fields are authoritative.
4. Env fallback may populate only the Azure credential fields currently supported by `tenant_config.py`:
   - `azure.tenant_id`
   - `azure.client_id`
   - `azure.client_secret`
   - `azure.client_certificate_path`
5. App-root `.env`, repo-root `.env`, and `~/.smarthaus/m365/.env` are bootstrap compatibility surfaces only. They are not canonical production identity authority.

### Explicit non-authorities for production

The following are not canonical production sources of truth after `P1A`:

1. Repo-root `.env` loaded directly by provisioning/dashboard entrypoints
2. App-root `.env` loaded by `m365-server`
3. Home-directory `.env` under `~/.smarthaus/m365/.env`
4. Raw env-only precedence in `src/smarthaus_common/config.py`

These surfaces may continue to exist in the current repository state, but they are classified as compatibility or local-bootstrap behavior pending `P1B`.

## Identity Model

The target production identity model is tenant-first, not dotenv-first.

Identity rules:

1. `UCP_TENANT` selects which tenant contract is active.
2. Tenant identity comes from tenant YAML under `tenant.*`.
3. Auth mode comes from tenant YAML under `auth.mode`, with supported modes:
   - `delegated`
   - `app_only`
   - `hybrid`
4. Azure credential material may be supplied by YAML or env fallback, but credential values do not define the tenant model by themselves.
5. SharePoint hostname, primary site, default user, and permission-tier semantics belong to the tenant contract, not ad hoc env overrides.

Commercial consequence:

Standalone M365 enterprise configuration can now be described honestly as a tenant-scoped contract with env-assisted secret injection, rather than a loose collection of interchangeable `.env` conventions.

Residual risk intentionally deferred to `P1B`:

1. The repo still contains direct repo-root `.env` loaders.
2. The launcher still uses app-root/home `.env` bootstrap.
3. Compatibility env aliases are still broad.
4. Migration and deprecation of those surfaces is a `P1B` concern, not a `P1A` concern.
