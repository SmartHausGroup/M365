# L111 - M365 Capability Pack C3 Docstring Audit v1

**Lemma id:** `L111_m365_cps_c3_docstring_audit_v1`
**Plan reference:** `plan:m365-cps-trkC-p3-mcp-tool-docstrings:T2`
**Predecessor:** `L110_m365_cps_c2_planned_short_circuit_v1`

## Mission

Add an audit script that cross-references the action-name references
inside MCP tool docstrings with the runtime registry + alias table and
reports per-action coverage status. The script doubles as a linter:
running it as part of CI surfaces drift between what tool docstrings
advertise and what the runtime can actually invoke.

## Predicate

```
DocstringAuditValid =
    L_AUDIT_SCRIPT_PRESENT
  ∧ L_AUDIT_OUTPUT_VALID
  ∧ L_LINTER_DETERMINISTIC
  ∧ L_NO_REGRESSION
```

## Lemmas

### L_AUDIT_SCRIPT_PRESENT

`scripts/audit_m365_docstring_coverage.py` exists and is invokable from
the M365 repo root. It reads `agents.yaml` allowed_actions (the
operator-facing surface) and classifies each action via
`compute_coverage_status`.

### L_AUDIT_OUTPUT_VALID

The script emits a JSON report:
```json
{
  "implemented": [...],
  "aliased": [...],
  "planned": [...],
  "deprecated": [],
  "totals": {"implemented": N, "aliased": M, "planned": K, "deprecated": L},
  "advertised_total": N+M+K+L,
  "coverage_pct_concrete": (N+M)/(N+M+K+L)*100
}
```

### L_LINTER_DETERMINISTIC

Given the same registry + alias table + agents.yaml, the audit produces
the same JSON output. Lists are sorted; counts are integer.

### L_NO_REGRESSION

All Track A + B + C1 + C2 tests pass.
