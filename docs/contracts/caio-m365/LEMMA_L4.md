# Lemma L4 — M365 Audit (One Record per Instruction When Enabled) {#lemma-l4}

**Invariant:** [`invariants/INV-M365-AUDIT-001.yaml`](../../invariants/INV-M365-AUDIT-001.yaml)

**Status:** Draft

**Backed by:** `docs/contracts/caio-m365/MATHEMATICS.md` — Eq. 5.

---

## Assumptions

- When `ENABLE_AUDIT_LOGGING` is true, every code path that completes an instruction request calls the audit writer exactly once (`_audit_instruction` → `log_event`).
- Audit record schema includes: ts, action, user, details (action, params, ok, result/error, trace_id, blocked?, idempotent_replay?).

---

## Claim

When audit logging is enabled, for every completed instruction execution (success, error, or blocked) there exists exactly one audit record for that request with the required schema.

---

## Derivation

1. By MATHEMATICS.md Eq. 5: \(\mathtt{auditEnabled}() \wedge \text{execution completed}(request) \Rightarrow \exists\) exactly one audit record.
2. Implementation: `execute_instruction_contract` calls `_audit_instruction` on every exit path (success, error, blocked, idempotent replay); `log_event` writes one line to audit store when enabled.
3. Verification: enable audit, run one instruction, count new records in audit store; assert count = 1 and schema holds.

---

## Verification

- **Producer:** `scripts/ci/verify_m365_audit.py` or `notebooks/ma_m365_audit.ipynb`.
- **Artifact:** `configs/generated/m365_audit_verification.json` with `audit_pass == true`.
