# C1 Operator Checklist for Candidate `52ca494`

## Before Live Execution

- [x] Export the exact standalone shell contract:
  - `UCP_ROOT=/Users/smarthaus/Projects/GitHub/UCP`
  - `UCP_TENANT=smarthaus`
  - `ALLOW_M365_MUTATIONS=true`
  - `ENABLE_AUDIT_LOGGING=true`
- [x] Verify the selected tenant YAML resolves correctly through the tenant-config loader.
- [x] Use the certificate-backed SharePoint executor contract at `/Users/smarthaus/.ucp/certs/smarthaus-sharepoint-executor.pem`.
- [x] Confirm the selected tenant contract carries the approval backend target for SMARTHAUS M365 Operations (`https://smarthausgroup.sharepoint.com/sites/SMARTHAUSM365Operations`, list `Approvals`) with pinned `approvals_site_id` and `approvals_list_id`.
- [x] Confirm the approval-path probe returns `200` on the approvals list metadata and approvals list items routes through the bounded SharePoint executor.
- [x] Decide whether the run uses an external OPA service; if yes, set `OPA_URL`.
- Scope note: CAIO and instruction-API operator inputs are out of scope for standalone M365 `C1`.
- [x] Confirm the certification window and rollback owner for controlled write-path checks.

## Live Execution Order

- [x] Execute read-only supported-surface checks first.
- [x] Execute controlled mutation checks only after read-only checks are green.
- [x] Execute governance, approval, and audit checks during the same certification window.
- [x] Save all live transcripts under `artifacts/certification/m365-v1-candidate-52ca494/transcripts/`.
- [x] Update `evidence_index.json` with the produced live artifacts.

## Live Results

- `C1B`: `GO`
  - read-only supported-surface checks passed
- `C1C`: `GO`
  - mutation checks passed: `create_site`, `create_team`, `add_channel`, `provision_service`, `reset_user_password`
  - governance checks passed: missing-bearer fail-closed, real actor-authenticated JWT path on the bounded supported surface, approval create/readback, audit evidence retention
- `C1D`: `GO`
  - validation-matrix mapping and packet closeout are synchronized for the bounded standalone M365 v1 scope
- `C2`: `GO`
  - bounded standalone release packet is complete and required human engineering, security, and release-owner sign-off is recorded

## Stop Conditions

- [ ] Stop immediately if tenant resolution fails.
- [ ] Stop immediately if app auth fails.
- [ ] Stop immediately if the exact standalone shell contract is not active.
- [ ] Stop immediately if approval-path checks cannot bind to the configured tenant-backed approval target by the pinned `site_id` and `list_id`.
- [ ] Stop immediately if any supported-surface live check returns ambiguous evidence.
