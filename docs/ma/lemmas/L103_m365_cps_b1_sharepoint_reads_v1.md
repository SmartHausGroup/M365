# L103 - M365 Capability Pack B1 SharePoint Reads v1

**Lemma id:** `L103_m365_cps_b1_sharepoint_reads_v1`
**Plan reference:** `plan:m365-cps-trkB-p1-sharepoint-reads:T2`
**Status:** Active
**Owner:** SMARTHAUS
**Module notebook:** `notebooks/m365/INV-M365-CPS-B1-sharepoint-reads-v1.ipynb`
**Invariant YAML:** `invariants/lemmas/L103_m365_cps_b1_sharepoint_reads_v1.yaml`
**Scorecard:** `artifacts/scorecards/scorecard_l103.json`
**Predecessor:** `L102_m365_cps_preflight_intersection_v1`

## Mission

Add SharePoint read coverage to the M365 runtime: 5 new ActionSpec entries
and 6 new legacy aliases. Also add path-parameter substitution to
`invoke()` so endpoints with `{siteId}` etc. resolve at call time.
Closes the SharePoint slice of `plan:m365-capability-pack-surface-remediation:R4`.

## Bundled predicate

```
SharePointReadsCovered =
    L_PATH_SUBST_CORRECT
  ∧ L_NEW_ENTRIES_REGISTERED
  ∧ L_ALIASES_RESOLVE
  ∧ L_NO_REGRESSION
```

## Lemmas

### L_PATH_SUBST_CORRECT

`invoke()` substitutes `{name}` placeholders in `spec.endpoint` from
`params[name]` before calling Graph. Unfilled placeholders return a
deterministic `internal_error` status with reason
`endpoint_param_missing` (mirroring the existing `?search=` handling).

### L_NEW_ENTRIES_REGISTERED

`READ_ONLY_REGISTRY` contains the five SharePoint read action_ids:
`graph.sites.get`, `graph.lists.list`, `graph.lists.get`,
`graph.lists.items`, `graph.drives.children`. Every entry is `risk=low`,
`rw=read`, scopes include `Sites.Read.All` (or `Files.Read.All` for
`graph.drives.children`).

### L_ALIASES_RESOLVE

`LEGACY_ACTION_TO_RUNTIME_ACTION` maps:
- `sites.list` → `graph.sites.search` (existing runtime action)
- `sites.get` → `graph.sites.get`
- `lists.list` → `graph.lists.list`
- `lists.get` → `graph.lists.get`
- `lists.items` → `graph.lists.items`
- `files.list` → `graph.drives.children`

### L_NO_REGRESSION

Every Track A surface (status semantics, inventory, preflight) still
passes its existing tests. Pre-B1 registry actions still resolve.
