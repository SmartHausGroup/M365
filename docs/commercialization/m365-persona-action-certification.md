# M365 Persona-Action Certification

## Status

`G0` is complete. The workforce-graph certification initiative now has a frozen baseline for personas, persona-facing actions, predecessor direct-support evidence, candidate orphan mismatch zones, and the known stub perimeter. `G1` persona reachability certification is the next act.

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
