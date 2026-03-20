# L15 — M365 Tenant Contract and Executor Registry Extension

## Claim

For the rebased SMARTHAUS multi-executor runtime to be implementable deterministically, the tenant contract is admissible iff:

1. the tenant schema can represent multiple bounded executor domains
2. one default executor remains derivable for backward compatibility with the current single-executor contract
3. executor registry metadata is explicit enough to support later routing and permission minimization
4. loader behavior remains fail-closed for unknown or incomplete executor definitions

If any of those conditions fails, `B7B` cannot implement routing without ambiguity and `C1A` remains blocked on the stale single-executor model.

## Existing Proof Sources

- `Operations/NORTHSTAR.md`
- `plans/m365-enterprise-readiness-master-plan/m365-enterprise-readiness-master-plan.md`
- `docs/commercialization/m365-executor-domain-routing-and-minimum-permission-model.md`
- `docs/commercialization/m365-certification-rebase-digital-employee-multi-executor-model.md`
- `src/smarthaus_common/tenant_config.py`
- `src/smarthaus_common/config.py`
- `notebooks/m365/INV-M365-Q-tenant-contract-executor-registry-extension.ipynb`
- `notebooks/lemma_proofs/L15_m365_tenant_contract_executor_registry_extension.ipynb`

## Acceptance Evidence

- the tenant loader supports bounded executor-domain definitions
- the existing root `azure` contract still resolves as the default executor when no registry is present
- config helpers can resolve executor data without bypassing the selected-tenant authority
- bounded tests prove both backward compatibility and multi-executor loading semantics

## Deterministic Surface

`ExecutorRegistryReady = MultiExecutorSchema ∧ BackwardCompatibleDefault ∧ ExplicitRegistryMetadata ∧ FailClosedLoaderSemantics`

`BackwardCompatibleDefault = LegacyAzureContract -> DefaultExecutorResolved`

`ExplicitRegistryMetadata = DomainId ∧ CredentialBinding ∧ RoutingHints ∧ EnabledState`
