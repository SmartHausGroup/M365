# M365 Audit and Governance Evidence Model

**Status:** `A3` imported; runtime synchronized through `B3`
**Date:** 2026-03-17
**Plan refs:** `plan:m365-enterprise-commercialization-readiness:R3`, `plan:m365-enterprise-commercialization-readiness:P2A`, `plan:m365-enterprise-readiness-master-plan:B3`, `plan:m365-enterprise-readiness-master-plan:R7`

This document defines the minimum audit and governance evidence model required to describe standalone M365 v1 honestly to an enterprise buyer. It does not claim that all requirements are already implemented. It defines what evidence is required, what evidence exists today, and which gaps remain open.

Deterministic evidence rule for this repository state:

`EnterpriseAuditClaim = RequiredEventModel + GovernanceEvidenceModel + GapDisclosure`

If any required enterprise audit or governance expectation lacks either a mapped evidence source or an explicit documented gap, the commercialization claim is invalid.

## Required Audit Events

Standalone M365 v1 needs an explicit required-event model across both the instruction API and the ops-adapter governance layer.

### Required event classes

1. **Request correlation event**
   - Required fields: request timestamp, correlation/request ID, action, channel or surface, tenant context when available
   - Current evidence sources:
     - `src/ops_adapter/main.py`
     - `src/ops_adapter/app.py`
     - `src/provisioning_api/main.py`
     - `src/provisioning_api/routers/m365.py`

2. **Actor and auth-context event**
   - Required fields: authenticated actor or service identity, auth mode, agent or caller context, user-context indicator when applicable
   - Current evidence sources:
     - `src/provisioning_api/routers/m365.py`
     - `src/ops_adapter/main.py`
     - `src/ops_adapter/app.py`

3. **Policy decision event**
   - Required fields: allow/deny result, reason, rate-limit or approval requirement state, correlation ID
   - Current evidence sources:
     - `src/ops_adapter/policies.py`
     - `src/ops_adapter/main.py`
     - `src/ops_adapter/app.py`

4. **Approval lifecycle event**
   - Required fields: approval created, approval target action, approval ID, approver identity, approval decision, decision reason, correlation ID
   - Current evidence sources:
     - `src/ops_adapter/main.py`
     - `src/ops_adapter/approvals.py`

5. **Execution result event**
   - Required fields: success, failure, blocked, or denied status; action; result or error summary; correlation ID
   - Current evidence sources:
     - `src/ops_adapter/audit.py`
     - `src/ops_adapter/main.py`
     - `src/ops_adapter/app.py`
     - `src/provisioning_api/routers/m365.py`
     - `src/provisioning_api/audit.py`

6. **Idempotency and replay event**
   - Required fields: idempotency key class, replay indicator, original or replayed outcome, trace/correlation linkage
   - Current evidence sources:
     - `src/provisioning_api/routers/m365.py`
     - `docs/contracts/caio-m365/MATHEMATICS.md`
     - `docs/contracts/caio-m365/LEMMA_L4.md`

7. **Mutation gate event**
   - Required fields: mutation allowed or blocked, gate reason, action attempted, trace/correlation linkage
   - Current evidence sources:
     - `src/provisioning_api/routers/m365.py`
     - `docs/CAIO_M365_CONTRACT.md`

8. **Administrative configuration event**
   - Required fields: tenant config read, reload, permission-tier mutation, actor, target tenant, before/after or requested effect, correlation ID
   - Current evidence sources:
     - `src/ops_adapter/audit.py`
     - `src/ops_adapter/actions.py`
     - `src/ops_adapter/main.py`
     - `tests/test_ops_adapter.py`

### Current evidence split

The repository has two materially different audit surfaces:

1. **Instruction API audit**
   - Formally documented and partially verified
   - Evidence sources:
     - `docs/contracts/caio-m365/MATHEMATICS.md`
     - `docs/contracts/caio-m365/LEMMA_L4.md`
     - `configs/generated/m365_audit_verification.json`
     - `src/provisioning_api/routers/m365.py`
     - `src/provisioning_api/audit.py`

2. **Ops-adapter and admin governance audit**
   - Implemented in runtime behavior and append-only local audit records
   - Admin/configuration actions now emit explicit admin-event records instead of returning snapshot-only state
   - Evidence sources:
     - `src/ops_adapter/audit.py`
     - `src/ops_adapter/main.py`
     - `src/ops_adapter/app.py`
     - `src/ops_adapter/actions.py`
     - `tests/test_ops_adapter.py`

## Governance Evidence

To support enterprise review, audit records alone are not enough. Governance evidence must also show why an action was allowed, denied, or held for approval.

### Required governance evidence classes

1. **Policy evaluation evidence**
   - OPA decision outcome
   - reason for deny or approval requirement
   - correlation ID linking policy to request and execution

