# Lemma L85 — M365 Persona-Action Reachability Certification v1

## Claim

The persona-to-action certification initiative may publish `G1` reachability truth iff:

1. every authoritative persona resolves by canonical id through the governed persona surface,
2. every authoritative persona resolves by human display name through the governed persona surface,
3. every authoritative persona exposes persona state through the governed runtime,
4. planned personas remain reachable as delegation targets but fail closed on action execution, and
5. those claims are frozen in a phase-specific notebook-backed artifact rather than inferred from older delegation notebooks alone.

If any of those conditions fails, `G1` must remain unpublished and the initiative must stop before `G2`.

## Definitions

- `CanonicalResolve(P)`: `/personas/resolve?query=<persona_id>` returns the canonical persona for persona `P`.
- `DisplayResolve(P)`: `/personas/resolve?query=<display_name>` returns the canonical persona for persona `P`.
- `StateReachable(P)`: `/personas/{target}/state` returns persona state for persona `P`.
- `PlannedFence(P)`: for a planned persona `P`, `/actions/{P}/health.overview` fails closed with `persona_inactive:<P>` under the bounded header-fallback runtime probe.

## Deterministic Formula

Let `A` be the authoritative persona set, `A_active` the active subset, and `A_planned` the planned subset.

`ReachabilityCertified = (forall P in A, CanonicalResolve(P))`
`AND (forall P in A, DisplayResolve(P))`
`AND (forall P in A, StateReachable(P))`
`AND (forall P in A_planned, PlannedFence(P))`

For the current governed repo state:

- `|A| = 59`
- `|A_active| = 54`
- `|A_planned| = 5`

`G1_GO = ReachabilityCertified AND NotebookBacked(G1)`

## Proof Sketch

1. The authoritative persona registry fixes the persona universe at `59` personas with `54` active and `5` planned.
2. The governed runtime resolves persona targets through `resolve_persona_target`, which is backed by the authoritative persona registry and humanized delegation patterns.
3. The persona surfaces `/personas/resolve` and `/personas/{target}/state` expose the delegation and state paths without requiring action execution.
4. The action surface rejects planned personas before runtime execution by enforcing `persona_inactive:<persona_id>`.
5. The phase-specific `G1` notebook reproduces and asserts all four counts against the live runtime surface.
6. Therefore `G1` reachability may be published truthfully only when the notebook-backed evidence chain is green.

## Failure Boundaries

- Any persona that fails canonical-id resolution.
- Any persona that fails display-name resolution.
- Any persona that fails state-surface reachability.
- Any planned persona that executes or fails for a reason other than `persona_inactive:<persona_id>`.
- Any attempt to close `G1` without notebook-backed evidence.

## Traceability

- `invariants/lemmas/L85_m365_persona_action_reachability_certification_v1.yaml`
- `notebooks/m365/INV-M365-CJ-persona-action-reachability-certification-v1.ipynb`
- `notebooks/lemma_proofs/L85_m365_persona_action_reachability_certification_v1.ipynb`
- `artifacts/scorecards/scorecard_l85.json`
- `configs/generated/persona_action_reachability_certification_v1_verification.json`
