# SMARTHAUS M365 Activated Persona Surface v1

## Purpose

Define the truthful commercial boundary for the final governed activated persona
surface on `codex/m365-authoritative-persona-humanization-expansion-plan`.

## Authority

- **Contract:** `registry/activated_persona_surface_v1.yaml`
- **Persona source:** `registry/persona_registry_v2.yaml`
- **Capability map:** `registry/persona_capability_map.yaml`
- **H5 proof:** `artifacts/scorecards/scorecard_l81.json`
- **H5 verification:** `configs/generated/authoritative_persona_activation_gate_closeout_v1_verification.json`

## Problem

H3 and H4 deliberately froze the authoritative workforce at the staged
pre-activation boundary of `34` active personas and `25` planned personas.
H5 exists to close that final activation gate only after every governed
promoted persona is fully named, manager-bound, escalation-bound, and
capability-mapped.

## Decision

Treat `registry/activated_persona_surface_v1.yaml` as the authority for the
final H5 activated persona surface. It certifies the all-or-nothing promotion
of the governed `20` staged personas while explicitly excluding the `5`
external-platform marketing personas that remain deferred.

## Certified Active Surface

- **54 registry-backed personas**
- **5 deferred external-platform personas**
- **430 total allowed persona-actions**
- **10 departments with at least one active persona**

### Department Breakdown

- Operations: 10
- HR: 2
- Communication: 4
- Engineering: 8
- Marketing: 3
- Product: 3
- Project Management: 5
- Studio Operations: 9
- Testing: 5
- Design: 5

## Deferred External Personas

These `5` personas remain non-active after H5:

- `app-store-optimizer`
- `instagram-curator`
- `reddit-community-builder`
- `tiktok-strategist`
- `twitter-engager`

They are all marketing roles that still require external-platform adapters,
credentials, and later platform-specific runtime work. They must not be
marketed as active.

## Supported Claims

- The current branch has **54 registry-backed personas** across all 10 departments.
- The currently activated persona surface is **M365-backed only**.
- The final activated surface is certified by the H5 closeout proof `L81`.
- The `5` deferred external-platform marketing personas are governed but not active.

## Not Supported

- Claiming **59/59 active personas**
- Claiming the deferred external-platform personas are live
- Claiming external-platform adapters or credentials are implemented
- Claiming this activated surface is already merged into `development`, `staging`, or `main`

## Packaging Alignment

`registry/workforce_packaging_v1.yaml` now mirrors this same final H5 boundary.
The active-surface contract and the packaging contract must remain in lockstep.