2. **Approval-boundary evidence**
   - which actions require approval
   - approval creation and resolution records
   - approver identity and method

3. **Actor traceability evidence**
   - calling service or user identity
   - tenant context
   - agent or role context where routing depends on persona registry

4. **Administrative change evidence**
   - tenant-config reads and reloads
   - permission-tier changes
   - evidence of before/after state or explicit mutation intent

5. **Audit-pipeline evidence**
   - local durable log sink
   - external forwarding path when configured
   - sanitization or redaction behavior for sensitive fields

6. **Formal verification evidence**
   - contract docs that define audit guarantees
   - generated verification artifacts showing the scope of what has actually been verified

### Current mapped evidence

| Governance requirement | Current mapped evidence | Classification |
| --- | --- | --- |
| Correlation IDs | `src/ops_adapter/main.py`, `src/ops_adapter/app.py`, `src/provisioning_api/main.py`, `src/provisioning_api/routers/m365.py` | Present |
| Policy deny / approval-required outcomes | `src/ops_adapter/policies.py`, `src/ops_adapter/main.py`, `src/ops_adapter/app.py` | Present |
| Approval lifecycle logging | `src/ops_adapter/main.py` | Present |
| Instruction API formal audit guarantee | `docs/contracts/caio-m365/MATHEMATICS.md`, `docs/contracts/caio-m365/LEMMA_L4.md`, `configs/generated/m365_audit_verification.json` | Present but narrow |
| Local ops-adapter audit sink with redaction | `src/ops_adapter/audit.py` | Present |
| Enterprise forwarding hook | `src/ops_adapter/audit.py` via `AUDIT_SERVICE_URL` | Present but best-effort |
| Admin audit for tenant/permission operations | `src/ops_adapter/audit.py`, `src/ops_adapter/actions.py`, `tests/test_ops_adapter.py` | Present for active ops-adapter admin surface |

## Current Gaps

The current repository state is not yet sufficient to claim complete enterprise audit posture.

1. **No unified audit schema across instruction API and ops-adapter**
   - Instruction API records use `ts, action, user, details`.
   - Ops-adapter records now use `timestamp, correlation_id, surface, agent, action, status, details`, with admin-event extensions such as `event_class`, `actor`, `tenant`, `before`, and `after`.
   - Enterprise review still needs the normalization boundary documented, not glossed over.

2. **Generated audit verification is narrow**
   - `configs/generated/m365_audit_verification.json` shows a passing result, but only for a limited schema check and a small record count.
   - `B3` adds targeted runtime tests for the admin/config audit path, but the generated artifact is still narrower than full enterprise governance coverage.

3. **Audit delivery is fail-open**
   - `src/ops_adapter/audit.py` intentionally avoids raising on forwarding failures.
   - That is acceptable operationally, but enterprise acceptance needs a defined reliability and monitoring expectation for the audit pipeline.

4. **Retention, tamper-evidence, and evidence custody are not yet formalized**
   - The current docs do not yet define enterprise retention duration, immutable storage requirements, or evidence export procedure for audit review.

## Enterprise Acceptance Expectations

Enterprise commercialization may proceed only with explicit acceptance boundaries.

### Minimum evidence expectation for a credible enterprise review

1. Supported v1 actions must have request-to-outcome traceability.
2. Policy decisions and approval requirements must be inspectable with correlation linkage.
3. Approval lifecycle records must exist for approval-bound actions.
4. Admin configuration operations must have a documented evidence story, even if current implementation is partial.
5. The boundary between formal instruction-audit guarantees and partial ops-adapter/admin evidence must be disclosed.
6. Any gap between current runtime behavior and enterprise-grade evidence expectations must be documented as a gap, not marketed as complete.

### Minimum evidence expectation for future enterprise release acceptance

1. Governance evidence must include reliable actor, tenant, action, decision, and approval linkage.
2. Audit schemas across major surfaces should either converge or be explicitly normalized for review/export.
3. Audit pipeline reliability, retention, and export expectations must be documented and tested.
4. Live-tenant validation in `P3A` must distinguish:
   - instruction API audit proof
   - ops-adapter governance proof
   - admin/configuration audit proof

### Fail-closed commercialization rule

Until the current gaps are closed or explicitly accepted as limited scope, SmartHaus may claim:

1. formal audit guarantees for the instruction API surface only where contract docs and generated verification already exist
2. runtime audit and governance behavior exists for ops-adapter and admin surfaces, including append-only admin/configuration events on the active request path
3. full live-certified enterprise governance evidence remains downstream of `C1` and `C2`

SmartHaus may not claim:

1. unified fully verified audit evidence across every M365 runtime surface today
2. immutable or externally guaranteed enterprise evidence custody today
3. live-certified governance evidence before `C1` and `C2`
