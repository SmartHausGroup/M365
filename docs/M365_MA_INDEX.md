# M365 — Mathematical Assurance (MA) index

This repo’s MA artifacts: contract, math, invariants, lemmas, verification scripts, notebooks, CI.

- **Contract and math:** `docs/contracts/caio-m365/`
  - INTENT.md, MATHEMATICS.md, M365_MASTER_CALCULUS.md, ACTION_SPECIFICATION.md
  - LEMMAS.md, LEMMA_L1.md–LEMMA_L4.md
- **Full M365 capability (master equation for all operations):** `docs/contracts/M365_MASTER_CALCULUS_FULL.md` — \(\mathcal{O}\) = 260 actions; full enumeration and process.
- **Master calculus for all actions:** `docs/contracts/M365_MASTER_CALCULUS_ACTIONS.md` — \(\mathcal{O}\), \(\mathcal{O}_m\), \(\mathcal{S}_{\texttt{action}}\) for every action (9 implemented, 251 planned).
- **Capability registry:** `registry/capability_registry.yaml` — canonical list of 260 actions. Build from universe: `scripts/ci/build_capability_registry.py`. Verify: `scripts/ci/verify_capability_registry.py` → `configs/generated/capability_registry_verification.json`.
- **Universe list:** `docs/contracts/M365_CAPABILITIES_UNIVERSE.md` — human-readable list of all capabilities.
- **Invariants:** `invariants/`
  - INDEX.yaml, INV-CAIO-M365-001.yaml, INV-CAIO-M365-002.yaml, INV-CAIO-M365-003.yaml, INV-M365-AUDIT-001.yaml
- **Verification scripts:** `scripts/ci/`
  - verify_caio_m365_contract.py, verify_capability_registry.py, verify_m365_idempotency.py, verify_m365_auth.py, verify_m365_audit.py
- **Notebooks:** `notebooks/`
  - ma_caio_m365_contract.ipynb, ma_m365_idempotency.ipynb, ma_m365_auth.ipynb, ma_m365_audit.ipynb, ma_m365_master.ipynb
- **CI:** `.github/workflows/ci.yml` (MA verification steps and artifact checks)

The overall plan (North Star) for M365 TAI lives in the SMARTHAUS repo: `docs/projects/m365-tai/NORTH_STAR.md`.
