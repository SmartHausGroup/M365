# Lemma L19 — Approval Backend Reproof and Certification Re-Readiness

## Claim

The rebased multi-executor runtime is ready to reopen `C1A` if:

1. the exact standalone shell contract selects the SMARTHAUS tenant and
   enables the controlled certification toggles;
2. the approvals backend is addressed through pinned SharePoint `site_id` and
   `list_id`, not URL-based site discovery;
3. the bounded SharePoint executor remains the projected approval executor; and
4. the live approval list metadata and live approval list items endpoints both
   return success through the SharePoint executor path.

## Why This Matters

`B7E` exists to remove the last stale readiness blocker before `C1A` resumes.
Earlier `C1A` evidence correctly blocked on SharePoint URL discovery, but the
tenant contract now pins the real SMARTHAUS approvals site and list. The
readiness packet must therefore be refreshed against the actual bounded
executor path, not the old discovery failure story.

## Inputs

- `artifacts/b7d_live_executor_validation.json`
- `/Users/smarthaus/Projects/GitHub/UCP/tenants/smarthaus.yaml`
- `src/ops_adapter/approvals.py`
- `artifacts/certification/m365-v1-candidate-52ca494/prerequisites_report.json`
- `artifacts/certification/m365-v1-candidate-52ca494/README.md`
- `artifacts/certification/m365-v1-candidate-52ca494/operator_checklist.md`

## Outputs

- exact-shell approval re-proof artifact
- refreshed `C1A` readiness packet
- explicit `GO/NO-GO` on whether live certification may resume

## Proof Sketch

If the SMARTHAUS tenant contract projects the bounded SharePoint executor as
the approval executor and carries explicit `approvals_site_id` and
`approvals_list_id`, then the approval backend no longer depends on
URL-discovery of `/sites/...`. If the exact shell contract activates the tenant
selection and controlled certification toggles, and the live Graph probe
returns `200` on both the approval list metadata route and the approval list
items route through that SharePoint executor, then the approval backend is
reachable on the rebased target. Under those conditions, the stale `NO-GO`
packet can be refreshed to a `GO` readiness posture for `C1A`.

## Runtime Bindings

- `src/ops_adapter/approvals.py`
- `artifacts/b7e_approval_backend_reproof.json`
- `artifacts/certification/m365-v1-candidate-52ca494/prerequisites_report.json`
- `artifacts/certification/m365-v1-candidate-52ca494/README.md`
- `artifacts/certification/m365-v1-candidate-52ca494/operator_checklist.md`

## Failure Boundary

`B7E` fails closed if:

- the exact shell contract is incomplete;
- the approval executor is no longer the bounded SharePoint executor;
- the pinned site or list IDs do not resolve;
- either approval probe returns a non-success status; or
- the readiness packet reopens `C1A` without real bounded-executor proof.
