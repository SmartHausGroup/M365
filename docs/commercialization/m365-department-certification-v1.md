# SMARTHAUS M365 Department Certification v1

## Purpose

Define the deterministic certification contract for every department pack in the expanded SMARTHAUS workforce, certifying each department against its target workflows and responsibilities.

## Authority

- **Contract:** `registry/department_certification_v1.yaml`
- **Department packs:** `registry/department_pack_*_v1.yaml`
- **Persona source:** `registry/persona_registry_v2.yaml`

## Problem

H4S rebased the department-pack authority to the staged post-H3 roster, but the department certification contract still undercounted the workforce and omitted the active/planned split. Without this contract, the program cannot claim truthful department-level coverage for the staged pre-H5 state.

## Decision

Make `registry/department_certification_v1.yaml` the authoritative department certification contract with four ordered certification phases and explicit staged counts.

## Certification Phases

1. **Pack Presence** — verify every department has a valid pack YAML.
2. **Persona Count Alignment** — verify pack persona counts match the persona registry.
3. **Workflow Family Coverage** — verify every pack has workflow and workload families.
4. **Bounded Claim Consistency** — verify no pack claims beyond its surface.

## Certification Results

All 10 departments pass four-phase certification with `59` total personas distributed correctly across the staged pre-H5 workforce:

- `34` active / registry-backed personas
- `25` planned / contract-only personas
- rebased workflow-family and workload-family counts that match the H4S department-pack contracts

## No-Go Conditions

- Missing department pack file.
- Persona count mismatch between pack and registry.
- Active/planned or registry-backed/contract-only counts drift from the staged H4 truth.
- Pack with zero workflow or workload families.
- Claim exceeding declared surface.

## Next Dependency

`H5` (Activation Gate Closeout) is the next governed act after H4 closes.
