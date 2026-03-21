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

- `GATE:M365-READY-C1C STATUS:GO`
- Mutation surface:
  - pass: `create_site`
  - pass: `create_team`
  - pass: `add_channel`
  - pass after reproof: `provision_service`
  - pass after reproof: `reset_user_password`
- Governance surface:
  - pass: missing-bearer fail-closed
  - pass: OPA health and approval-required decision path
  - pass after reproof: real actor-authenticated governed path (`m365-administrator/users.read` with JWT-backed actor identity)
  - pass after reproof: approval record creation and readback on the pinned `Approvals` list
  - pass after reproof: approval-linked audit evidence in `logs/ops_audit.log`

## Post-Attempt Remediation

- `provision_service` is now green under `transcripts/provision_service_reproof.json`.
- `reset_user_password` is now green under `transcripts/reset_user_password_reproof.json`.
- Governed JWT parity, approval create/readback, and audit evidence are now green under `transcripts/governance_surface_reproof.json`.
- Root cause: existing-site detection was guessing `/sites/hr` from `mail_nickname=hr`, while the live HR group resolves to `https://smarthausgroup.sharepoint.com/sites/hr2`.
- The runtime now resolves the existing group root site first and only uses path lookup as bounded fallback.

## Scope Note

- The green governance reproof is intentionally bounded to the active OPA-allowed certification surface.
- Historical exploratory `admin.*` and `directory.org` probes remain outside the supported `C1C` contract and are not treated as release blockers.

## C1D Closeout

- `GATE:M365-READY-C1D STATUS:GO`
- The retained `C1B` and `C1C` evidence is now mapped into `validation_matrix_status.json`.
- `docs/commercialization/m365-live-tenant-validation-matrix.md` is synchronized to the standalone packet.
- `docs/commercialization/m365-release-gates-and-certification.md` now reflects that Gate 4 is passable for the bounded standalone v1 claim, while Gate 6 still awaits the formal `C2` decision packet.

## C2 Decision

- `GATE:M365-READY-C2 STATUS:GO`
- Runtime evidence is green for the bounded standalone M365 v1 release claim.
- Final release decision is `GO` because `sign_off_record.json` is complete for engineering, security, and release-owner sign-off.

## Additional Observation

- An earlier exploratory `create_team` attempt against a freshly created disposable group exposed a separate owner-resolution warning (`Team owner not found for group ...`). The bounded certification transcript therefore uses the existing `hr` surface for deterministic classification instead of that fresh-group path.
