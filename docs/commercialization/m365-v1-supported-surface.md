# M365 v1 Supported Surface

**Status:** `P0A` complete
**Date:** 2026-03-17
**Plan refs:** `plan:m365-enterprise-commercialization-readiness:R1`, `plan:m365-enterprise-commercialization-readiness:P0A`

This document is the commercialization authority for the standalone SmartHaus M365 module v1. If broader repository language conflicts with this boundary, this document wins for product claims, support scope, pilot commitments, and enterprise review.

Deterministic support definition for this repository state:

`Supported_v1 = {a | a.status = implemented in registry/capability_registry.yaml} ∩ {a | a is accepted by src/provisioning_api/routers/m365.py} ∩ {a | a is listed as supported in docs/CAIO_M365_CONTRACT.md}`

For the current repository state, that set contains exactly 9 actions. The broader M365 universe remains `260` total actions with `9` implemented and `251` planned.

## Supported Actions

Only the actions below are commercially supported in standalone M365 v1.

| Action | Domain | Mutating | Required permissions | Runtime surface |
| --- | --- | --- | --- | --- |
| `list_users` | `identity` | No | `User.Read.All` | instruction API and module |
| `get_user` | `identity` | No | `User.Read.All` | instruction API and module |
| `reset_user_password` | `identity` | Yes | `User.ReadWrite.All` | instruction API and module |
| `list_teams` | `teams` | No | `Team.ReadBasic.All` | instruction API and module |
| `list_sites` | `sharepoint` | No | `Sites.Read.All` | instruction API and module |
| `create_site` | `sharepoint` | Yes | `Sites.ReadWrite.All`, `Group.ReadWrite.All` | instruction API and module |
| `create_team` | `teams` | Yes | `Team.Create`, `Group.ReadWrite.All` | instruction API and module |
| `add_channel` | `teams` | Yes | `Channel.Create.Group` | instruction API and module |
| `provision_service` | `sharepoint` | Yes | `Sites.ReadWrite.All`, `Group.ReadWrite.All`, `Team.Create` | instruction API and module |

Commercial support for mutating actions assumes the existing runtime gates remain in force, including auth, idempotency, audit logging, and `ALLOW_M365_MUTATIONS`.

## Unsupported Actions

The following are explicitly out of scope for standalone M365 v1 commercialization:

1. Every action in `registry/capability_registry.yaml` with `status: planned`. This is the remaining `251` actions in the 260-action universe.
2. Contract or notebook-only actions that are not implemented in the instruction router:
   - `list_groups`
   - `get_group`
   - `create_group`
   - `list_group_members`
   - `add_group_member`
3. Broader capability statements elsewhere in the repo that imply more than the 9-action surface above. Those statements are roadmap or higher-level vision, not commercialization authority for standalone M365 v1.
4. Any claim of full M365 administration coverage, full identity lifecycle coverage, or general-purpose Graph coverage.

Adding a new commercially supported action requires all of the following:

1. The action is implemented in `src/provisioning_api/routers/m365.py` or the shared execution path used by the module.
2. The action is marked `implemented` in `registry/capability_registry.yaml`.
3. The contract is updated in `docs/CAIO_M365_CONTRACT.md` and `docs/contracts/caio-m365/ACTION_SPECIFICATION.md`.
4. Validation evidence is updated for the new action.
5. This commercialization boundary document is updated and re-approved.

## Evidence Sources

The table below is the required evidence-source map for each supported action.

| Action | Registry evidence | Contract evidence | Runtime evidence | Additional evidence |
| --- | --- | --- | --- | --- |
| `list_users` | `registry/capability_registry.yaml` | `docs/CAIO_M365_CONTRACT.md`, `docs/contracts/caio-m365/ACTION_SPECIFICATION.md` | `src/provisioning_api/routers/m365.py` | `docs/M365_MA_INDEX.md` |
| `get_user` | `registry/capability_registry.yaml` | `docs/CAIO_M365_CONTRACT.md`, `docs/contracts/caio-m365/ACTION_SPECIFICATION.md` | `src/provisioning_api/routers/m365.py` | `docs/M365_MA_INDEX.md` |
| `reset_user_password` | `registry/capability_registry.yaml` | `docs/CAIO_M365_CONTRACT.md`, `docs/contracts/caio-m365/ACTION_SPECIFICATION.md` | `src/provisioning_api/routers/m365.py` | `docs/M365_MA_INDEX.md` |
| `list_teams` | `registry/capability_registry.yaml` | `docs/CAIO_M365_CONTRACT.md`, `docs/contracts/caio-m365/ACTION_SPECIFICATION.md` | `src/provisioning_api/routers/m365.py` | `docs/M365_MA_INDEX.md` |
| `list_sites` | `registry/capability_registry.yaml` | `docs/CAIO_M365_CONTRACT.md`, `docs/contracts/caio-m365/ACTION_SPECIFICATION.md` | `src/provisioning_api/routers/m365.py` | `docs/M365_MA_INDEX.md` |
| `create_site` | `registry/capability_registry.yaml` | `docs/CAIO_M365_CONTRACT.md`, `docs/contracts/caio-m365/ACTION_SPECIFICATION.md` | `src/provisioning_api/routers/m365.py` | `tests/test_endpoints.py`, `tests/test_m365_module_entrypoint.py` |
| `create_team` | `registry/capability_registry.yaml` | `docs/CAIO_M365_CONTRACT.md`, `docs/contracts/caio-m365/ACTION_SPECIFICATION.md` | `src/provisioning_api/routers/m365.py` | `tests/test_m365_module_entrypoint.py` |
| `add_channel` | `registry/capability_registry.yaml` | `docs/CAIO_M365_CONTRACT.md`, `docs/contracts/caio-m365/ACTION_SPECIFICATION.md` | `src/provisioning_api/routers/m365.py` | `docs/M365_MA_INDEX.md` |
| `provision_service` | `registry/capability_registry.yaml` | `docs/CAIO_M365_CONTRACT.md`, `docs/contracts/caio-m365/ACTION_SPECIFICATION.md` | `src/provisioning_api/routers/m365.py` | `docs/M365_MA_INDEX.md` |

Source hierarchy for this boundary:

1. `registry/capability_registry.yaml` defines implementation status.
2. `src/provisioning_api/routers/m365.py` defines the actual accepted instruction surface.
3. `docs/CAIO_M365_CONTRACT.md` and `docs/contracts/caio-m365/ACTION_SPECIFICATION.md` define the published and formal contract.
4. `docs/M365_MA_INDEX.md` defines the current repo-wide implemented-versus-planned count and prevents commercialization drift to the full universe.

## Product Claim Boundary

SmartHaus may claim the following for standalone M365 v1 and no more:

1. The module exposes a deterministic, policy-gated M365 instruction surface of exactly 9 supported actions across identity, Teams, and SharePoint.
2. The commercial surface is narrow by design and is bounded to the actions listed in this document.
3. Mutating actions are gated by explicit runtime controls and are not unconditional administrative powers.
4. The 260-action universe is roadmap and contract-universe context, not launch-scope support.

SmartHaus may not claim the following for standalone M365 v1:

1. Support for all actions in the M365 capability universe.
2. Support for notebook-only or contract-only actions that are not runtime-implemented.
3. Broad enterprise M365 administration beyond the 9 actions listed above.
4. Production readiness of future phases such as canonical config, governance hardening, live-tenant certification, or operator packaging until those phases are completed.
