# C1 Operator Checklist for Candidate `52ca494`

## Before Live Execution

- [ ] Select the non-production tenant by setting `UCP_TENANT`.
- [ ] Verify the selected tenant YAML resolves correctly through the tenant-config loader.
- [ ] Load one supported app-auth credential set for the tenant.
- [ ] Prefer certificate auth; use client secret only if the tenant cannot yet support certificate auth.
- [ ] Enable `ALLOW_M365_MUTATIONS=true` for the approved test window.
- [ ] Enable `ENABLE_AUDIT_LOGGING=true`.
- [ ] Provide approval storage configuration with either `APPROVALS_SITE_ID` or `APPROVALS_SITE_URL`.
- [ ] Decide whether the run uses an external OPA service; if yes, set `OPA_URL`.
- [ ] Decide whether the CAIO instruction API is in scope; if yes, set `CAIO_API_KEY` and `BASE_URL`.
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
- [ ] Stop immediately if mutation gating or audit logging is not active.
- [ ] Stop immediately if approval-path checks cannot bind to configured approval storage.
- [ ] Stop immediately if any supported-surface live check returns ambiguous evidence.
