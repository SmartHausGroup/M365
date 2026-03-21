# L8 — M365 Scripts and CI Ruff Cleanup

## Claim

After `B4D1` pins the clean-baseline validation inventory, the scripts and CI Ruff cleanup act is admissible iff:

1. the touched surface is limited to `scripts/` and `scripts/ci/`
2. the scoped Ruff error set for that tooling surface is reduced to zero
3. the remediation does not widen into runtime, notebook-format, or mypy-only work

## Existing Proof Sources

- `artifacts/b4d1_failure_inventory.json`
- `notebooks/m365/INV-M365-J-scripts-ci-ruff-cleanup.ipynb`
- `notebooks/lemma_proofs/L8_m365_scripts_ci_ruff_cleanup.ipynb`
- `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4d2-scripts-ci-ruff-cleanup.md`

## Acceptance Evidence

- `ruff check scripts scripts/ci` returns zero violations
- touched-file diff remains bounded to the scripts/CI tooling surface plus MA traceability artifacts
- `git diff --check` remains clean after the scoped patch

## Deterministic Surface

`ToolingGate(B4D2) = RuffOK(scripts ∪ scripts/ci) + ScopeBoundedDiff + NoRuntimeSurfaceExpansion`
