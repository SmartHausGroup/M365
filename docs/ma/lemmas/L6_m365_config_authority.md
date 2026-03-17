# L6 — M365 Tenant-Selected Config Authority

## Claim

When `UCP_TENANT` is selected, runtime configuration authority for Graph credentials and tenant org mappings is deterministic:

1. tenant YAML values are primary
2. injected environment fallback is allowed only for omitted secret-bearing fields
3. bootstrap dotenv inputs do not override tenant-selected production authority

## Existing Proof Sources

- `notebooks/lemma_proofs/L6_m365_config_authority.ipynb`
- `src/smarthaus_common/tenant_config.py`
- `docs/commercialization/m365-canonical-config-contract.md`
- `docs/commercialization/m365-config-migration-and-auth-policy.md`

## Acceptance Evidence

- tenant-selected bootstrap filtering leaves bootstrap keys intact while suppressing tenant-authority keys from dotenv inputs
- tenant-selected graph auth resolution prefers tenant config values over dotenv-style env aliases
- no-tenant local bootstrap remains available for local development and controlled testing

## Deterministic Surface

`Authority(K) = TenantConfigPrimary + EnvSecretFallback + BootstrapOnlyNonAuthorityDotenv`
