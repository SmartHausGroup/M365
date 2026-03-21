# M365 Compliance / Retention / eDiscovery Expansion v2

## Purpose

`E4C` opens the compliance workload family with a bounded Microsoft 365 Purview / eDiscovery slice that is honest about what the pack can administer today.

## Implemented Surface

- `list_ediscovery_cases`
- `get_ediscovery_case`
- `create_ediscovery_case`
- `list_ediscovery_case_searches`
- `get_ediscovery_case_search`
- `create_ediscovery_case_search`
- `list_ediscovery_case_custodians`
- `list_ediscovery_case_legal_holds`

## Boundary

This slice covers case discovery, bounded case/search creation, custodian inventory, and legal-hold visibility. It does not claim full Purview retention-label lifecycle, DLP policy administration, content export, or advanced eDiscovery review-set automation.

## Deterministic Guarantees

1. Every implemented action is routed to the bounded `compliance` executor domain.
2. Every implemented action resolves to `app_only` auth in the v2 auth model.
3. Read actions remain low-observe and non-approval-bearing.
4. `create_ediscovery_case` and `create_ediscovery_case_search` are approval-bearing and fail-closed under the critical-regulated profile.
5. Runtime, contracts, registries, and verifiers all agree on the same eight-action surface.
