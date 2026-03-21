# Lemma L37 — M365 Cross-Workload Automation Recipes v2

## Statement

`E3E` is complete only when the bounded cross-workload recipe authority, runtime discovery surface, capability registry, executor routing, auth model, approval matrix, and verification artifacts all agree on the same implemented recipe-catalog action family.

## Scope

The lemma covers:

- Recipe catalog discovery
- Recipe detail retrieval
- Cross-workload recipe definitions whose steps reference only implemented actions

## Proof Sketch

1. The recipe authority fixes the exact catalog actions, recipe IDs, workload spans, and step-action references.
2. The runtime exposes only bounded discovery/read actions against the repository-backed catalog.
3. The capability registry, executor routing, auth model, and approval matrix all record the same action family as implemented and low-risk.
4. The verifier and tests prove every recipe spans multiple workloads and every referenced step action is already implemented.

## Failure Boundary

If any catalog action is missing from the router, missing from the implemented registry set, routed or authorized incorrectly, or if any recipe is not cross-workload or references a non-implemented step action, `L37` fails closed.
