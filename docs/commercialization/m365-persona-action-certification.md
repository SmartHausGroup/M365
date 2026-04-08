# M365 Persona-Action Certification

## Status

`G0` through `G5` are complete as the historical predecessor certification, and the successor remediation initiative now closes with the live `P5` recertification.

Current published truth:

- `172` live unique persona-facing aliases
- `445` live active persona/action pairs
- unique-alias closeout:
  - `103` `green`
  - `36` `approval-gated`
  - `1` `actor-tier-gated`
  - `32` `fenced`
- active-pair closeout:
  - `360` `green`
  - `49` `approval-gated`
  - `1` `actor-tier-gated`
  - `35` `fenced`

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

## G2 Mapping / Orphan / Stub Audit

`G2` closes the first real workforce-graph truth gap: it does not ask whether an action exists somewhere in the repo, it asks whether the action is actually usable by the personas that claim it.

### What G2 Proved

The authoritative workforce graph now classifies all `184` unique persona-facing aliases with no unclassified residue:

- `115` unique aliases are `mapped`
- `48` unique aliases are `legacy-stubbed`
- `21` unique aliases are `dead-routed`
- `0` unique aliases are `orphaned`
- `0` unique aliases are `fenced` at the alias level because the current planned personas do not contribute active allowed-action rows

At the active persona/action-pair level, the classifier closes all `430` active pairs:

- `265` persona/action pairs are `mapped`
- `49` persona/action pairs are `legacy-stubbed`
- `116` persona/action pairs are `dead-routed`
- `0` persona/action pairs are `orphaned`

The reverse orphan check over the direct instruction surface also proves that `84` direct actions still have no active persona owner in the workforce graph.

### What Changed In The Stub Boundary

`G2` confirms the earlier known stub perimeter and expands it by `8` additional pure literal handlers that were previously easy to over-count as real runtime support:

- `archive-project`
- `conflict.resolve`
- `deprovision-client-services`
- `email.classify`
- `follow-up.schedule`
- `get-client-status`
- `reminder.send`
- `update-project-status`

These branches return synthetic literal payloads without awaiting a real runtime path, so they are now counted as `legacy-stubbed` rather than `mapped`.

### What G2 Revealed About The Workforce Graph

The largest problem is not orphan aliases. It is mixed ownership truth.

`23` aliases are now proven mixed across the workforce graph, which means the same alias can be `mapped` for one specialist persona and `dead-routed` or `legacy-stubbed` for another. Examples include:

- `sites.list`
- `files.search`
- `reports.users_active`
- `health.overview`
- `mail.reply`
- `teams.list`
- `client.follow-up`
- `task.create`

That means workforce certification cannot be reduced to alias-level support alone. `G4` must certify the persona/action pairs explicitly.

### Notebook-Backed Evidence

`G2` is now backed by a dedicated proof chain:

- [L86_m365_persona_action_mapping_audit_v1.md](/Users/smarthaus/Projects/GitHub/M365/docs/ma/lemmas/L86_m365_persona_action_mapping_audit_v1.md)
- [L86_m365_persona_action_mapping_audit_v1.yaml](/Users/smarthaus/Projects/GitHub/M365/invariants/lemmas/L86_m365_persona_action_mapping_audit_v1.yaml)
- [INV-M365-CK-persona-action-mapping-audit-v1.ipynb](/Users/smarthaus/Projects/GitHub/M365/notebooks/m365/INV-M365-CK-persona-action-mapping-audit-v1.ipynb)
- [L86_m365_persona_action_mapping_audit_v1.ipynb](/Users/smarthaus/Projects/GitHub/M365/notebooks/lemma_proofs/L86_m365_persona_action_mapping_audit_v1.ipynb)
- [scorecard_l86.json](/Users/smarthaus/Projects/GitHub/M365/artifacts/scorecards/scorecard_l86.json)
- [persona_action_mapping_audit_v1_verification.json](/Users/smarthaus/Projects/GitHub/M365/configs/generated/persona_action_mapping_audit_v1_verification.json)

