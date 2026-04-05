# Lemma L79 — M365 Authoritative Persona Department Pack Rebase v1

## Statement

If every department-pack authority is rebased to the staged H3 authoritative registry truth and
every promoted persona remains `persona-contract-only` with zero supported actions, then H4 can
resume certification/count rebase without over-claiming activation or department coverage.

## Inputs

- `registry/persona_registry_v2.yaml`
- `registry/department_pack_*_v1.yaml`
- `docs/commercialization/m365-*-department-pack-v1.md`
- `scripts/ci/verify_*_department_pack_v1.py`
- `tests/test_*_department_pack_v1.py`

## Governing Formula

`H4S_GO = PreflightMismatchProof AND AllDepartmentPackCountsMatch AND NoActivationOverclaim AND DeterministicReplay`

where:

- `PreflightMismatchProof := seven departments differed between the pre-H4S pack counts and the staged H3 registry counts`
- `AllDepartmentPackCountsMatch := FOR ALL department, pack.required_personas = registry.total AND pack.required_active_personas = registry.active AND pack.required_registry_backed_personas = registry.registry_backed`
- `NoActivationOverclaim := FOR ALL contract_only_persona, supported_actions = []`
- `DeterministicReplay := repeated reconciliation emits the same verification hash`

## Proof Sketch

1. H3 rebased the authoritative workforce from `39` to `59` personas while leaving promoted personas staged and contract-only.
2. The pre-H4S department-pack authorities still encoded the old distribution for seven departments, which blocked H4 certification/count rebase.
3. H4S rebases the pack authority surface so each department pack mirrors the staged H3 totals, active counts, and registry-backed counts.
4. Every promoted persona remains contract-only with zero supported actions, so the pack contracts do not over-claim activation.
5. Therefore H4 may resume from truthful department-pack authority without silently changing runtime activation truth.

## Machine Bindings

- `scripts/ci/verify_*_department_pack_v1.py`
- `tests/test_*_department_pack_v1.py`
- `configs/generated/authoritative_persona_department_pack_rebase_v1_verification.json`
