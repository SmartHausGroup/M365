# Lemma L86 — M365 Persona-Action Mapping Audit v1

## Claim

The persona-to-action certification initiative may publish `G2` mapping truth iff:

1. every authoritative persona-facing action alias is classified as `mapped`, `legacy-stubbed`, `dead-routed`, `orphaned`, or `fenced`,
2. the classification is computed from the authoritative persona registry plus the real runtime routing and dispatch surfaces,
3. synthetic literal-only persona handlers are not miscounted as real runtime support, and
4. the reverse orphan check over the direct instruction surface is published explicitly.

If any active persona/action pair remains unclassified, `G2` must stay red and the initiative may not continue to `G3`.

## Definitions

- `MappedPair(P, A)`: persona `P` exposes action alias `A` and the runtime either maps `A` through the direct crosswalk or implements `P/A` through a non-stub dispatch branch.
- `LegacyStubbedPair(P, A)`: persona `P` exposes action alias `A`, but the only available branch is a legacy or synthetic literal handler.
- `DeadRoutedPair(P, A)`: persona `P` exposes action alias `A`, routing resolves but no real persona-specific implementation exists.
- `OrphanedPair(P, A)`: persona `P` exposes action alias `A`, but neither routing nor runtime implementation exists.
- `ReverseDirectOrphan(D)`: direct instruction action `D` has no active persona owner through the workforce graph.

## Deterministic Formula

Let `U` be the unique persona-facing alias universe and `W` the active persona/action pair universe.

`G2_GO = Classified(U) AND Classified(W) AND ReverseOrphanAudit(D)`

For the current governed repo state:

- `|U| = 184`
- `|W| = 430`
- unique alias split = `115 mapped`, `48 legacy-stubbed`, `21 dead-routed`, `0 orphaned`, `0 fenced`
- pair split = `265 mapped`, `49 legacy-stubbed`, `116 dead-routed`, `0 orphaned`, `0 fenced`
- reverse direct orphans = `84`

## Proof Sketch

1. The authoritative registry fixes the workforce alias universe at `184` unique aliases across `54` active personas.
2. The v2 expansion registries and cross-workload catalog fix the canonical direct-action crosswalk.
3. The live dispatcher in `src/ops_adapter/actions.py` distinguishes real awaited handlers from pure literal placeholders.
4. Executor routing distinguishes dead-routed paths from truly orphaned paths.
5. The phase-specific notebook recomputes the classification and asserts the published counts.
6. Therefore `G2` mapping truth is publishable iff the notebook-backed classifier remains green.

## Failure Boundaries

- Any active persona/action pair that remains unclassified.
- Any literal-only synthetic handler counted as mapped.
- Any dead-routed or stubbed alias omitted from the published audit.
- Any reverse direct orphan omitted from the published audit.

## Traceability

- `invariants/lemmas/L86_m365_persona_action_mapping_audit_v1.yaml`
- `notebooks/m365/INV-M365-CK-persona-action-mapping-audit-v1.ipynb`
- `notebooks/lemma_proofs/L86_m365_persona_action_mapping_audit_v1.ipynb`
- `artifacts/scorecards/scorecard_l86.json`
- `configs/generated/persona_action_mapping_audit_v1_verification.json`
