# Codex Prompt: M365 Authoritative Persona H3 Regression Proof Rebinding

Plan reference: `plan:m365-authoritative-persona-h3-regression-proof-rebinding:R1`

## Objective

Fix the remaining `M1` blocker by rebinding the stale H3 regression to frozen H3 proof artifacts instead of the live post-H5 authority files.

## Required outputs

- `plans/m365-authoritative-persona-h3-regression-proof-rebinding/m365-authoritative-persona-h3-regression-proof-rebinding.md`
- `plans/m365-authoritative-persona-h3-regression-proof-rebinding/m365-authoritative-persona-h3-regression-proof-rebinding.yaml`
- `plans/m365-authoritative-persona-h3-regression-proof-rebinding/m365-authoritative-persona-h3-regression-proof-rebinding.json`
- `docs/prompts/codex-m365-authoritative-persona-h3-regression-proof-rebinding-prompt.txt`
- synchronized `Operations/EXECUTION_PLAN.md`
- synchronized `Operations/ACTION_LOG.md`
- synchronized `Operations/PROJECT_FILE_INDEX.md`

## Constraints

- do not change live post-H5 registry truth
- use `configs/generated/authoritative_persona_registry_rebase_v1_verification.json` as the frozen staged H3 truth source unless the package proves another H3 artifact is more appropriate
- keep the correction bounded to the stale H3 regression surface and trackers
- fail closed if the frozen H3 proof is insufficient

## Required validations

- `PYTHONPATH=src .venv/bin/pytest -q tests/test_authoritative_persona_registry_rebase_v1.py`
- `PYTHONPATH=src .venv/bin/pytest -q tests/test_persona_registry_v2.py`
- `pre-commit run --all-files`
- `git diff --check`

## Notes

- This is not a live registry fix.
- This is a proof-binding fix so historical H3 assertions remain true without conflicting with the final post-H5 branch state.
