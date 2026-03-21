# Lemma L20 — Service Provisioning Site Detection Alignment

## Claim

`provision_service` remains deterministic for existing SMARTHAUS services if:

1. the service group is resolved by `mail_nickname` first;
2. the existing SharePoint site is resolved through the group's actual root-site
   relationship before any guessed `/sites/{mail_nickname}` path is used; and
3. path lookup remains only as a bounded fallback for freshly created groups
   whose root-site relationship is not yet observable.

## Why This Matters

`C1C` failed on the live HR service surface because the runtime assumed the
existing group-connected site would live at `/sites/hr`. The live tenant proved
the opposite: the group behind `mail_nickname=hr` exists, but its SharePoint
site lives at `/sites/hr2`. The runtime has to prefer the group-root site
relationship or it will mis-detect existing service sites.

## Inputs

- `src/provisioning_api/m365_provision.py`
- `src/smarthaus_graph/client.py`
- `tests/test_m365_provision.py`
- `artifacts/certification/m365-v1-candidate-52ca494/transcripts/mutation_surface_transcript.json`

## Outputs

- deterministic existing-service site resolution
- bounded regression coverage for group-root-site preference and path fallback
- live re-proof target for the `provision_service` certification row

## Proof Sketch

If an existing Microsoft 365 group can be resolved by `mail_nickname`, then the
runtime can query the group's root SharePoint site directly. If that root-site
relationship returns an `id`, then the existing service site is fully
determined and no guessed site path is needed. If the root-site relationship is
not yet available, a bounded path lookup remains acceptable as a fallback for
freshly created groups. Under those conditions, existing services with
non-standard site slugs, including the live HR surface at `/sites/hr2`, remain
deterministically detectable.

## Runtime Bindings

- `src/smarthaus_graph/client.py`
- `src/provisioning_api/m365_provision.py`
- `tests/test_m365_provision.py`

## Failure Boundary

`L20` fails closed if:

- the runtime still prefers guessed `/sites/{mail_nickname}` paths over the
  group-root site for existing groups;
- the group-root site is ignored when it returns a valid `id`; or
- the bounded fallback path is removed without a replacement for fresh-group
  propagation lag.
