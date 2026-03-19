# M365 Persona Registry and Humanized Delegation Contract

## Purpose

Define how natural-language delegation targets named digital employees while remaining policy-gated and auditable.

## Delegation Contract

User-facing commands should resolve through persona identity:

- “Talk to Elena Rodriguez”
- “Have Priya handle this”
- “Route this to Marcus in Operations”

The runtime contract is:

1. resolve persona
2. verify persona exists and is active
3. verify the requested work fits the persona’s responsibility boundary
4. map the task to one executor domain
5. apply policy, approval, and audit rules

## Persona Registry Minimum Fields

- `persona_id`
- `display_name`
- `department`
- `title`
- `manager`
- `responsibilities`
- `allowed_domains`
- `approval_owner`
- `status`
- `external_presence_policy`

## Audit Rule

Every action must preserve:

- human requester
- digital employee persona
- selected executor domain
- approval result
- runtime evidence

## Public Persona Rule

External or public presence is a later-stage operating mode.

No public persona should exist without:

- explicit AI disclosure
- brand governance
- human-review policy
- approval-bound outbound channels
