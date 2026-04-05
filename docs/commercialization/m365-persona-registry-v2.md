# M365 Persona Registry v2

## Purpose

Define the authoritative digital-employee registry for the SMARTHAUS workforce runtime.

## Problem

The earlier authoritative registry froze the workforce at `39` personas even though `20` additional runtime agents had already been promoted through the governed humanization path. H3 rebases the authoritative roster to `59` named personas without activating the promoted set before H5.

## Decision

`registry/persona_registry_v2.yaml` remains the authoritative runtime registry for digital employees.

It is built deterministically from:

- `registry/ai_team.json`
- `registry/persona_capability_map.yaml`
- `registry/agents.yaml`

## Current Authoritative Summary

- Total personas: `59`
- Total departments: `10`
- Active personas: `34`
- Planned personas: `25`
- Registry-backed personas: `34`
- Persona-contract-only personas: `25`

## Required Persona Fields

- `persona_id`
- `canonical_agent`
- `display_name`
- `slug`
- `department`
- `title`
- `manager`
- `escalation_owner`
- `responsibilities`
- `allowed_actions`
- `allowed_domains`
- `approval_owner`
- `approval_profile`
- `risk_tier`
- `coverage_status`
- `status`
- `external_presence_policy`
- `aliases`
- `action_count`

## Status Semantics

- `active`
  - authoritative persona with implemented runtime actions
- `planned`
  - authoritative persona with locked contract fields but still fail-closed for action execution
- `inactive`
  - authoritative persona that is intentionally unavailable

## Runtime Rule

Only personas present in `registry/persona_registry_v2.yaml` may be treated as valid digital employees by the governed runtime.

That means:

- all `59` authoritative personas are now roster-valid delegation targets
- the `20` promoted personas are authoritative in H3 but remain `planned`
- `planned` personas must keep `allowed_actions = []`, `allowed_domains = []`, and `action_count = 0` until H5 closes the activation gate
- non-authoritative overflow registry agents no longer exist in the authoritative persona surface

## Required Guarantees

- exactly `59` authoritative personas
- exactly `10` departments
- exactly `34` active personas and `25` planned personas until H5
- deterministic alias resolution for canonical-agent and full-name targets
- stable projection of manager, escalation owner, approval owner, and staged action boundaries

## No-Go Conditions

- any promoted persona becomes `active` in H3
- any promoted persona exposes actions or domains before H5
- summary counts drift away from `59 total / 34 active / 25 planned`
- the roster, capability map, and persona registry disagree on membership