### G2 Closeout

`G2` is green because the workforce graph now has complete mapping truth:

- every active persona/action pair is classified
- no active persona-facing alias remains orphaned
- the dead-routed perimeter is explicit instead of implied
- the expanded synthetic stub perimeter is explicit instead of hidden inside literal handlers
- reverse direct orphans are explicit instead of assumed away

## G3 Unique Action Execution Reuse

`G3` does not try to prove new behavior yet. It joins the `G2` mapped workforce graph to the predecessor direct-support matrix so the workforce program can reuse already-proven execution truth where that reuse is explicit and fail-closed.

### What G3 Proved

At the mapped unique-alias layer, the `115` aliases that survived `G2` now split cleanly into:

- `33` reusable `green`
- `1` reusable `approval-gated`
- `1` reusable `actor-tier-gated`
- `24` reusable `fenced`
- `56` remaining unique aliases that still require fresh live proof in `G4`

At the mapped active persona/action-pair layer, the `265` mapped pairs now split into:

- `135` reusable `green`
- `1` reusable `approval-gated`
- `1` reusable `actor-tier-gated`
- `72` reusable `fenced`
- `56` remaining mapped pairs that still require fresh live proof in `G4`

The join is now deterministic and owner-aware:

- the canonical crosswalked mapped surface no longer leaves any unproven reuse residue
- `ca.policy_create` is carried forward as a reusable `approval-gated` path
- `users.disable` is carried forward as a reusable `actor-tier-gated` path
- the remaining live-proof scope is exactly the wrapper-owned mapped surface
- there are `0` mixed-reuse aliases after the `G2` pair classifier is joined to predecessor direct evidence

### What G3 Leaves For G4

`G4` is now narrowed to the `56` mapped persona/action pairs that still need direct workforce proof. That remaining scope is concentrated in the wrapper layer, including:

- `audit-operations` audit reads
- `calendar-management-agent` legacy scheduling wrappers
- `email-processing-agent` reply/forward/respond/archive wrappers
- `m365-administrator` wrapper reads like `users.list`, `users.read`, `sites.list`, `sites.root`, `files.search`, and `files.share`
- `reports`, `service-health`, `teams-manager`, `ucp-administrator`, and other wrapper-owned specialist paths

### Notebook-Backed Evidence

`G3` is now backed by a dedicated proof chain:

- [L87_m365_persona_action_execution_reuse_v1.md](/Users/smarthaus/Projects/GitHub/M365/docs/ma/lemmas/L87_m365_persona_action_execution_reuse_v1.md)
- [L87_m365_persona_action_execution_reuse_v1.yaml](/Users/smarthaus/Projects/GitHub/M365/invariants/lemmas/L87_m365_persona_action_execution_reuse_v1.yaml)
- [INV-M365-CM-persona-action-execution-reuse-v1.ipynb](/Users/smarthaus/Projects/GitHub/M365/notebooks/m365/INV-M365-CM-persona-action-execution-reuse-v1.ipynb)
- [L87_m365_persona_action_execution_reuse_v1.ipynb](/Users/smarthaus/Projects/GitHub/M365/notebooks/lemma_proofs/L87_m365_persona_action_execution_reuse_v1.ipynb)
- [scorecard_l87.json](/Users/smarthaus/Projects/GitHub/M365/artifacts/scorecards/scorecard_l87.json)
- [persona_action_execution_reuse_v1_verification.json](/Users/smarthaus/Projects/GitHub/M365/configs/generated/persona_action_execution_reuse_v1_verification.json)

### G3 Closeout

`G3` is green because the workforce program no longer has to guess where predecessor execution evidence applies:

