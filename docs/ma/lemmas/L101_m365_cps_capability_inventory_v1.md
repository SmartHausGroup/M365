# L101 - M365 Capability Pack Surface Inventory v1

**Lemma id:** `L101_m365_cps_capability_inventory_v1`
**Plan reference:** `plan:m365-cps-trkA-p2-inventory-tool:T2`
**Status:** Active
**Owner:** SMARTHAUS
**Module notebook:** `notebooks/m365/INV-M365-CPS-A2-inventory-tool-v1.ipynb`
**Invariant YAML:** `invariants/lemmas/L101_m365_cps_capability_inventory_v1.yaml`
**Scorecard:** `artifacts/scorecards/scorecard_l101.json`
**Generated verification:** `configs/generated/m365_cps_capability_inventory_v1_verification.json`
**Predecessor:** `L100_m365_cps_status_code_semantics_v1`

## Mission

Add a `/v1/inventory` endpoint to the M365 runtime that returns the runtime's actual capability surface so operators can see (a) what actions are implemented, (b) what legacy aliases map to what runtime actions, and (c) what actions agents.yaml advertises but the runtime does not implement.

This closes `plan:m365-capability-pack-surface-remediation:R2`. Without this endpoint, operators must call actions blind to discover the coverage gap; with it, one call returns the complete picture.

## Bundled predicate

```
InventoryContractValid =
    L_IMPL_LIST_FROM_REGISTRY
  ∧ L_ALIAS_MAP_FROM_CLIENT
  ∧ L_ADVERTISED_ONLY_DIFF
  ∧ L_RESPONSE_SHAPE_STABLE
  ∧ L_NO_MUTATION
```

Any single false clause means `NO_GO`.

## Lemmas

### L_IMPL_LIST_FROM_REGISTRY

`/v1/inventory` must derive `implemented_actions` from `READ_ONLY_REGISTRY` only. Each entry includes `action_id`, `workload`, `endpoint`, `scopes`, `auth_modes`, `risk`, `rw`. Length equals `len(READ_ONLY_REGISTRY)`.

**Failure boundary:** the endpoint returns a hand-coded list that does not track the registry, or includes actions not in the registry, or omits actions that are.

### L_ALIAS_MAP_FROM_CLIENT

`alias_map` is loaded from `ucp_m365_pack.client.LEGACY_ACTION_TO_RUNTIME_ACTION` exactly. Pre-Track-B size is 22; the map will grow during Track B.

**Failure boundary:** the endpoint reproduces the alias map manually instead of reading the source of truth.

### L_ADVERTISED_ONLY_DIFF

`advertised_only` is the set difference: `agents.yaml allowed_actions` minus `LEGACY_ACTION_TO_RUNTIME_ACTION.keys()` minus `READ_ONLY_REGISTRY.keys()`. This is exactly the set of actions agents claim but the runtime cannot serve.

**Failure boundary:** the diff is computed wrong, e.g. missing the alias-key subtraction (would over-count gaps) or missing the registry-key subtraction (would over-count gaps for actions present under their non-graph-prefixed name like `sites.list`).

### L_RESPONSE_SHAPE_STABLE

The JSON response shape is stable: top-level keys `implemented_actions`, `alias_map`, `advertised_only`, `agent_summary`, `runtime_version`. Adding new top-level keys is allowed; removing or renaming is a breaking change requiring a new notebook authority.

**Failure boundary:** any of the five required keys is missing or renamed.

### L_NO_MUTATION

The endpoint is GET only, has no body, performs no Graph calls, takes no tenant context, and is safe to call from any auth state including unauthenticated.

**Failure boundary:** the endpoint accepts a body, makes a Graph call, requires auth, or has any side effect on runtime state.

## Test bindings

- `tests/test_m365_runtime_inventory_endpoint.py` (T3)
- UCP-side `tests/test_m365_integration.py::TestInventoryTool` (T5)

## Determinism

```
seed_locked: true
seed: 0
mode: deterministic-static
```

The notebook performs no random sampling. Source-of-truth reads (REGISTRY, alias map, agents.yaml) are deterministic given a fixed working tree.
