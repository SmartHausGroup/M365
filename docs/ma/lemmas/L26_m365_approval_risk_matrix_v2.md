# L26 — M365 Approval and Risk Matrix v2

## Claim

For the SMARTHAUS workforce control plane to apply approvals consistently as the action universe expands:

1. one machine-readable approval/risk authority must exist
2. each action must resolve to exactly one `risk_class`
3. each action must resolve to exactly one `approval_profile`
4. approval-bearing actions must resolve deterministically to `approval_required = true`
5. the governed ops-adapter runtime must project that authority before approval creation or execution

If any condition fails, `E1E` and later workload-expansion phases inherit a split governance model.

## Existing Proof Sources

- `Operations/NORTHSTAR.md`
- `plans/m365-ai-workforce-expansion-master-plan/m365-ai-workforce-expansion-master-plan.md`
- `registry/universal_action_contract_v2.yaml`
- `registry/persona_capability_map.yaml`
- `registry/approval_risk_matrix_v2.yaml`
- `docs/commercialization/m365-approval-risk-matrix-v2.md`
- `src/smarthaus_common/approval_risk.py`
- `src/ops_adapter/main.py`
- `src/ops_adapter/approvals.py`
- `tests/test_approval_risk_v2.py`
- `tests/test_ops_adapter.py`
- `notebooks/m365/INV-M365-AB-approval-risk-matrix-v2.ipynb`
- `notebooks/lemma_proofs/L26_m365_approval_risk_matrix_v2.ipynb`

## Acceptance Evidence

- the approval/risk registry defines deterministic domain defaults plus exact and prefix overrides
- the shared approval/risk resolver returns one risk class and one approval profile per action
- approval-bearing actions can force pending approval even when older OPA rules do not yet carry the full v2 matrix
- approval metadata is projected into the governed runtime before approval creation
- the active plan and trackers advance from `E1D` to `E1E`

## Deterministic Surface

`ApprovalRiskV2(agent, action, params) = ExactPolicy(action) ∨ PrefixPolicy(action) ∨ DomainDefault(Route(agent, action))`

`ApprovalRequired = Requirement(Policy(action), params)`

`E1D_GO = SharedApprovalRiskAuthority ∧ DeterministicResolution ∧ GovernedRuntimeProjection ∧ TrackerAdvance(E1D, E1E)`
