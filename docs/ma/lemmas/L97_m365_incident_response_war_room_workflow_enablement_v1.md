# Lemma L97: M365 Incident Response War Room Workflow Enablement v1

## Statement

For the incident response war room workflow package, the repo can only claim truthful composite provisioning if each requested workspace satisfies all of the following:

1. the Team and SharePoint site resolve through one shared M365 group-backed workspace identity
2. the command channel, runbook document, Planner plan, Planner bucket, and seed task are created or reused through deterministic idempotent selectors
3. the activation mail is bounded to an explicit sender mailbox and explicit recipient set
4. the public contract and registry surfaces describe the same composite action shape as the runtime
5. focused regression tests prove the orchestration path preserves the same asset contract and fail-closed Planner boundary

If any one of these obligations fails, the workflow surface remains non-green and must not be represented as fully enabled.

## Inputs

- Workflow request inputs:
  - `incidentName`
  - `teamName`
  - `siteName`
  - `incidentLeadUpn`
  - optional `mailNickname`, `commandChannelName`, `activationRecipients`, `activationSenderUserPrincipalName`, `runbookPath`, `planTitle`, `bucketName`, `seedTaskTitle`
- Planned write set:
  - `src/smarthaus_common/incident_response_war_room.py`
  - `src/provisioning_api/routers/m365.py`
  - `src/smarthaus_graph/client.py`
  - `scripts/ops/provision_incident_response_war_room.py`
  - `tests/test_incident_response_war_room.py`
  - `docs/commercialization/m365-incident-response-war-room-workflow-enablement.md`
  - `docs/CAIO_M365_CONTRACT.md`
  - `docs/contracts/caio-m365/ACTION_SPECIFICATION.md`
  - `docs/contracts/M365_CAPABILITIES_UNIVERSE.md`
  - `registry/capability_registry.yaml`
  - `registry/executor_routing_v2.yaml`
  - `registry/auth_model_v2.yaml`
  - `registry/approval_risk_matrix_v2.yaml`

## Formula

Let:

- `W(req)` be the resolved shared workspace identity for request `req`
- `C(req)` be the command-channel idempotence predicate
- `D(req)` be the runbook-document bounded-upsert predicate
- `P(req)` be the Planner seed idempotence predicate
- `M(req)` be the activation-mail bounded-delivery predicate
- `R(req)` be the contract-and-registry synchronization predicate
- `T(req)` be the focused regression result

Then the workflow claim is truthful iff:

`WarRoomTruth(req) = WorkspaceUnified(req) AND ChannelDeterministic(req) AND DocumentBounded(req) AND PlannerSeedIdempotent(req) AND MailBounded(req) AND ContractsSynced(req) AND TestsGreen(req)`

where:

- `WorkspaceUnified(req) := W(req)` yields exactly one shared M365 group-backed identity
- `ChannelDeterministic(req) := C(req)` preserves one command-channel selector
- `DocumentBounded(req) := D(req)` preserves one runbook path and bounded overwrite behavior
- `PlannerSeedIdempotent(req) := P(req)` either reuses or creates one plan/bucket/task seed deterministically
- `MailBounded(req) := M(req)` binds one sender mailbox and one explicit recipient set
- `ContractsSynced(req) := R(req)` keeps runtime, contract, and registry surfaces aligned
- `TestsGreen(req) := T(req) = pass`

## Boundary Conditions

- This lemma does not claim live tenant Planner writes are currently permission-green.
- This lemma does not authorize separate Team and site identities for one workflow request.
- This lemma does not allow implicit sender-mailbox inference without an explicit mailbox or incident lead.
- This lemma does not widen the workflow beyond Team, channel, site, runbook document, Planner seed, and activation mail.

## Determinism

- One shared workspace identity is authoritative for the Team and site.
- One command channel name is authoritative per workflow request.
- One runbook path, one plan title, one bucket name, and one seed task title are authoritative per workflow request.
- The live Planner `403` boundary remains explicit and fail-closed until tenant permissions change.

## Proof Sketch

The incident workflow is only truthful if the repo stops treating the Team and SharePoint site as separate workspace identities and instead derives both from one bounded group-backed contract. Once that identity is fixed, the remaining assets can be created or reused through deterministic selectors. Planner remains the critical live boundary, so the runtime must preserve fail-closed behavior instead of masking tenant permission gaps. When the runtime, contract, registry, and focused regression coverage all preserve those same selectors and boundaries, the composite action is truthful.
