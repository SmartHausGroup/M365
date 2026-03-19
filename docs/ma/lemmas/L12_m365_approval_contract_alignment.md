# L12 — M365 Approval Contract Alignment

## Claim

For standalone M365 `C1A`, the approval-path readiness gate is admissible iff:

1. the selected tenant contract can carry the approval backend target deterministically
2. approval Graph authentication resolves through the tenant-selected app-only execution contract instead of a parallel env-only credential path
3. approval site and list resolution are deterministic for the selected tenant
4. the live certification shell only needs runtime-selection and controlled execution toggles once the approval target is present in the tenant contract

If any of those conditions fails, approval-path readiness remains `NO-GO`.

## Existing Proof Sources

- `artifacts/certification/m365-v1-candidate-52ca494/prerequisites_report.json`
- `artifacts/certification/m365-v1-candidate-52ca494/README.md`
- `artifacts/certification/m365-v1-candidate-52ca494/operator_checklist.md`
- `docs/commercialization/m365-canonical-config-contract.md`
- `docs/prompts/codex-m365-enterprise-readiness-master-plan-c1a-certification-environment-readiness.md`
- `notebooks/m365/INV-M365-N-approval-contract-alignment.ipynb`
- `notebooks/lemma_proofs/L12_m365_approval_contract_alignment.ipynb`

## Acceptance Evidence

- approval storage target resolves from the selected tenant contract with env fallback only as a compatibility surface
- approval Graph auth resolves through the tenant-selected app-only executor path
- the approval target for SMARTHAUS is explicitly bound to the Operations site
- touched-file diff remains bounded to approval-path runtime/config, `C1A` evidence, MA traceability, and tracker synchronization

## Deterministic Surface

`ApprovalGate(C1A) = ApprovalTargetResolved(tenant_contract, env_fallback) ∧ ApprovalAuthBounded(app_only_executor) ∧ ApprovalSiteListDeterministic(selected_tenant) ∧ ShellInputsBounded(UCP_TENANT, ALLOW_M365_MUTATIONS, ENABLE_AUDIT_LOGGING)`
