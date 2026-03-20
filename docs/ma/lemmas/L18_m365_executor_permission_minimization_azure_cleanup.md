# Lemma L18 — Executor Permission Minimization and Azure Cleanup

## Claim

The rebased multi-executor runtime can replace the legacy monolithic executor
without reducing the supported v1 surface if:

1. each supported v1 action maps deterministically to exactly one bounded
   executor domain;
2. each live executor app carries only the application roles needed for that
   bounded domain;
3. the tenant contract projects one bounded default executor and no longer uses
   the legacy monolithic executor as the active runtime default;
4. missing Azure app-role assignments are repaired before live validation; and
5. each bounded executor proves one representative app-only Graph path against
   the live SMARTHAUS tenant.

## Why This Matters

`B7D` is the act that makes the rebased multi-executor architecture real in the
tenant instead of only in repo documents and routing code. Without bounded
permission envelopes and live app-only proof, `C1A` would still be pointed at
an oversized or partially configured executor posture.

## Inputs

- `docs/commercialization/m365-v1-supported-surface.md`
- `docs/commercialization/m365-executor-domain-routing-and-minimum-permission-model.md`
- `/Users/smarthaus/Projects/GitHub/UCP/tenants/smarthaus.yaml`
- live Azure / Entra app registrations and service principals
- executor-aware runtime bindings in `src/provisioning_api/routers/m365.py`
  and `src/provisioning_api/m365_provision.py`

## Outputs

- per-domain permission matrix
- Azure cleanup execution evidence
- bounded live app-only validation per executor domain

## Proof Sketch

If the supported v1 action surface is partitioned into bounded SharePoint,
collaboration, and directory domains, then each domain can be given its own
service principal and certificate-backed credential. If the tenant contract
projects those executors deterministically, and the runtime explicitly projects
the correct executor before Graph client construction, then live app-only
validation can test each domain in isolation. If each domain returns `200` on a
representative live route with only its bounded role set, and the legacy
monolithic executor is no longer the active default, then the executor cleanup
is sufficient for `B7D`.

## Runtime Bindings

- `src/provisioning_api/routers/m365.py`
- `src/provisioning_api/m365_provision.py`
- `tests/test_env_loading.py`
- `artifacts/b7d_executor_permission_matrix.json`
- `artifacts/b7d_live_executor_validation.json`

## Failure Boundary

`B7D` fails closed if:

- any supported v1 action still depends on the legacy monolithic executor;
- any bounded executor lacks its required Graph app-role assignment;
- the tenant contract still defaults to the legacy executor;
- runtime projection does not select the bounded executor deterministically; or
- any representative live app-only probe fails for SharePoint, collaboration,
  or directory.
