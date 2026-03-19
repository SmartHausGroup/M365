# L11 — M365 Certification Environment Readiness

## Claim

After `B4E` and `B5C` are green, `C1A` may return `GO` iff:

1. the selected tenant contract exists and resolves deterministically through the tenant loader
2. one supported app-only credential contract is available for the selected tenant
3. the live certification shell exports the required runtime-selection, mutation, audit, and approval-path inputs
4. instruction-surface operator inputs are present whenever the CAIO path is explicitly in scope

If any of those conditions fails, `C1A` must return deterministic `NO-GO` and keep live certification blocked.

## Existing Proof Sources

- `artifacts/certification/m365-v1-candidate-52ca494/prerequisites_report.json`
- `artifacts/certification/m365-v1-candidate-52ca494/README.md`
- `artifacts/certification/m365-v1-candidate-52ca494/operator_checklist.md`
- `notebooks/m365/INV-M365-M-certification-environment-readiness.ipynb`
- `notebooks/lemma_proofs/L11_m365_certification_environment_readiness.ipynb`
- `docs/prompts/codex-m365-enterprise-readiness-master-plan-c1a-certification-environment-readiness.md`

## Acceptance Evidence

- the SmartHaus tenant YAML exists and resolves through `smarthaus_common.tenant_config` when selected
- the app-only credential contract is classified separately from the active shell environment
- the readiness report identifies missing launch inputs without exposing secret values
- the `C1A` gate is emitted explicitly as `GO` or `NO-GO`
- touched-file diff remains bounded to `C1A` evidence, MA traceability, scorecard linkage, and tracker synchronization

## Deterministic Surface

`ReadinessGate(C1A) = TenantContractResolved ∧ AppOnlyCredentialContractPresent ∧ RuntimeSelectionPresent ∧ MutationAuditTogglesPresent ∧ ApprovalPathPresent ∧ (CAIOInScope -> CAIOInputsPresent)`
