# Lemma L89: M365 Persona-Action Dead-Route Remediation v1

## Statement

For the active persona-action full-support remediation initiative, the certified dead-route surface can only be reduced truthfully if each repaired alias satisfies all of the following:

1. the persona-facing alias resolves to one canonical runtime action path
2. the runtime dispatcher recognizes that action path for every intended owning persona class
3. permission-tier and OPA policy checks evaluate against the same canonical action identity
4. focused regression tests prove the repaired route no longer collapses into `dead-routed`

If any repaired alias fails one of these obligations, the support claim remains false and the alias must stay non-green.

## Inputs

- Certified predecessor backlog from `artifacts/diagnostics/m365_persona_action_certification.json`
- Blocked `P1` write set:
  - `src/ops_adapter/actions.py`
  - `src/smarthaus_common/permission_enforcer.py`
  - `policies/ops.rego`
  - `tests/test_ops_adapter.py`
  - `tests/test_policies.py`
  - `tests/test_executor_routing_v2.py`

## Formula

Let:

- `A_dead` be the certified set of dead-routed aliases
- `R(alias)` be the canonical runtime route for alias `alias`
- `D(alias)` be the dispatcher ownership truth for alias `alias`
- `P(alias)` be the permission-tier truth for alias `alias`
- `O(alias)` be the OPA allow/approval truth for alias `alias`
- `T(alias)` be the focused regression result for alias `alias`

Then a repaired alias is truthful iff:

`RepairTruth(alias) = RouteUnique(alias) AND DispatchAligned(alias) AND PermissionAligned(alias) AND PolicyAligned(alias) AND TestGreen(alias)`

where:

- `RouteUnique(alias) := R(alias) is defined exactly once`
- `DispatchAligned(alias) := D(alias) preserves persona ownership for R(alias)`
- `PermissionAligned(alias) := P(alias)` recognizes the same canonical action identity as `R(alias)`
- `PolicyAligned(alias) := O(alias)` evaluates the same canonical action identity as `R(alias)`
- `TestGreen(alias) := T(alias) = pass`

The phase-level repair condition is:

`DeadRouteRepairGO = forall alias in A_repair, RepairTruth(alias)`

## Boundary Conditions

- This lemma does not claim that every certified dead-routed alias can be repaired in `P1`.
- This lemma does not authorize widening the persona claim surface beyond aliases explicitly repaired and tested.
- This lemma does not convert permission-blocked or policy-fenced aliases into green unless those boundaries are repaired truthfully.

## Determinism

- The blocker baseline is frozen at `116` dead-routed active pairs and `21` dead-routed unique aliases.
- The admissible `P1` write set is frozen by `P1S`.
- The future `P1` repair must classify aliases against one canonical route identity only.

## Proof Sketch

The certified workforce artifact already proves the dead-route backlog exists and is bounded. The `P1S` governance notebook proves the repair phase may only begin once notebook-backed evidence exists. Therefore the first truthful repair wave must define a deterministic route identity, keep dispatcher/permission/policy layers aligned to that identity, and verify the repaired aliases with focused regression tests. Any alias lacking one of those properties remains non-green, which preserves fail-closed support claims.
