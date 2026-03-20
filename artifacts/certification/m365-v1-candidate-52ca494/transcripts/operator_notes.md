# C1B / C1C Operator Notes for Candidate `52ca494`

## Exact Live Shell Contract

```bash
export UCP_ROOT=/Users/smarthaus/Projects/GitHub/UCP
export UCP_TENANT=smarthaus
export ALLOW_M365_MUTATIONS=true
export ENABLE_AUDIT_LOGGING=true
```

## C1B Result

- `GATE:M365-READY-C1B STATUS:GO`
- Read-only supported-surface checks passed through `m365.module.entrypoint:M365ConnectorModule`.
- Verified live rows:
  - `list_users`
  - `get_user`
  - `list_teams`
  - `list_sites`

## C1C Result

- `GATE:M365-READY-C1C STATUS:NO-GO`
- Mutation surface:
  - pass: `create_site`
  - pass: `create_team`
  - pass: `add_channel`
  - fail: `provision_service`
  - fail: `reset_user_password`
- Governance surface:
  - pass: missing-bearer fail-closed
  - pass: OPA health and approval-required decision path
  - fail: real actor-authenticated governed path (`401 invalid_token:Signature verification failed`)
  - fail: approval record creation compatibility probe (`400` on SharePoint-backed list-item create)
  - blocked: approval-linked audit evidence

## Live Blockers

1. `provision_service` fails because existing-site detection does not match the live HR service-site shape.
2. `reset_user_password` fails because the bounded directory executor lacks the required privilege.
3. The current JWT validation contract does not accept the delegated Azure CLI bearer token used for the real-actor governed-path probe.
4. Approval record creation still fails with Graph HTTP `400` when writing to the pinned `Approvals` list, so approval and audit evidence is incomplete.

## Additional Observation

- An earlier exploratory `create_team` attempt against a freshly created disposable group exposed a separate owner-resolution warning (`Team owner not found for group ...`). The bounded certification transcript therefore uses the existing `hr` surface for deterministic classification instead of that fresh-group path.
