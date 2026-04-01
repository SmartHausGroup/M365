# SMARTHAUS M365 Activated Persona Surface v1

## Purpose

Define the truthful commercial boundary for the currently activated persona
surface on `feature/m365_personas`.

## Authority

- **Contract:** `registry/activated_persona_surface_v1.yaml`
- **Persona source:** `registry/persona_registry_v2.yaml`
- **Capability map:** `registry/persona_capability_map.yaml`
- **Wave evidence:** `artifacts/scorecards/scorecard_l73.json`, `artifacts/scorecards/scorecard_l74.json`, `artifacts/scorecards/scorecard_l75.json`

## Problem

The historical workforce packaging baseline from E9A reflects the pre-activation
state with 4 active personas and 35 planned personas. On this review branch,
P2B through P2D have materially changed the live activation boundary, so the
commercialization surface must be re-stated truthfully before current claims can
be treated as certified.

## Decision

Treat `registry/activated_persona_surface_v1.yaml` as the branch-specific
authority for the current M365-backed activated surface. It certifies the
aggregated output of P2B, P2C, and the M365-backed portion of P2D while
explicitly excluding the deferred external-platform personas.

## Certified Active Surface

- **34 registry-backed personas**
- **5 deferred external-platform personas**
- **298 total allowed persona-actions**
- **10 departments with at least one active persona**

### Department Breakdown

- Operations: 2
- HR: 1
- Communication: 1
- Engineering: 7
- Marketing: 2
- Product: 3
- Project Management: 3
- Studio Operations: 5
- Testing: 5
- Design: 5

## Deferred External Personas

These 5 personas remain non-active and are deferred into `P3`:

- `instagram-curator`
- `tiktok-strategist`
- `reddit-community-builder`
- `twitter-engager`
- `app-store-optimizer`

They require external-platform APIs and credential-gated runtime surfaces that
do not yet exist in this repo. They must not be marketed as active.

## Supported Claims

- The current review branch has **34 registry-backed personas** across all 10 departments.
- The currently activated persona surface is **M365-backed only**.
- The current activated surface is certified by P2B, P2C, and the M365-backed scope of P2D.
- The 5 deferred external-platform personas are part of later `P3`, not the current active claim set.

## Not Supported

- Claiming **39/39 active personas**
- Claiming the deferred external-platform personas are live
- Claiming external-platform adapters or credentials are implemented
- Claiming this activated surface is already merged into `development`, `staging`, or `main`

## Historical Baseline

`registry/workforce_packaging_v1.yaml` remains the historical E9A packaging
baseline. On `feature/m365_personas`, the truthful current activated-surface
boundary is this document and its companion contract.

## Next Dependency

`P3A` (External Platform Contract and Credentialless Preparation) is the next
act once the current M365-backed activation track is certified closed.
