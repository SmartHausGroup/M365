# M365 Persona-Action Certification

## Status

`G0` and `G1` are complete. The workforce-graph certification initiative now has a frozen baseline plus notebook-backed persona reachability truth. `G2` mapping / orphan / stub audit is the next act.

## Purpose

This initiative exists because the direct instruction surface is now truthfully classified, but that is still not the same as certifying the workforce graph itself.

The user requirement is stricter:

- every persona must be reachable or fenced
- every persona-facing action must be mapped or classified
- any orphaned, dead-routed, or stubbed surface must be explicit
- no persona capability can be implied just because some lower-level action exists elsewhere in the repo

## G0 Workforce Graph Lock

`G0` froze the current repo truth before any reachability or execution claims:

- `59` agents in `registry/agents.yaml`
- `59` authoritative personas in `registry/persona_registry_v2.yaml`
- `54` active personas
- `5` planned personas
- `5` contract-only personas
- `184` unique persona-facing allowed-action aliases
- `41` approval rules across the persona surface

The five current contract-only personas are:

- `app-store-optimizer`
- `instagram-curator`
- `reddit-community-builder`
- `tiktok-strategist`
- `twitter-engager`

## Predecessor Direct-Surface Truth Reused By This Initiative

`G0` also locked the predecessor direct-surface result from the completed direct full-surface certification initiative:

- `155` direct instruction actions
- `64` certified live-green direct actions
- `91` fenced direct actions

This predecessor evidence will be reused in later phases where a persona-facing action truly maps onto a previously certified direct action.

## What G0 Proved

`G0` does not yet classify final reachability, orphan status, or execution truth. It freezes the raw workforce graph and the candidate problem zones that later phases must resolve.

### 1. Exact-name overlap between persona aliases and direct actions is tiny

The raw persona/action layer and the direct instruction layer almost never match by exact action id:

- `184` persona-facing aliases
- `155` direct instruction actions
- only `2` exact-name overlaps:
  - `create_plan`
  - `list_plans`

That means workforce certification cannot rely on raw string equality. `G2` must explicitly resolve translation, mapping, and dead-surface truth.

### 2. Candidate orphan mismatch zones are large

Because the persona/action layer and direct instruction layer use different vocabularies:

- `182` persona-facing aliases currently have no exact direct-action name match
- `153` direct instruction actions currently have no exact persona-alias name match

These are candidate mismatch zones, not final orphan counts. They exist to force the later mapping audit to be explicit instead of assumed.

### 3. The known stub perimeter is still material

`G0` froze the current known legacy-stub perimeter at:

- `8` known stub agents
- `46` currently attached allowed actions across those agents

Current known stub agents:

- `it-operations-manager`
- `website-operations-specialist`
- `project-coordination-agent`
- `client-relationship-agent`
- `compliance-monitoring-agent`
- `recruitment-assistance-agent`
- `financial-operations-agent`
- `knowledge-management-agent`

This perimeter must be re-audited in `G2` because the attached action total now exceeds the earlier predecessor baseline and therefore cannot be assumed stable.

### 4. The predecessor crosswalk gap still matters

The predecessor direct-surface initiative already proved:

- `125` persona-facing aliases sit outside the current direct crosswalk

`G0` carries that forward as a locked inherited blocker class. The workforce program must now resolve those aliases truthfully rather than assume they are supported.

## G0 Closeout

`G0` is green because the workforce graph is now frozen truthfully before certification continues:

- the persona universe is locked
- the persona-facing action universe is locked
- the predecessor direct-support matrix is locked
- the contract-only personas are explicit
- the candidate mismatch zones are explicit
- the current stub perimeter is explicit

The next act is `G1`, which will certify persona reachability through the governed runtime surfaces.

## G1 Persona Reachability Certification

`G1` certifies persona reachability through the governed runtime surfaces. This phase does not yet classify mapping, orphan truth, or execution truth; it only proves whether personas are actually reachable and whether planned personas stay fenced from action execution.

### What G1 Proved

- `59/59` authoritative personas resolve by canonical persona id through `/personas/resolve`
- `59/59` authoritative personas resolve by display name through `/personas/resolve`
- `59/59` authoritative personas expose `/personas/{target}/state`
- the `54` active personas remain the action-eligible workforce surface
- the `5` planned personas remain reachable as delegation targets but fail closed on action execution with `persona_inactive:<persona_id>`

The five planned personas that remain reachable but action-fenced are:

- `app-store-optimizer`
- `instagram-curator`
- `reddit-community-builder`
- `tiktok-strategist`
- `twitter-engager`

### Notebook-Backed Evidence

`G1` is now backed by a phase-specific proof chain instead of relying only on older delegation notebooks:

- [L85_m365_persona_action_reachability_certification_v1.md](/Users/smarthaus/Projects/GitHub/M365/docs/ma/lemmas/L85_m365_persona_action_reachability_certification_v1.md)
- [L85_m365_persona_action_reachability_certification_v1.yaml](/Users/smarthaus/Projects/GitHub/M365/invariants/lemmas/L85_m365_persona_action_reachability_certification_v1.yaml)
- [INV-M365-CJ-persona-action-reachability-certification-v1.ipynb](/Users/smarthaus/Projects/GitHub/M365/notebooks/m365/INV-M365-CJ-persona-action-reachability-certification-v1.ipynb)
- [L85_m365_persona_action_reachability_certification_v1.ipynb](/Users/smarthaus/Projects/GitHub/M365/notebooks/lemma_proofs/L85_m365_persona_action_reachability_certification_v1.ipynb)
- [scorecard_l85.json](/Users/smarthaus/Projects/GitHub/M365/artifacts/scorecards/scorecard_l85.json)
- [persona_action_reachability_certification_v1_verification.json](/Users/smarthaus/Projects/GitHub/M365/configs/generated/persona_action_reachability_certification_v1_verification.json)

### G1 Closeout

`G1` is green because the workforce runtime now proves:

- the full authoritative persona roster is reachable on persona surfaces
- humanized delegation resolution stays aligned with the authoritative registry
- planned personas do not silently become action-capable
- the initiative can now move to `G2` with reachability truth frozen

The next act is `G2`, which will classify persona-facing actions as mapped, orphaned, dead-routed, legacy-stubbed, or fenced.
