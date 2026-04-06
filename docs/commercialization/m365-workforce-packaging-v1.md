# SMARTHAUS M365 Workforce Packaging v1

## Purpose

Package the final workforce offering into a deterministic product definition
with explicit capability tiers, persona classes, department coverage, and
bounded claims.

## Authority

- **Contract:** `registry/workforce_packaging_v1.yaml`
- **Activated surface:** `registry/activated_persona_surface_v1.yaml`
- **Persona source:** `registry/persona_registry_v2.yaml`

## Final H5 Boundary

After H5 closeout, this document is no longer a historical baseline. It now
tracks the final governed activated commercial surface and must agree with:

- `registry/activated_persona_surface_v1.yaml`
- `docs/commercialization/m365-activated-persona-surface-v1.md`

## Packaging Layers

1. **Capability Tier Definition** — define tiers from the final certified workload surface.
2. **Persona Class Packaging** — package personas into active and deferred-external classes.
3. **Department Coverage Matrix** — map departments to active and deferred personas.
4. **Product Boundary Lock** — lock claims to activated-surface evidence.

## Product Tiers

- **Core:** 54 active personas, 430 routed actions, 13 certified domains, all 10 departments with active personas.
- **Expansion:** 5 deferred external-platform marketing personas, 0 actions, non-live pending later platform-specific runtime work.

## No-Go Conditions

- Packaging claim exceeding activated-surface evidence.
- Deferred external persona presented as action-capable.
- Department coverage drifting away from the authoritative registry.

## Status

H5 closes this packaging boundary. No later phase in this initiative should
re-open these counts without a new governed change.
