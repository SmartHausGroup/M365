# Master Plan: TAI Licensed Modular Runtime (Embedded Modules + Entitlements)

**Plan ID:** `tai-licensed-modular-runtime`
**Type:** Overarching high-level cross-repo plan
**Status:** Draft (Pending Approval)
**Date:** 2026-02-06
**Owner:** SmartHaus
**North Star alignment:**
- M365: `Operations/NORTHSTAR.md`
- TAI Core: `docs/NORTH_STAR_V3.md`
- CAIO Core: `docs/NORTH_STAR.md`
- MAIA: `docs/NORTH_STAR.md`
- VFE Core: `docs/NORTH_STAR.md`

---

## Objective

Move from a "multiple separately managed services" deployment model to a **single TAI product runtime** where CAIO, MAIA, VFE, and M365 capabilities are delivered as **licensed modules** that can be installed/imported, enabled, disabled, and updated from TAI.

Target user experience:

1. Install TAI once.
2. Add license key.
3. Enable module toggles (or import module package).
4. Use capability immediately (no manual multi-service wiring in default mode).

---

## Current State

- Voice→M365 integration exists across repos using API contracts and orchestration.
- Deployments can still feel like separate service management to operators.
- Licensing exists in parts of the stack but is not yet unified as a module-entitlement UX in TAI.

---

## Target State

- **TAI Core** is the runtime host and module control plane.
- **Modules** are separately versioned artifacts (CAIO, MAIA, VFE, M365 connector) loaded by TAI.
- **Entitlements** from license keys unlock module IDs/capabilities.
- **Default runtime mode** is embedded/in-process module execution.
- **Optional compatibility mode** supports external service execution when explicitly configured.

---

## Architecture (High Level)

### Core Components

- **TAI Module Host**: module lifecycle manager (install, verify, enable, disable, unload).
- **Entitlement Engine**: maps license claims to module/capability access.
- **Capability Registry**: maps capability IDs to active module providers.
- **Audit + Health**: unified status, audit trail, and failure visibility per module.

### Module Package Contract (v1)

Each module package includes a manifest with:

- `module_id`, `version`, `entrypoint`
- `capabilities[]`
- `entitlements[]` (required license claims)
- `permissions[]` (network, filesystem, Graph scopes, etc.)
- `compatibility` (`min_tai_version`, dependency constraints)
- `signature`/verification metadata

### Canonical Capability Shapes (frozen terms)

- `intent.classify` -> output `{ intent: { domain, action, params } }`
- `orchestrate.execute` -> structured orchestration response (`ok/result/error/trace_id`)
- `inference.generate_draft` -> structured generation response (`ok/result/error/trace_id`)
- `m365.instruction.execute` -> structured instruction response (`ok/result/error/trace_id`)

---

## Repositories and Responsibilities

| Repo | Responsibility | Detailed plan path |
|------|----------------|--------------------|
| **TAI Core** | Implement module host, manifest validation, entitlement checks, capability routing, module control UI/UX. | `plans/tai-licensed-modular-runtime/tai-core-repo-plan.md` (tai-core repo) |
| **CAIO Core** | Provide embeddable orchestration module entrypoints and capability provider implementation for TAI host runtime. | `plans/tai-licensed-modular-runtime/caio-core-repo-plan.md` (caio-core repo) |
| **MAIA** | Provide embeddable intent module entrypoints and preserve CAIO-compatible intent output shape. | `plans/tai-licensed-modular-runtime/maia-repo-plan.md` (MAIA repo) |
| **VFE Core** | Provide embeddable inference module entrypoints for draft/content generation, keeping VFE inference-only. | `plans/tai-licensed-modular-runtime/vfe-core-repo-plan.md` (vfe-core repo) |
| **M365** | Provide embeddable M365 connector module behavior, auth/gates/audit, and action mapping contract used by CAIO/TAI runtime. | `plans/tai-licensed-modular-runtime/m365-repo-plan.md` (M365 repo) |

---

## Deterministic Execution Order

1. **TAI Core**: establish module host, manifest/entitlement contract, and lifecycle APIs first.
2. **CAIO Core**: deliver embeddable orchestrator module against TAI host contract.
3. **MAIA**: deliver embeddable intent module against TAI host + CAIO intent contract.
4. **VFE Core**: deliver embeddable inference module against TAI host + CAIO draft contract.
5. **M365**: deliver embeddable connector module and finalize TAI-hosted M365 execution path.

No repo reordering for implementation unless explicitly approved.

---

## MA Process Applicability

This initiative is primarily packaging, module lifecycle, contract wiring, and licensing/entitlement work.

- **MA process not required** for pure wiring/packaging/configuration.
- **MA process required** before implementation if work introduces or modifies mathematical/algorithmic behavior, including:
  - MAIA intent scoring/attention/RL changes
  - VFE selection calculus changes
  - New mathematical guarantees/invariants in any repo

When triggered, follow each repo's MA rules (Phases 1-5, notebook-first, CI enforcement).

---

## Success Criteria (Overarching)

- One-product user workflow is available: install TAI, apply license, enable module, use feature.
- TAI can install/import module artifacts and enforce entitlement gates before activation.
- CAIO, MAIA, VFE, and M365 capabilities are callable through TAI module runtime without mandatory external service ops in default mode.
- Health, audit, and rollback paths exist for module enable/disable/update.
- Optional external-service compatibility mode remains available without being the default operator path.

---

## Detailed Plan Index

| Repo | Plan reference |
|------|----------------|
| TAI Core | `plan:tai-licensed-modular-runtime:tai-core` |
| CAIO Core | `plan:tai-licensed-modular-runtime:caio-core` |
| MAIA | `plan:tai-licensed-modular-runtime:maia` |
| VFE Core | `plan:tai-licensed-modular-runtime:vfe-core` |
| M365 | `plan:tai-licensed-modular-runtime:m365` |

---

## Governance

- Plan-first execution is mandatory in each repo.
- No implementation without explicit approval (`go`) against repo-specific plans.
- Post-work requirements apply per repo: action log updates and execution plan/status updates.
