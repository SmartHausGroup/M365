# M365 Contracts (MA Process)

Contracts in this repo follow the **Mathematical Autopsy (MA)** process so that every guarantee is **mathematically guaranteed**. See:

- **Process:** [MathematicalAutopsy/docs/operations/CONTRACTS_MA_PROCESS.md](https://github.com/SmartHausGroup/MathematicalAutopsy/blob/main/docs/operations/CONTRACTS_MA_PROCESS.md)
- **SMARTHAUS reference:** [SMARTHAUS/docs/reference/CONTRACTS_MA_PROCESS.md](https://github.com/SmartHausGroup/SMARTHAUS/blob/main/docs/reference/CONTRACTS_MA_PROCESS.md)

## Contract: CAIO ↔ M365 Instruction API

| Phase | Artifact |
|-------|----------|
| 1. Intent | `caio-m365/INTENT.md` |
| 2. Mathematics | `caio-m365/MATHEMATICS.md` |
| 3. Invariants | `../invariants/INV-CAIO-M365-001.yaml` (and INDEX) |
| 3. Lemma | `caio-m365/LEMMA_L1.md` |
| 4. Verification | Scripts/notebooks → `configs/generated/caio_m365_contract_verification.json`, `m365_idempotency_verification.json`, `m365_auth_verification.json`, `m365_audit_verification.json` |
| 5. CI | Gate on all MA verification artifacts |

**Master equation:** All guarantees (Eq. 1–5) are composed in `caio-m365/M365_MASTER_CALCULUS.md`. Invariants INV-CAIO-M365-001 (postcondition), INV-CAIO-M365-002 (idempotency), INV-CAIO-M365-003 (auth), INV-M365-AUDIT-001 (audit); lemmas L1–L4; notebooks under `notebooks/ma_*.ipynb`.

Human-readable API summary remains in **`docs/CAIO_M365_CONTRACT.md`**; the MA artifacts above formalize and guarantee it.
