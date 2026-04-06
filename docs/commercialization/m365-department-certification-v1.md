# SMARTHAUS M365 Department Certification v1

## Purpose

Define the deterministic certification contract for every department pack in the expanded SMARTHAUS workforce, certifying each department against its target workflows and responsibilities.

## Authority

- **Contract:** `registry/department_certification_v1.yaml`
- **Department packs:** `registry/department_pack_*_v1.yaml`
- **Persona source:** `registry/persona_registry_v2.yaml`

## Problem

H5 closed the activation gate, but department certification still claims the staged `34 active / 25 planned` split. Without rebasing this contract, the program cannot claim truthful department-level coverage for the final post-H5 state.

## Decision

Make `registry/department_certification_v1.yaml` the authoritative department certification contract with four ordered certification phases and explicit final post-H5 counts. The department-status field continues to mirror the current department-pack authority surface because those pack files remain outside this bounded correction.

## Certification Phases

1. **Pack Presence** — verify every department has a valid pack YAML.
2. **Persona Count Alignment** — verify pack persona counts match the persona registry.
3. **Workflow Family Coverage** — verify every pack has workflow and workload families.
4. **Bounded Claim Consistency** — verify no pack claims beyond its surface.

## Certification Results

All 10 departments pass four-phase certification with `59` total personas distributed correctly across the final post-H5 workforce:

- `54` active / registry-backed personas
- `5` planned / contract-only personas
- rebased workflow-family and workload-family counts that still match the current H4S department-pack contracts
- preserved department-pack status labels (`registry-backed` or `partial-activation`) from the current pack authority surface

## No-Go Conditions

- Missing department pack file.
- Persona count mismatch between pack and registry.
- Active/planned or registry-backed/contract-only counts drift from the final `59 / 54 / 5` truth.
- Pack with zero workflow or workload families.
- Claim exceeding declared surface.

## Next Dependency

Fresh `M1` merge replay is the next governed act after the post-H5 certification parity correction closes.
