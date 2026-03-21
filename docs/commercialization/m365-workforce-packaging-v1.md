# SMARTHAUS M365 Workforce Packaging v1

## Purpose

Package the full workforce offering into a deterministic product definition with explicit capability tiers, persona classes, department coverage, and bounded claims.

## Authority

- **Contract:** `registry/workforce_packaging_v1.yaml`
- **Release gate:** `registry/enterprise_release_gate_v2.yaml`

## Packaging Layers

1. **Capability Tier Definition** — define tiers from certified workload surface.
2. **Persona Class Packaging** — package personas into active and planned classes.
3. **Department Coverage Matrix** — map departments to active/planned personas.
4. **Product Boundary Lock** — lock claims to release gate evidence.

## Product Tiers

- **Core:** 4 active personas, 155 actions, 13 domains, 3 departments with active personas.
- **Expansion:** 35 planned personas, all 10 departments, roadmap to full action backing.

## No-Go Conditions

- Packaging claim exceeding release gate evidence.
- Contract-only persona presented as action-capable.
- Department claiming active coverage without registry-backed personas.

## Next Dependency

`E9B` (Customer Onboarding v2) is the next act.