- reusable direct-surface proof is explicit
- approval and actor-tier boundaries remain explicit instead of being over-claimed as `green`
- the remaining `G4` live-proof scope is finite and published
- the workforce certification program can now move to pair-level proof without re-testing already-proven direct actions

## G4 Persona/Action Certification

`G4` executed the remaining `56` mapped persona/action pairs through the governed `/actions/{agent}/{action}` route using JWT-backed actor identity and a live local OPA server.

### What G4 Proved

The irreducible wrapper-owned route surface now closes at:

- `1` `green` pair:
  - `m365-administrator::users.read`
- `15` `permission-blocked` pairs:
  - these legacy alias names are not granted by any tier in `registry/permission_tiers.yaml`
- `40` `fenced` pairs:
  - these stop at the OPA layer with `action_not_allowed`

The `15` permission-blocked aliases are:

- `add-workspace-members`
- `availability.check`
- `create-channels`
- `create-project`
- `create-workspace`
- `deployment.preview`
- `email.archive`
- `email.forward`
- `email.respond`
- `email.send_individual`
- `employee.onboard`
- `get-team-status`
- `list-projects`
- `meeting.organize`
- `provision-client-services`

The `40` fenced pairs are not dead routes. Many of them still have tier support at the domain layer, but the governed route denies them because the current OPA surface does not allow those persona/action combinations. That fenced set includes:

- `audit-operations` audit reads
- `m365-administrator` wrapper reads like `sites.list`, `sites.root`, `files.search`, `files.share`, and `users.list`
- `reports` activity and usage reads
- `service-health` wrappers
- `teams-manager` Teams / chat / channel wrappers
- `ucp-administrator` admin wrappers

### Notebook-Backed Evidence

`G4` is now backed by a dedicated proof chain:

- [L88_m365_persona_action_route_certification_v1.md](/Users/smarthaus/Projects/GitHub/M365/docs/ma/lemmas/L88_m365_persona_action_route_certification_v1.md)
- [L88_m365_persona_action_route_certification_v1.yaml](/Users/smarthaus/Projects/GitHub/M365/invariants/lemmas/L88_m365_persona_action_route_certification_v1.yaml)
- [INV-M365-CN-persona-action-route-certification-v1.ipynb](/Users/smarthaus/Projects/GitHub/M365/notebooks/m365/INV-M365-CN-persona-action-route-certification-v1.ipynb)
- [L88_m365_persona_action_route_certification_v1.ipynb](/Users/smarthaus/Projects/GitHub/M365/notebooks/lemma_proofs/L88_m365_persona_action_route_certification_v1.ipynb)
- [scorecard_l88.json](/Users/smarthaus/Projects/GitHub/M365/artifacts/scorecards/scorecard_l88.json)
- [persona_action_route_certification_v1_verification.json](/Users/smarthaus/Projects/GitHub/M365/configs/generated/persona_action_route_certification_v1_verification.json)

### G4 Closeout

`G4` is green because the remaining mapped route surface is no longer implied:

- the last reusable live-green wrapper path is explicit
- the unsupported legacy alias perimeter is explicit at the permission-tier layer
- the policy-fenced wrapper perimeter is explicit at the OPA layer
- the initiative can now close with a full workforce matrix

## G5 Closeout (Historical Baseline)

The predecessor workforce graph was fully classified for the pre-remediation state, but that closeout is now historical rather than current.

Historical `G5` totals:

- `184` unique persona-facing aliases
- `430` active persona/action pairs

## P5 Post-Remediation Recertification Closeout

`P5` republishes the workforce graph against the live post-remediation runtime instead of the stale historical `G5` surface.

### What Changed

The live workforce universe shifted materially during remediation:

- historical `G5` publication: `184` unique aliases / `430` active pairs
- live post-remediation universe: `172` unique aliases / `445` active pairs

The support surface is now narrower, cleaner, and truthful:

- `0` `permission-blocked`
- `0` `legacy-stubbed`
- `0` `dead-routed`
- `0` `orphaned`

