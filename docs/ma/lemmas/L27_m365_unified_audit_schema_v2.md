# L27 — M365 Unified Audit Schema v2

## Claim

For the SMARTHAUS workforce control plane to claim one bounded audit model as expansion continues:

1. one machine-readable audit schema authority must exist
2. instruction-api and ops-adapter audit writers must emit the same canonical top-level envelope
3. actor, persona, executor, approval, and result evidence must normalize into one deterministic structure
4. the existing instruction-api verifier must prove the unified schema rather than the legacy narrow dialect
5. the active plan and trackers must advance from `E1E` to `E2A`

If any condition fails, `E2` and later phases inherit split evidence semantics.

## Existing Proof Sources

- `Operations/NORTHSTAR.md`
- `plans/m365-ai-workforce-expansion-master-plan/m365-ai-workforce-expansion-master-plan.md`
- `registry/unified_audit_schema_v2.yaml`
- `docs/commercialization/m365-unified-audit-schema-v2.md`
- `src/smarthaus_common/audit_schema.py`
- `src/ops_adapter/audit.py`
- `src/provisioning_api/audit.py`
- `scripts/ci/verify_m365_audit.py`
- `configs/generated/m365_audit_verification.json`
- `tests/test_audit_schema_v2.py`
- `tests/test_ops_adapter.py`
- `notebooks/m365/INV-M365-AC-unified-audit-schema-v2.ipynb`
- `notebooks/lemma_proofs/L27_m365_unified_audit_schema_v2.ipynb`

## Acceptance Evidence

- the audit-schema registry defines one canonical envelope and surface defaults
- both audit writers emit the shared schema through one runtime helper
- instruction-api verification now checks the unified schema instead of the legacy narrow shape
- bounded runtime tests prove the shared schema on both instruction-api and ops-adapter paths
- the active plan and trackers advance from `E1E` to `E2A`

## Deterministic Surface

`AuditRecordV2(surface, action, status, details, contexts) = SharedBuilder(surface_defaults, required_fields, contexts)`

`E1E_GO = SharedAuditAuthority ∧ SharedRuntimeProjection ∧ BoundedVerificationGreen ∧ TrackerAdvance(E1E, E2A)`
