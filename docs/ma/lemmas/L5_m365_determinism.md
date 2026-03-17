# L5 — M365 Determinism Projection

## Claim

For fixed repository state, the supported action surface and governing contract projection are deterministic.

## Existing Proof Sources

- `notebooks/m365/INV-M365-C-001-determinism.ipynb`
- `registry/capability_registry.yaml`
- `src/provisioning_api/routers/m365.py`
- `docs/CAIO_M365_CONTRACT.md`

## Acceptance Evidence

- repeated extraction of the supported action set yields the same 9-action result
- the determinism notebook is present and recorded as the source notebook for this lemma

## Deterministic Surface

`Supported_v1 = RegistryImplemented ∩ RouterSupported ∩ PublishedContract`
