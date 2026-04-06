# M365 Persona Registry v2

## Purpose

Define the authoritative digital-employee registry for the SMARTHAUS workforce runtime.

## Problem

H3 rebased the authoritative roster to `59` named personas, and H4 preserved a
staged truth of `34` active and `25` planned personas. H5 closes the final
activation gate so the governed `20` promoted personas become fully active while
the `5` deferred external-platform personas remain fail-closed.

## Decision

`registry/persona_registry_v2.yaml` remains the authoritative runtime registry
for digital employees. It is built deterministically from:

- `registry/ai_team.json`
- `registry/persona_capability_map.yaml`
- `registry/agents.yaml`

## Current Authoritative Summary

- Total personas: `59`
- Total departments: `10`
- Active personas: `54`
- Planned personas: `5`
- Registry-backed personas: `54`
- Persona-contract-only personas: `5`

The only remaining planned personas are the deferred external-platform
marketing roles.

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
  - authoritative persona that remains governed but not yet action-capable
- `inactive`
  - authoritative persona that is intentionally unavailable

## Runtime Rule

Only personas present in `registry/persona_registry_v2.yaml` may be treated as
valid digital employees by the governed runtime.

That means:

- all `59` authoritative personas are valid delegation targets
- the governed `20` promoted personas are now `active`
- the `5` deferred external-platform personas remain `planned` with `allowed_actions = []`, `allowed_domains = []`, and `action_count = 0`
- non-authoritative overflow registry agents do not exist in the authoritative surface

## Required Guarantees

- exactly `59` authoritative personas
- exactly `10` departments
- exactly `54` active personas and `5` planned personas after H5
- deterministic alias resolution for canonical-agent and full-name targets
- stable projection of manager, escalation owner, approval owner, and final action boundaries

## No-Go Conditions

- any governed promoted persona remains `planned` after H5
- any deferred external persona exposes actions or domains
- summary counts drift away from `59 total / 54 active / 5 planned`
- the roster, capability map, and persona registry disagree on membership
