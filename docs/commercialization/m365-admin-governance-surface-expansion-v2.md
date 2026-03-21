# M365 Admin and Governance Surface Expansion v2

## Purpose

`E4E` closes the remaining bounded enterprise-admin and governance gap in the workforce plane by turning Microsoft 365 admin reports and Entra access reviews into first-class governed instruction-surface actions.

## Bounded Surface

The supported `E4E` actions are:

- `get_report`
- `get_usage_reports`
- `get_activity_reports`
- `list_access_reviews`
- `get_access_review`
- `create_access_review`
- `list_access_review_decisions`
- `record_access_review_decision`

## Deterministic Contract

- Report actions are bounded to a fixed allowlist of named Microsoft 365 admin reports and fixed periods `D7`, `D30`, `D90`, and `D180`.
- Report actions always return a normalized `report` envelope with `name`, `category`, `period`, `format`, `rows`, and `count`.
- Access-review actions are bounded to review definitions and decision records only.
- Report actions route to the `reports` executor domain and require app-only auth.
- Access-review actions route to the `access_reviews` executor domain and require app-only auth.
- Read actions are low-observe and non-approval-bearing.
- Mutating access-review actions are high-impact and approval-bearing.

## Runtime Extraction

- Shared runtime: `src/smarthaus_common/admin_governance_client.py`
- Instruction router: `src/provisioning_api/routers/m365.py`
- Authority registry: `registry/admin_governance_surface_expansion_v2.yaml`

## Proof Chain

- Lemma: `docs/ma/lemmas/L42_m365_admin_governance_surface_expansion_v2.md`
- Invariant: `invariants/lemmas/L42_m365_admin_governance_surface_expansion_v2.yaml`
- Notebook: `notebooks/m365/INV-M365-AR-admin-governance-surface-expansion-v2.ipynb`
- Lemma proof notebook: `notebooks/lemma_proofs/L42_m365_admin_governance_surface_expansion_v2.ipynb`
- Scorecard: `artifacts/scorecards/scorecard_l42.json`

## Validation

- `python3 -m py_compile src/smarthaus_common/admin_governance_client.py src/provisioning_api/routers/m365.py scripts/ci/verify_admin_governance_surface_expansion.py tests/test_admin_governance_surface_expansion_v2.py scripts/ci/verify_caio_m365_contract.py scripts/ci/build_capability_registry.py`
- `PYTHONPATH=src .venv/bin/pytest -q tests/test_admin_governance_surface_expansion_v2.py`
- `PYTHONPATH=src .venv/bin/pytest -q tests/test_executor_routing_v2.py tests/test_auth_model_v2.py tests/test_approval_risk_v2.py tests/test_admin_governance_surface_expansion_v2.py`
- `PYTHONPATH=src python3 scripts/ci/verify_admin_governance_surface_expansion.py`
- `PYTHONPATH=src python3 scripts/ci/build_capability_registry.py`
- `PYTHONPATH=src python3 scripts/ci/verify_capability_registry.py`
- `PYTHONPATH=src python3 scripts/ci/verify_caio_m365_contract.py`
