# L4 — M365 Audit Recording

## Claim

The claimed audit surfaces emit append-only audit evidence with correlation linkage under the current invariant boundary:

1. each instruction execution produces one instruction-audit record with the expected contract schema
2. each successful admin/configuration operation on the active ops-adapter path produces an append-only admin audit event with actor, tenant, action, and requested-effect evidence

## Existing Proof Sources

- `docs/contracts/caio-m365/LEMMA_L4.md`
- `docs/contracts/caio-m365/MATHEMATICS.md`
- `configs/generated/m365_audit_verification.json`
- `src/ops_adapter/audit.py`
- `src/ops_adapter/actions.py`
- `tests/test_ops_adapter.py`

## Acceptance Evidence

- `audit_pass == true`
- `tests/test_ops_adapter.py::test_admin_set_user_tier_records_append_only_audit_event`
- `tests/test_ops_adapter.py::test_admin_audit_log_can_return_snapshot_context`

## Source Invariant

- `invariants/lemmas/L4_m365_audit_recording.yaml`
