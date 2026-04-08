# Lemma L88 — M365 Persona-Action Route Certification v1

## Claim

The remaining `56` mapped persona/action pairs from `G3` can be classified deterministically at the governed `/actions/{agent}/{action}` route without leaving any unclassified residue.

For the fixed repo and tenant state used by `G4`:

- `56` remaining mapped persona/action pairs split into:
  - `1` `green`
  - `15` `permission-blocked`
  - `40` `fenced`
- the lone `green` pair is `m365-administrator::users.read`
- all `15` `permission-blocked` pairs use legacy alias names that are not granted by any permission tier in `registry/permission_tiers.yaml`
- all `40` `fenced` pairs stop at the OPA boundary with `action_not_allowed`, even though their underlying domains remain tier-allowed for at least one tier

## Construction

`G4` probes the governed runtime path directly:

1. load the `56` remaining mapped pairs from `configs/generated/persona_action_execution_reuse_v1_verification.json`
2. execute each pair through `/actions/{agent}/{action}`
3. use JWT-backed actor identity for `phil@smarthausgroup.com`
4. use the local tenant context `smarthaus`
5. enforce OPA decisions through a live local OPA server at `http://127.0.0.1:8181`

The classifier is fail-closed:

- `200` success on a real route path is `green`
- `403` with `tier_not_allowed:*` or other tier/permission denial is `permission-blocked`
- `403` with `action_not_allowed` is `fenced`
- no remaining pair is allowed to stay unclassified

## Why It Matters

`L88` closes the workforce-certification gap that remained after `G3`.
It proves the final governed route truth for the wrapper-owned mapped surface instead of inferring support from lower-level direct action evidence.

## Boundaries

- `L88` does not upgrade dead-routed or legacy-stubbed aliases; those were already closed in `G2`
- `L88` does not widen OPA policy or permission tiers
- `L88` only classifies the remaining mapped persona/action route surface truthfully

## Artifacts

- `invariants/lemmas/L88_m365_persona_action_route_certification_v1.yaml`
- `notebooks/m365/INV-M365-CN-persona-action-route-certification-v1.ipynb`
- `notebooks/lemma_proofs/L88_m365_persona_action_route_certification_v1.ipynb`
- `artifacts/scorecards/scorecard_l88.json`
- `configs/generated/persona_action_route_certification_v1_verification.json`
