# C1 Operator Checklist for Candidate `52ca494`

## Before Live Execution

- [ ] Export the exact standalone shell contract:
  - `UCP_ROOT=/Users/smarthaus/Projects/GitHub/UCP`
  - `UCP_TENANT=smarthaus`
  - `ALLOW_M365_MUTATIONS=true`
  - `ENABLE_AUDIT_LOGGING=true`
- [ ] Verify the selected tenant YAML resolves correctly through the tenant-config loader.
- [ ] Load one supported app-auth credential set for the tenant.
- [x] Use the certificate-backed executor contract at `/Users/smarthaus/.ucp/certs/smarthaus-m365-executor.pem`.
- [ ] Confirm the selected tenant contract carries the approval backend target for SMARTHAUS Operations (`https://smarthausgroup.sharepoint.com/sites/operations`, list `Approvals`) or set an explicit compatibility override.
- [ ] Confirm the approval-path probe can resolve the configured site and list without Graph `503` errors, or supply explicit site and list IDs to bypass discovery.
- [ ] Decide whether the run uses an external OPA service; if yes, set `OPA_URL`.
- Scope note: CAIO and instruction-API operator inputs are out of scope for standalone M365 `C1`.
- [ ] Confirm the certification window and rollback owner for controlled write-path checks.

## Live Execution Order

- [ ] Execute read-only supported-surface checks first.
- [ ] Execute controlled mutation checks only after read-only checks are green.
- [ ] Execute governance, approval, and audit checks during the same certification window.
- [ ] Save all live transcripts under `artifacts/certification/m365-v1-candidate-52ca494/transcripts/`.
- [ ] Update `evidence_index.json` with the produced live artifacts.

## Stop Conditions

- [ ] Stop immediately if tenant resolution fails.
- [ ] Stop immediately if app auth fails.
- [ ] Stop immediately if the exact standalone shell contract is not active.
- [ ] Stop immediately if approval-path checks cannot bind to the configured tenant-backed approval target.
- [ ] Stop immediately if any supported-surface live check returns ambiguous evidence.
