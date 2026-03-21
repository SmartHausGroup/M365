# M365 Persona Registry v2

## Purpose

Define the authoritative digital-employee registry for the SMARTHAUS workforce runtime.

## Problem

The legacy runtime persona projection merged the entire `registry/agents.yaml` inventory with the
authoritative roster. That produced `59` active personas, including `20` non-authoritative
registry-only agents that are not part of the committed `39`-persona workforce.

## Decision

`registry/persona_registry_v2.yaml` is now the authoritative runtime registry for digital
employees.

It is built deterministically from:

- `registry/ai_team.json`
- `registry/persona_capability_map.yaml`
- `registry/agents.yaml`

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
  - authoritative persona with locked contract fields but not yet action-backed
- `inactive`
  - authoritative persona that is intentionally unavailable

## Runtime Rule

Only personas present in `registry/persona_registry_v2.yaml` may be treated as valid digital
employees by the governed runtime.

That means:

- non-authoritative overflow registry agents are not valid delegation targets
- authoritative contract-only personas remain addressable in the registry, but they stay
  fail-closed for action execution until later workload phases make them action-backed

## Required Guarantees

- exactly `39` personas
- exactly `10` departments
- zero non-authoritative overflow agents in runtime persona resolution
- deterministic alias resolution for full-name and canonical-agent targets
- stable projection of status, approval ownership, and executor-domain boundaries

## No-Go Conditions

- runtime can still resolve the extra registry-only agents as personas
- required persona fields are missing
- persona status and coverage status disagree
- summary counts drift from the roster authority
