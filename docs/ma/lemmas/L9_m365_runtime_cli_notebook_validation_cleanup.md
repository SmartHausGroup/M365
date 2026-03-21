# L9 — M365 Runtime, CLI, and Notebook Validation Cleanup

## Claim

After `B4D2` clears the scripts and CI tooling surface, the runtime, CLI, governed-test, and notebook validation cleanup act is admissible iff:

1. the touched surface is limited to runtime, CLI, governed-test, and notebook formatting files required by the pinned failure inventory
2. the scoped Ruff and formatter failure set for that execution surface is reduced deterministically
3. the remediation does not widen into Mypy-environment fixes or unrelated repo-wide spillover

## Existing Proof Sources

- `artifacts/b4d3_failure_inventory.json`
- `notebooks/m365/INV-M365-K-runtime-cli-notebook-cleanup.ipynb`
- `notebooks/lemma_proofs/L9_m365_runtime_cli_notebook_validation_cleanup.ipynb`
- `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4d3-runtime-cli-ruff-black-cleanup.md`

## Acceptance Evidence

- `ruff check` returns zero violations over the pinned runtime/CLI/governed-test surface
- formatter acceptance is restored for the touched runtime/CLI files and the governed notebook surface
- touched-file diff remains bounded to the runtime/CLI/notebook cleanup surface plus MA traceability artifacts
- `git diff --check` remains clean after the scoped patch

## Deterministic Surface

`ExecutionGate(B4D3) = RuffOK(runtime ∪ cli ∪ governed_tests) + FormatOK(runtime ∪ cli ∪ notebooks) + ScopeBoundedDiff + NoMypySurfaceExpansion`
