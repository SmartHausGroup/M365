# SMARTHAUS M365 Department Certification v1

## Purpose

Define the deterministic certification contract for every department pack in the expanded SMARTHAUS workforce, certifying each department against its target workflows and responsibilities.

## Authority

- **Contract:** `registry/department_certification_v1.yaml`
- **Department packs:** `registry/department_pack_*_v1.yaml`
- **Persona source:** `registry/persona_registry_v2.yaml`

## Problem

E8A certified workloads and E8B certified personas. However, no contract certifies that each department pack has correct persona counts, valid workflow families, and bounded-claim consistency. Without this, the program cannot claim department-level coverage.

## Decision

Make `registry/department_certification_v1.yaml` the authoritative department certification contract with four ordered certification phases.

## Certification Phases

1. **Pack Presence** — verify every department has a valid pack YAML.
2. **Persona Count Alignment** — verify pack persona counts match the persona registry.
3. **Workflow Family Coverage** — verify every pack has workflow and workload families.
4. **Bounded Claim Consistency** — verify no pack claims beyond its surface.

## Certification Results

All 10 departments pass four-phase certification with 39 total personas distributed correctly.

## No-Go Conditions

- Missing department pack file.
- Persona count mismatch between pack and registry.
- Pack with zero workflow families.
- Claim exceeding declared surface.

## Next Dependency

`E8D` (Cross-Department Workflow Certification) is the next act.
