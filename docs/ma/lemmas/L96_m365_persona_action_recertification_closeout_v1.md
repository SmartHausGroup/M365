# Lemma L96 — M365 Persona-Action Recertification Closeout v1

## Claim

After `P1` through `P4` complete, the live active workforce graph can be recertified deterministically against the current repo truth without leaving any non-green residue outside the explicit fenced perimeter.

For the fixed post-remediation repo state used by `P5`:

- the live active workforce universe is `172` unique persona-facing aliases across `445` active persona/action pairs
- the final unique-alias matrix closes at:
  - `103` `green`
  - `36` `approval-gated`
  - `1` `actor-tier-gated`
  - `32` `fenced`
  - `0` `permission-blocked`
  - `0` `legacy-stubbed`
  - `0` `dead-routed`
  - `0` `orphaned`
- the final active persona/action matrix closes at:
  - `360` `green`
  - `49` `approval-gated`
  - `1` `actor-tier-gated`
  - `35` `fenced`
  - `0` `permission-blocked`
  - `0` `legacy-stubbed`
  - `0` `dead-routed`
  - `0` `orphaned`
- the fenced perimeter is exactly the explicit `unsupported_m365_only_action` runtime perimeter still owned by active personas
- the preserved actor-tier-gated pair is `m365-administrator::users.disable`

## Construction

`P5` re-certifies the workforce graph from the live post-remediation sources:

1. load the active persona graph from `registry/agents.yaml` and `registry/persona_registry_v2.yaml`
2. compute the live active universe from active personas only
3. derive the explicit fenced perimeter from the `unsupported_m365_only_action` dispatcher calls in `src/ops_adapter/actions.py`
4. resolve approval requirements through `src/smarthaus_common/approval_risk.py`
5. preserve `m365-administrator::users.disable` as the lone actor-tier-gated path
6. classify the remaining active pairs as `green`

The classifier is fail-closed:

- any active pair still landing in `permission-blocked`, `legacy-stubbed`, `dead-routed`, or `orphaned` would fail `P5`
- any alias omitted from the recertified live universe would fail `P5`
- any drift between the published `P5` artifact and the live post-remediation universe would fail `P5`

## Why It Matters

`L96` closes the successor remediation initiative.
It replaces the stale historical `G5` publication with the truthful post-remediation workforce graph and proves the backlog has been driven to either real support, explicit approval/actor-tier control, or explicit fenced unsupported status.

## Boundaries

- `L96` does not widen the runtime beyond the current post-`P4` truth
- `L96` does not claim that conditional approvals trigger under empty/default params
- `L96` does not erase the explicit M365-only unsupported perimeter; it freezes it as fenced truth
- `L96` only certifies the current repo-local workforce graph after the completed remediation program

## Artifacts

- `invariants/lemmas/L96_m365_persona_action_recertification_closeout_v1.yaml`
- `notebooks/m365/INV-M365-DF-persona-action-recertification-closeout-v1.ipynb`
- `notebooks/lemma_proofs/L96_m365_persona_action_recertification_closeout_v1.ipynb`
- `artifacts/scorecards/scorecard_l96.json`
- `configs/generated/persona_action_recertification_closeout_v1_verification.json`
