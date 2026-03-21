# M365 Cross-Workload Automation Recipes v2

## Purpose

`E3E` defines the first bounded catalog of reusable multi-step automation recipes that span more than one M365 workload family.

## Implemented surface

- `list_automation_recipes`
- `get_automation_recipe`

These actions expose a deterministic recipe catalog to Claude/UCP without claiming that the pack already has a general-purpose orchestration engine.

## Boundaries

- Recipes are discovery/read surfaces in `E3E`, not a full execution scheduler.
- Every recipe must reference only already-implemented actions.
- Every recipe must span at least `2` workload families.

## Recipe families

- Employee onboarding workspace
- Incident response war room
- Knowledge connector launch
- Analytics operating review
- Service workspace bootstrap

## Deterministic guarantees

- The catalog is repository-backed and deterministic on fixed repo state.
- Each recipe has a stable `recipeId`, workload list, persona ownership, risk class, approval profile, and ordered step list.
- Verification fails closed if any referenced step action is not implemented in the capability registry or if any recipe stops being cross-workload.
