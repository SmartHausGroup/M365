# Execution Prompt — Persona-Action Certification

Plan Reference: `plan:m365-persona-action-certification`
North Star Reference: `Operations/NORTHSTAR.md`
Execution Plan Reference: `Operations/EXECUTION_PLAN.md`

**Mission:** Certify the full workforce graph, not just the direct instruction surface. Prove every persona is reachable or fenced, prove every persona-facing action is mapped or classified, identify orphan/stub/dead-route paths, and only then claim workforce support.

## Governance Lock

Before any write or mutating action:

1. Read:
- `AGENTS.md`
- applicable `.cursor/rules/**/*.mdc`
- `Operations/NORTHSTAR.md`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`
- `plans/m365-persona-action-certification/m365-persona-action-certification.md`
- predecessor evidence:
  - `plans/m365-direct-full-surface-certification/m365-direct-full-surface-certification.md`
  - `docs/commercialization/m365-direct-full-surface-certification.md`
  - `artifacts/diagnostics/m365_direct_full_surface_certification.json`
- workforce graph sources:
  - `registry/agents.yaml`
  - `registry/ai_team.json`
  - `registry/persona_registry_v2.yaml`
  - `registry/persona_capability_map.yaml`
  - `registry/capability_registry.yaml`
  - `registry/auth_model_v2.yaml`
  - `registry/approval_risk_matrix_v2.yaml`
  - `registry/executor_routing_v2.yaml`
  - `src/provisioning_api/routers/m365.py`
  - `src/ops_adapter/main.py`
  - `src/ops_adapter/actions.py`
  - `src/ops_adapter/personas.py`

2. Cite:
- `plan:m365-persona-action-certification:R0` through `R6`
- `G0` through `G5`

3. Stop immediately if:
- the work escapes the allowlist
- UCP-side edits are required
- certification would require undocumented or unsafe tenant changes

## Execution Order

1. `G0` workforce graph lock
2. `G1` persona reachability certification
3. `G2` mapping / orphan / stub audit
4. `G3` unique action execution certification reuse
5. `G4` persona/action certification
6. `G5` closeout

## Hard rule

Do not treat a persona as certified just because one lower-level action works somewhere in the repo. Workforce certification must prove:

- the persona can actually be reached
- the persona-facing action is actually mapped
- the runtime path is real rather than stubbed or dead
- the execution or approval result is classified truthfully

Every persona and every persona-facing action must end the initiative classified as:

- `green`
- `approval-gated`
- `permission-blocked`
- `tenant-blocked`
- `stubbed`
- `dead-routed`
- `orphaned`
- or `fenced`
