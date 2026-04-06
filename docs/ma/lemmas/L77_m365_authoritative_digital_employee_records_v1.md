# Lemma L77 — M365 Authoritative Digital Employee Records v1

## Statement

If every promoted persona has one bounded employee record with explicit
department, title, manager token, escalation token, and exactly three style
fields, then the authoritative roster can be rebased later without freeform
personality drift or chain-of-command ambiguity.

## Inputs

- `registry/authoritative_digital_employee_records_v1.yaml`
- `docs/commercialization/m365-authoritative-digital-employee-records-v1.md`
- `docs/commercialization/m365-authoritative-persona-census-and-department-model-decision.md`

## Proof Sketch

1. H1 fixes the set of 20 promoted personas and their approved departments.
2. H2 binds each promoted persona to one deterministic record keyed by the
   canonical agent identifier.
3. Each record must contain title, department, manager, escalation owner, and
   only the bounded style fields `working_style`, `communication_style`, and
   `decision_style`.
4. Because the manager and escalation tokens derive from the department, the
   chain of command is explicit and replay-stable.
5. Therefore H3-H5 can consume the employee records without inventing new
   personality schema or unbounded management metadata.

## Machine Bindings

- `scripts/ci/verify_authoritative_digital_employee_records_v1.py`
- `tests/test_authoritative_digital_employee_records_v1.py`
