# L75 — M365 Specialist and Regulated Persona Activation v1

## Lemma

The P2D specialist and regulated personas may be claimed as registry-backed, action-surfaced, domain-bound, approval-wired workers only when all six conditions from the P2A activation definition are satisfied for each persona against the authoritative persona registry, agents.yaml, capability map, and department pack authorities. Personas that require non-M365 external-platform APIs must remain contract-only with documented residual scope.

## Plan Reference

`plan:m365-post-expansion-promotion-and-persona-activation:P2D`

## Assumptions

- `registry/persona_registry_v2.yaml` is the authoritative persona roster.
- `registry/agents.yaml` is the authoritative action registry.
- `registry/persona_capability_map.yaml` is the authoritative capability map.
- `registry/department_pack_*_v1.yaml` are the authoritative department pack files.
- `registry/executor_routing_v2.yaml` is the authoritative routing table.
- The P2A activation definition (6-point test) is the gate for each persona.
- P2B (6 personas) and P2C (8 personas) are already activated (18 registry-backed).

## Activated Personas (16)

| Persona | Department | Actions | Risk | Approval Profile |
|---------|-----------|---------|------|-----------------|
| ai-engineer | engineering | 10 | medium | medium-operational |
| frontend-developer | engineering | 7 | low | low-observe-create |
| mobile-app-builder | engineering | 7 | low | low-observe-create |
| rapid-prototyper | engineering | 8 | low | low-observe-create |
| test-writer-fixer | engineering | 7 | low | low-observe-create |
| performance-benchmarker | testing | 8 | low | low-observe-create |
| test-results-analyzer | testing | 7 | low | low-observe-create |
| tool-evaluator | testing | 7 | low | low-observe-create |
| workflow-optimizer | testing | 8 | low | medium-operational |
| finance-tracker | studio-operations | 8 | high | high-impact |
| infrastructure-maintainer | studio-operations | 8 | medium | medium-operational |
| legal-compliance-checker | studio-operations | 8 | high | critical-regulated |
| visual-storyteller | design | 7 | low | low-observe-create |
| whimsy-injector | design | 7 | low | low-observe-create |
| experiment-tracker | project-management | 8 | low | low-observe-create |
| trend-researcher | product | 7 | low | low-observe-create |

**Total new actions across 16 personas: 122**

## Blocked Personas (5) — Documented Residual Scope

| Persona | Department | Reason |
|---------|-----------|--------|
| instagram-curator | marketing | Requires Instagram/Meta API (not available in this repo) |
| tiktok-strategist | marketing | Requires TikTok API (not available in this repo) |
| reddit-community-builder | marketing | Requires Reddit API (not available in this repo) |
| twitter-engager | marketing | Requires Twitter/X API (not available in this repo) |
| app-store-optimizer | marketing | Requires App Store Connect / Google Play API (not available in this repo) |

These 5 personas remain `persona-contract-only` with `allowed_actions: []`. They can be activated in a future wave if and when the corresponding external-platform APIs are integrated into this repo.

## Notebook Evidence

- Primary: `notebooks/m365/INV-M365-BW-specialist-regulated-activation-v1.ipynb`
- Proof: `notebooks/lemma_proofs/L75_m365_specialist_regulated_activation_v1.ipynb`

## Boundary Conditions

- If any activated persona's `allowed_actions` in `agents.yaml` is empty -> fail closed.
- If any activated persona's `coverage_status` is not `registry-backed` -> fail closed.
- If any declared action lacks a routing entry in `executor_routing_v2.yaml` -> fail closed.
- The 5 blocked personas must remain `persona-contract-only` with `allowed_actions: []`.
- High-risk personas (finance-tracker, legal-compliance-checker) must have explicit approval rules.
