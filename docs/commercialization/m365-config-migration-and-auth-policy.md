# M365 Config Migration and Auth Policy

**Status:** `P1B` complete
**Date:** 2026-03-17
**Plan refs:** `plan:m365-enterprise-commercialization-readiness:R2`, `plan:m365-enterprise-commercialization-readiness:P1B`

This document defines the singular migration path from the current mixed config state to the canonical production contract established in `P1A`, and it locks the supported auth and secret posture for standalone M365 commercialization.

Deterministic policy rule for this repository state:

`ProdAuthority = TenantYaml(UCP_TENANT) ; ProdAuthDefault = AppOnly ; ProdCredentialPreference = Certificate ; ClientSecret = TransitionalFallback ; Dotenv = BootstrapOnly`

## Migration Path

The migration path is linear. Production guidance must not branch by operator preference.

### Stage 1 — Immediate commercial rule

Effective immediately for standalone M365 v1:

1. `UCP_TENANT` selects the active tenant contract.
2. Tenant YAML remains the authoritative source for tenant identity, auth mode, governance settings, graph settings, org mappings, and permission tiers.
3. Direct repo-root or app-root `.env` loading is classified as bootstrap or local-test behavior only, not production authority.
4. No new production guidance may describe `.env` as the primary source of tenant identity or auth semantics.

### Stage 2 — Runtime migration target

The runtime should converge on this production shape:

1. Provisioning and dashboard entrypoints stop treating repo-root `.env` as a source of production truth.
2. Bootstrap env remains allowed only to:
   - select `UCP_TENANT`
   - locate tenant directories
   - inject secret values or secret-store-resolved values at process start
3. `src/smarthaus_common/config.py` remains a compatibility wrapper until implementation cleanup, but no new production behavior should depend on env-only precedence.

### Stage 3 — Retirement target

The following legacy patterns are on a retirement path:

1. direct repo-root `.env` authority in provisioning/dashboard entrypoints
2. app-root or `~/.smarthaus/m365/.env` as production identity authority
3. broad env-alias sprawl as the primary operator contract

Until runtime cleanup lands, these paths may still exist technically, but commercialization and operator guidance must treat them as legacy compatibility surfaces.

## Auth Mode Policy

The supported auth posture is singular:

1. **Production default:** `app_only`
2. **Enterprise-preferred credential within app-only:** certificate auth
3. **Transitional fallback within app-only:** client secret
4. **Interactive exception mode:** `hybrid`
5. **Local-only interactive mode:** `delegated`

### Auth decision matrix

| Mode | Allowed context | Commercial support class | Policy |
| --- | --- | --- | --- |
| `app_only` | unattended production operations, service-run workflows, supported v1 admin actions | Default | Use by default for standalone M365 v1 |
| `hybrid` | approved exception where service operations must also support explicitly interactive `/me` or user-scoped flows | Exception-only | Allowed only with documented operator need; app-only remains the base posture |
| `delegated` | local operator setup, local testing, support/debug, interactive demos | Local/test only | Not a supported unattended production default |

Policy consequences:

1. Standalone M365 v1 launch claims must not depend on delegated auth as the standard enterprise path.
2. `hybrid` is not a second default. It is an exception posture for specific user-context scenarios.
3. New operator-facing guidance should assume `app_only` unless a specific documented action class requires user-context access.

## Secret Policy

Secret handling is fail-closed.

1. No live secret may be committed to repository files, notebooks, prompt docs, runbooks, or scripts.
2. Committed tenant YAML must not be treated as the storage location for live client secrets or certificate private keys.
3. Production secret material must come from:
   - managed secret store, or
   - runtime environment injection controlled outside versioned repo content
4. `.env` may still be used for local development and controlled bootstrap flows, but it is not an enterprise production secret-management contract.
5. Any secret exposed through branch history, local notes, or blocked push-protection events must be treated as compromised and rotated.
6. Client secrets are allowed only as a transitional runtime fallback where certificate auth is not yet activated.

Operational consequences:

1. Secret-bearing examples in docs must use placeholders only.
2. Checked-in helper scripts must read secret material from env or external secret sources, never hardcoded literals.
3. If a deployment cannot supply secret material without a checked-in file, that deployment is outside the supported enterprise posture.

## Certificate Guidance

Certificate auth is the enterprise-preferred credential model for standalone M365 v1.

Current runtime evidence:

1. `src/smarthaus_common/tenant_config.py` supports `azure.client_certificate_path`.
2. `src/smarthaus_graph/client.py` prefers `client_certificate_path` over `client_secret` for app-only token acquisition when the certificate path exists.

Policy:

1. Broad enterprise production posture should target `app_only + certificate`.
2. `app_only + client_secret` is acceptable only as a transitional path for pilots, early deployments, and migration windows.
3. Certificate private key material must remain outside the repo and outside committed tenant YAML.
4. Final enterprise certification of the certificate-backed path is deferred to `P3A` live-tenant validation and `P3B` release gating.

## Deprecation Map

| Legacy surface | Current location | Commercial status after `P1B` | Required direction |
| --- | --- | --- | --- |
| Repo-root `.env` as production authority | `src/provisioning_api/main.py`, `src/provisioning_api/agent_command_center.py`, `src/provisioning_api/agent_workstation.py`, `src/provisioning_api/business_operations.py`, `src/provisioning_api/enterprise_dashboard.py`, `src/provisioning_api/unified_dashboard.py` | Deprecated for production | Retain only as bootstrap compatibility until runtime migration lands |
| App-root or home `.env` as production authority | `src/m365_server/__main__.py` | Deprecated for production | Keep only for launcher/bootstrap and local operator convenience |
| Env-only config precedence as canonical contract | `src/smarthaus_common/config.py` | Compatibility-only | No new production guidance or new runtime dependence |
| Delegated auth as enterprise default | runtime auth modes | Not supported | Restrict to local/test/support use |
| Client secret as long-term enterprise default | runtime app-only auth | Transitional only | Replace with certificate-backed app-only posture |
| Hardcoded secret literals in scripts/docs | repository content | Prohibited | Remove immediately and rotate if exposed |

## Decision Summary

`P1B` closes the config/auth ambiguity with one supported commercialization posture:

1. tenant YAML selected by `UCP_TENANT` is the production authority
2. `app_only` is the production default
3. certificate auth is the enterprise-preferred credential model
4. client secret is transitional only
5. `.env` remains bootstrap and local-test behavior, not production authority

Residual work intentionally deferred:

1. runtime removal of legacy `.env` authority paths
2. live-tenant certification of the certificate-backed path
3. audit and governance evidence hardening in `P2A`