Everything non-green is now explicit either as approval/actor-tier governance or as the fenced unsupported M365-only perimeter.

### Final Unique-Alias Matrix

All `172` live unique persona-facing aliases now close at:

- `103` `green`
- `36` `approval-gated`
- `1` `actor-tier-gated`
- `32` `fenced`
- `0` `permission-blocked`
- `0` `legacy-stubbed`
- `0` `dead-routed`
- `0` `orphaned`

### Final Active Persona/Action Matrix

All `445` live active persona/action pairs now close at:

- `360` `green`
- `49` `approval-gated`
- `1` `actor-tier-gated`
- `35` `fenced`
- `0` `permission-blocked`
- `0` `legacy-stubbed`
- `0` `dead-routed`
- `0` `orphaned`

### Preserved Governance Boundaries

The preserved actor-tier-gated path is:

- `m365-administrator::users.disable`

The base `approval-gated` totals above classify default-parameter approval truth. Additional conditional approval overlays remain explicit and intentional:

- `calendar-management-agent::meeting.organize` when attendee or external-attendee thresholds are exceeded
- `email-processing-agent::email.respond` when priority or sensitivity triggers approval
- `outreach-coordinator::email.send_bulk` when bulk-recipient thresholds are exceeded
- `project-coordination-agent::task.assign` when hours or priority thresholds are exceeded
- `project-shipper::task.assign` when hours or priority thresholds are exceeded
- `support-responder::mail.send` when priority or sensitivity triggers approval

### Explicit Fenced Perimeter

The final fenced perimeter is the explicit runtime `unsupported_m365_only_action` surface still owned by active personas:

- `audit.prepare`
- `backup.restore`
- `budget.track`
- `campaign.create`
- `candidate.screen`
- `cdn.purge`
- `compliance.check`
- `conflict.resolve`
- `content.curate`
- `dns.update`
- `document.index`
- `email.classify`
- `engagement.plan`
- `expense.approve`
- `expert.connect`
- `feedback.analyze`
- `feedback.collect`
- `forecast.update`
- `invoice.process`
- `offer.prepare`
- `onboarding.initiate`
- `performance.optimize`
- `policy.create`
- `policy.validate`
- `relationship.score`
- `remediation.plan`
- `review.initiate`
- `search.optimize`
- `ssl.renew`
- `training.recommend`
- `violation.report`
- `website.deploy`

### Notebook-Backed Evidence

`P5` is now backed by the final successor proof chain:

- [L96_m365_persona_action_recertification_closeout_v1.md](/Users/smarthaus/Projects/GitHub/M365/docs/ma/lemmas/L96_m365_persona_action_recertification_closeout_v1.md)
- [L96_m365_persona_action_recertification_closeout_v1.yaml](/Users/smarthaus/Projects/GitHub/M365/invariants/lemmas/L96_m365_persona_action_recertification_closeout_v1.yaml)
- [INV-M365-DF-persona-action-recertification-closeout-v1.ipynb](/Users/smarthaus/Projects/GitHub/M365/notebooks/m365/INV-M365-DF-persona-action-recertification-closeout-v1.ipynb)
- [L96_m365_persona_action_recertification_closeout_v1.ipynb](/Users/smarthaus/Projects/GitHub/M365/notebooks/lemma_proofs/L96_m365_persona_action_recertification_closeout_v1.ipynb)
- [scorecard_l96.json](/Users/smarthaus/Projects/GitHub/M365/artifacts/scorecards/scorecard_l96.json)
- [persona_action_recertification_closeout_v1_verification.json](/Users/smarthaus/Projects/GitHub/M365/configs/generated/persona_action_recertification_closeout_v1_verification.json)

### P5 Closeout

The successor remediation initiative is complete.

The workforce graph no longer carries any residual dead-route, legacy-stub, permission-blocked, or orphaned claims. The remaining non-green surface is explicit, governed, and truthful.
