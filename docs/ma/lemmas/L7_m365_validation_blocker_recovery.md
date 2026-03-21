# L7 — M365 Validation-Blocker Syntax Recovery

## Claim

The repo-wide validation pipeline cannot enter meaningful Ruff/Black/Mypy remediation until the narrow hard-blocker surface is syntactically valid:

1. `scripts/generate-policies.py` must parse under Python
2. the malformed invariants under `governance/invariants/m365/` must parse under YAML
3. blocker recovery must not widen into unrelated repo-wide lint cleanup

## Existing Proof Sources

- `notebooks/m365/INV-M365-I-validation-blocker-recovery.ipynb`
- `notebooks/lemma_proofs/L7_m365_validation_blocker_recovery.ipynb`
- `scripts/generate-policies.py`
- `governance/invariants/m365/INV-M365-B-001.yaml`
- `governance/invariants/m365/INV-M365-E-001.yaml`
- `governance/invariants/m365/INV-M365-F-001.yaml`
- `governance/invariants/m365/INV-M365-G-001.yaml`
- `docs/prompts/codex-m365-enterprise-readiness-master-plan-b4c-validation-blockers-syntax-recovery.md`

## Acceptance Evidence

- Python parser accepts `scripts/generate-policies.py`
- YAML loader accepts the four corrected invariant files
- `git diff --check` remains clean after the scoped recovery patch

## Deterministic Surface

`SyntaxGate(B4C) = PythonParse(script_generate_policies) + YamlParse(invariant_blocker_set) + ScopeBoundedDiff`
