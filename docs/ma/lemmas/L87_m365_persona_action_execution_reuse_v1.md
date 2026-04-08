# Lemma L87 — M365 Persona-Action Execution Reuse v1

## Claim

The mapped persona-action layer can be reduced deterministically into predecessor-certified reuse versus fresh proof scope.

For the fixed repo state used by `G3`:

- `115` mapped unique persona-facing aliases are partitioned into:
  - `33` reusable `green`
  - `1` reusable `approval-gated`
  - `1` reusable `actor-tier-gated`
  - `24` reusable `fenced`
  - `56` remaining aliases requiring fresh live proof in `G4`
- `265` mapped active persona/action pairs are partitioned into:
  - `135` reusable `green`
  - `1` reusable `approval-gated`
  - `1` reusable `actor-tier-gated`
  - `72` reusable `fenced`
  - `56` remaining mapped pairs requiring fresh live proof in `G4`
- there are `0` mixed-reuse aliases once `G2` pair truth and predecessor direct evidence are joined deterministically

## Construction

`G3` joins three fixed sources of truth:

1. the `G2` mapping audit pair classifier
2. the predecessor direct-support certification matrix from `F4`
3. the explicit direct supplemental governance boundary for `ca.policy_create` and `users.disable`

The join rule is fail-closed:

- if a mapped persona alias resolves through the canonical crosswalk and its direct target was already proven `green`, inherit `green`
- if the alias was already proven at the approval boundary, inherit `approval-gated`
- if the alias was already proven only at the actor-tier denial boundary, inherit `actor-tier-gated`
- if the canonical direct target was previously fenced, inherit `fenced`
- otherwise keep the mapped pair in `requires-live-proof`

## Why It Matters

This lemma is the bridge between mapping truth and final workforce certification.
It prevents `G4` from re-testing already-proven direct actions while also preventing wrapper aliases from inheriting proof they do not actually own.

## Boundaries

- `L87` does not certify dead-routed or stubbed aliases.
- `L87` does not upgrade wrapper aliases to `green` without predecessor evidence.
- `L87` only narrows the remaining live-proof scope for `G4`.

## Artifacts

- `invariants/lemmas/L87_m365_persona_action_execution_reuse_v1.yaml`
- `notebooks/m365/INV-M365-CM-persona-action-execution-reuse-v1.ipynb`
- `notebooks/lemma_proofs/L87_m365_persona_action_execution_reuse_v1.ipynb`
- `artifacts/scorecards/scorecard_l87.json`
- `configs/generated/persona_action_execution_reuse_v1_verification.json`
