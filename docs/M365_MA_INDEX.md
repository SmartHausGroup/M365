# M365 — Mathematical Assurance (MA) index

This repo’s MA artifacts: contract, math, invariants, lemmas, verification scripts, notebooks, CI.

- **Contract and math:** `docs/contracts/caio-m365/`  
  - INTENT.md, MATHEMATICS.md, M365_MASTER_CALCULUS.md, ACTION_SPECIFICATION.md  
  - LEMMAS.md, LEMMA_L1.md–LEMMA_L4.md  
- **Invariants:** `invariants/`  
  - INDEX.yaml, INV-CAIO-M365-001.yaml, INV-CAIO-M365-002.yaml, INV-CAIO-M365-003.yaml, INV-M365-AUDIT-001.yaml  
- **Verification scripts:** `scripts/ci/`  
  - verify_caio_m365_contract.py, verify_m365_idempotency.py, verify_m365_auth.py, verify_m365_audit.py  
- **Notebooks:** `notebooks/`  
  - ma_caio_m365_contract.ipynb, ma_m365_idempotency.ipynb, ma_m365_auth.ipynb, ma_m365_audit.ipynb, ma_m365_master.ipynb  
- **CI:** `.github/workflows/ci.yml` (MA verification steps and artifact checks)

The overall plan (North Star) for M365 TAI lives in the SMARTHAUS repo: `docs/projects/m365-tai/NORTH_STAR.md`.
