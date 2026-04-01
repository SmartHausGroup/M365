# L76 — M365 Activated Persona Surface v1

## Lemma

The current activated persona surface on `feature/m365_personas` may be
claimed as certified only when the authoritative registries partition the
workforce into exactly 34 registry-backed personas and 5 deferred
external-platform personas, the P2B through P2D wave scorecards are green, the
current commercialization boundary excludes the deferred external personas, and
the same fixed branch state reproduces the same `34/5` partition and claim set.

## Plan Reference

`plan:m365-post-expansion-promotion-and-persona-activation:P2E`

## Assumptions

- `registry/persona_registry_v2.yaml` is the authoritative persona roster.
- `registry/persona_capability_map.yaml` is the authoritative capability map.
- `registry/activated_persona_surface_v1.yaml` is the authoritative P2E closeout contract.
- `artifacts/scorecards/scorecard_l73.json`, `scorecard_l74.json`, and `scorecard_l75.json` are the authoritative prior-wave scorecards.
- `docs/commercialization/m365-activated-persona-surface-v1.md` is the authoritative current branch commercialization boundary.
- `docs/commercialization/m365-workforce-packaging-v1.md` remains the historical E9A baseline and must not be mistaken for the current branch activation boundary.

## Certified Partition

- **Registry-backed / active:** 34
- **Deferred external / contract-only:** 5
- **Total personas:** 39
- **Total allowed persona-actions:** 298
- **Departments with active personas:** 10

## Deferred External Personas

- `instagram-curator`
- `tiktok-strategist`
- `reddit-community-builder`
- `twitter-engager`
- `app-store-optimizer`

These personas remain outside the current certified activated surface because
they require external-platform APIs and credentials that are not yet implemented
in this repo.

## Notebook Evidence

- Primary: `notebooks/m365/INV-M365-BX-activated-persona-surface-v1.ipynb`
- Proof: `notebooks/lemma_proofs/L76_m365_activated_persona_surface_v1.ipynb`

## Boundary Conditions

- If actual registry-backed personas != 34 -> fail closed.
- If actual deferred external personas != 5 -> fail closed.
- If any deferred external persona has non-zero actions -> fail closed.
- If any prior wave scorecard is missing or non-green -> fail closed.
- If commercialization language implies `39/39` active personas or includes the deferred external personas in the active surface -> fail closed.
