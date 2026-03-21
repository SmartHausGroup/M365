# M365 Persona Discovery Contract v1

## Purpose

Make it easy for Claude and UCP to find and target the right digital employee for any
request by providing deterministic discovery filters, ranking criteria, and selection rules
across all 39 personas, 10 departments, and the full capability-family taxonomy.

## Problem

The delegation contract (E7A) defines how requests flow from Claude through UCP to the
workforce. But the persona resolution phase needs a formal discovery contract defining
how to find the right persona in the first place — by name, department, capability,
workload family, risk tier, or coverage status.

## Decision

`registry/persona_discovery_contract_v1.yaml` is now the authoritative persona discovery
and selection contract.

## Discovery Dimensions

1. **By Name** — resolve via display name, slug, agent ID, or alias
2. **By Department** — list all personas in a department
3. **By Capability Family** — find personas matching capability families
4. **By Workload Family** — find personas matching workload families
5. **By Risk Tier** — filter by risk tier
6. **By Coverage Status** — filter by registry-backed vs contract-only

## Selection Rules

- **Single Match** — select the matched persona
- **Multiple Matches** — rank by specificity and return for confirmation
- **No Match** — return not-found with suggested alternatives
- **Ambiguity** — fail closed

## Required Guarantees

- deterministic discovery results for fixed registry state
- every persona discoverable through at least one dimension
- contract-only personas visible but clearly marked as not action-backed

## No-Go Conditions

- a persona exists in the registry but is not discoverable
- discovery results differ for the same query on the same state
- a contract-only persona is presented as action-backed in discovery results
