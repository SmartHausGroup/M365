# M365 Unified Audit Schema v2

Before `E1E`, the repo still had two materially different audit dialects:

- instruction-api audit wrote `ts, action, user, details`
- ops-adapter audit wrote `timestamp, correlation_id, surface, agent, action, status, details`, with richer actor, executor, and admin-event extensions

That meant the control plane could not yet claim one shared evidence contract across the expanding workforce runtime.

## Canonical Rule

`AuditRecordV2 = (schema_version, timestamp, ts, correlation_id, surface, agent, action, status, details, result, actor?, persona?, executor?, approval?, before?, after?)`

If a runtime surface cannot project into that envelope, the unified workforce audit model is incomplete.

## Machine-Readable Authority

The canonical authority for this act is:

- [unified_audit_schema_v2.yaml](/Users/smarthaus/Projects/GitHub/M365/registry/unified_audit_schema_v2.yaml)

The shared runtime projection is:

- [audit_schema.py](/Users/smarthaus/Projects/GitHub/M365/src/smarthaus_common/audit_schema.py)

## Runtime Extraction

`E1E` projects the shared schema into both existing audit writers:

- [audit.py](/Users/smarthaus/Projects/GitHub/M365/src/ops_adapter/audit.py)
- [audit.py](/Users/smarthaus/Projects/GitHub/M365/src/provisioning_api/audit.py)

This means:

1. instruction-api audit now emits the same canonical top-level envelope as ops-adapter audit
2. ops-adapter audit keeps its richer actor, executor, admin, and approval evidence but now places it inside one stable schema
3. the older instruction-api aliases `ts` and `user` remain present for bounded backward compatibility

## Canonical Contexts

The unified schema normalizes these evidence contexts:

- `actor`
  - `actor`
  - `actor_tier`
  - `actor_groups`
- `persona`
  - `persona`
  - `persona_target`
- `executor`
  - `executor`
  - `tenant`
- `approval`
  - `approval_id`
  - `approval_profile`
  - `risk_class`
  - `required`
  - `approvers`
  - `rule_source`
  - `decision`
  - `reason`
- `result`
  - `outcome`
  - `payload`
  - `error`
  - `trace_id`
  - `blocked`
  - `idempotent_replay`

## What E1E Resolves

`E1E` resolves the audit-authority split:

- one machine-readable audit schema
- one shared runtime builder
- one canonical top-level envelope across instruction-api and ops-adapter surfaces
- one bounded verification path for the instruction-api audit writer

## What E1E Does Not Yet Resolve

- live workforce certification across the expanded workload universe
- retention, tamper-evidence, and custody guarantees for every downstream deployment topology
- workload-by-workload audit adoption beyond the currently wired runtime surfaces

Those remaining acts begin at:

- `E2A` through `E9E`
