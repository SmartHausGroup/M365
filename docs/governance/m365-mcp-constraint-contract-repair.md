# M365 MCP Constraint Contract Repair

## Purpose

Define the governed repair scope for the inconsistent MCP `validate_action` behavior observed during `B7C`, and make the ownership boundary explicit before `B7D` resumes.

## Observed Mismatch

During `B7C`, the governed write validations passed for the real runtime and tracker edits, but bounded read-only validation and governance-closeout command shapes were rejected on metadata semantics.

Observed live-failure class:

- bounded `test_run` validation for read-only proof commands rejected despite explicit plan references and notebook evidence
- governance-closeout validation shapes rejected when expressed as `governance_edit`
- equivalent governance-closeout writes could pass when normalized to `file_edit` with `scope=governance`

Observed live constraint identifiers during the rejected upstream gate responses:

- `map-7-gating-for-long-running`
- `map-8-notebook-first-for-notebook-error-fix`
- `qual-4-fix-root-cause-mode`
- `qual-5-testing-real-service-warning`
- `qual-7-metrics-notice`
- `tg-5-test-run-tier`

## Root Cause Boundary

The failing constraint identifiers are not defined anywhere in this repo, but the live source files are present in the sibling UCP repo:

- `/Users/smarthaus/Projects/GitHub/UCP/configs/constraints/ma_process.yaml`
- `/Users/smarthaus/Projects/GitHub/UCP/configs/constraints/quality.yaml`
- `/Users/smarthaus/Projects/GitHub/UCP/configs/constraints/tier_gating.yaml`
- `/Users/smarthaus/Projects/GitHub/UCP/src/ucp/constraints/evaluator.py`

That means:

- this repo is the source of truth for the execution record, plan sequencing, and prompt discipline
- the actual constraint implementation and metadata parser behavior live in upstream UCP, even though the affected act and execution record live here

This act therefore exists to prevent local runtime work from proceeding while the governance contract itself remains ambiguous.

## Accepted Live Contract

The repaired contract is now explicit and matches the live UCP evaluator.

### Bounded `test_run` in `scope=test`

The bounded passing shape proved on 2026-03-19 uses:

- top-level `action_type=test_run`
- top-level `target`
- top-level `scope=test`
- top-level `plan_ref`
- top-level `approval=true`
- `metadata.plan_hint`
- `metadata.error_id`
- `metadata.root_cause`
- `metadata.test_target`
- `metadata.command_name`
- `metadata.dataset`
- notebook backing via `metadata.has_notebook_backing=true`

Important detail:

- `metadata.root_cause` alone is not enough for the current live contract
- `map-8-notebook-first-for-notebook-error-fix` still requires `metadata.error_id` plus notebook backing
- notebook backing passes only when `metadata.has_notebook_backing` is truthy or `metadata.notebook_path` is a non-empty string

### Governance closeout in `scope=governance`

The bounded passing shape proved on 2026-03-19 uses:

- top-level `action_type=governance_edit`
- top-level `target`
- top-level `scope=governance`
- top-level `plan_ref`
- top-level `approval=true`
- notebook backing via `metadata.has_notebook_backing=true`

No `test_run`-specific metadata keys are required for the governance-closeout shape.

## Validated Passing Shapes

Live `validate_action` proofs on 2026-03-19:

1. Bounded read-only validation accepted:
   - `action_type=test_run`
   - `target=PYTHONPATH=src pytest -q tests/test_ops_adapter.py tests/test_approvals.py`
   - `scope=test`
   - `plan_ref=plan:m365-enterprise-readiness-master-plan:B7C1`
   - metadata:
     - `plan_hint=B7C1 bounded proof run`
     - `error_id=b7c1-metadata-contract`
     - `root_cause=validate_action metadata contract ambiguity`
     - `test_target=tests/test_ops_adapter.py tests/test_approvals.py`
     - `command_name=pytest`
     - `dataset=bounded-local-fixtures`
     - `has_notebook_backing=true`

2. Governance closeout accepted:
   - `action_type=governance_edit`
   - `target=docs/governance/m365-mcp-constraint-contract-repair.md`
   - `scope=governance`
   - `plan_ref=plan:m365-enterprise-readiness-master-plan:B7C1`
   - metadata:
     - `command_name=governance_closeout`
     - `dataset=b7c1-live-contract-proof`
     - `has_notebook_backing=true`

## Repair Result

The live contract mismatch turned out to be a local understanding and documentation gap, not a required UCP code mutation.

The repaired result is:

- this repo now records the exact accepted metadata keys
- the ownership boundary is explicit
- one bounded `test_run` shape and one `governance_edit` shape have both been admitted by the live gate
- `B7D` may resume without relying on undocumented metadata guesses

## Local Responsibilities

This repo must:

- block `B7D` until the contract mismatch is understood and validated against the live gate
- record the mismatch honestly in the governed action log
- keep the active plan and prompt inventory aligned to the repaired control plane

## Upstream UCP Responsibilities

The upstream governance layer remains the source of truth for:

- the actual constraint YAML
- the evaluator predicate semantics
- any future changes to the accepted metadata schema

No upstream mutation was required to close `B7C1`.

## Exit Criteria

`B7C1` is only complete when:

- the failing ownership boundary is explicit
- the accepted metadata contract is written down and unambiguous
- one bounded read-only validation shape is accepted under the repaired contract
- one governance-closeout validation shape is accepted under the repaired contract
- `B7D` can proceed without relying on undocumented gate behavior

All five conditions are now satisfied.
