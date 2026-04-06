# M365 Direct Full Surface Certification

## Status

`F4` is complete. The direct full-surface certification program now closes with a truthful reduced support matrix for the repo-direct instruction surface: `64` live-green direct actions and `91` fenced direct actions, plus supplemental approval and actor-tier governance evidence at the ops-adapter boundary.

## Purpose

This initiative exists because the repo is beyond partial smoke testing now. The user requirement is stronger: the direct M365 surface this repo claims to support must be locked, enabled, and tested truthfully enough that Claude or Codex can be asked to perform supported Microsoft 365 work with real confidence.

## F0 Universe Lock

The notebook-backed `F0` baseline is:

- Notebook: `notebooks/m365/INV-M365-CH-direct-full-surface-certification-universe-lock-v1.ipynb`
- Machine-readable artifact: `artifacts/diagnostics/m365_direct_full_surface_certification.json`

The locked baseline counts are:

- `59` agents
- `155` direct instruction actions
- `184` persona-facing allowed-action aliases
- `340` capability-registry actions
- `146` crosswalked canonical actions when the v2 expansion registries and cross-workload recipe catalog are combined

## What F0 Proved

The repo does not yet expose one single direct-certification surface. It currently has multiple overlapping action vocabularies:

- direct instruction actions in `src/provisioning_api/routers/m365.py`
- persona-facing aliases in `registry/agents.yaml`
- capability-registry actions in `registry/capability_registry.yaml`
- canonicalized v2 action mappings in the `*_expansion_v2.yaml` files plus `registry/cross_workload_automation_recipes_v2.yaml`

That means full certification must normalize these surfaces before any claim of “everything works” can be truthful.

## Current F0 Blockers

`F0` identified two blocker classes that matter for the rest of the program.

### 1. Legacy direct instruction actions outside the v2 crosswalk

The direct instruction surface still claims nine actions that are not yet represented in the expansion-backed canonical universe:

- `list_users`
- `get_user`
- `reset_user_password`
- `list_teams`
- `list_sites`
- `create_site`
- `create_team`
- `add_channel`
- `provision_service`

These actions are real runtime paths, but they still sit outside the current v2 expansion-backed normalization layer.

### 2. Persona-facing actions that are not real M365 execution yet

`F0` also proved that a material part of the persona-facing surface is not ready for honest full certification.

- `125` persona aliases are outside the current direct crosswalk.
- `41` actions across `8` agents are still implemented as legacy stub behavior in `src/ops_adapter/actions.py`.

The current legacy-stub agent set is:

- `it-operations-manager`
- `website-operations-specialist`
- `project-coordination-agent`
- `client-relationship-agent`
- `compliance-monitoring-agent`
- `recruitment-assistance-agent`
- `financial-operations-agent`
- `knowledge-management-agent`

These actions cannot be counted as “tested M365 functionality” until they are either implemented against real M365 behavior or explicitly fenced out of the certified surface.

## What F1 Had To Do

`F1` is now responsible for the enablement and truth decision boundary:

- identify which remaining failures are pure environment/tenant enablement blockers
- identify which remaining claimed actions are actually implementation-truth blockers
- remove the blockers that can be fixed safely inside scope
- reduce the claimed certified surface anywhere a truthful fix is not available yet

## Current Decision

The direct runtime is no longer the primary blocker. The program now moves forward with a clearer truth:

- some remaining failures are environment or tenant enablement blockers
- some remaining failures are surface-truth blockers caused by legacy action topology and stubbed behavior

Full certification can now proceed on a real baseline instead of on mixed assumptions.

## F1 Enablement Results

`F1` closed the blocker class that had kept the repaired direct runtime from being broadly testable.

### What changed

- collaboration executor Graph permissions were expanded to cover direct mail and calendar reads
- directory executor Graph permissions were expanded to cover reports and service health
- local Power Platform admin modules were installed and verified
- the `powerplatform` executor app was registered as a Power Platform management application through the documented tenant-admin operator path
- the Power Apps / Power Automate clients were hardened so PowerShell warning preambles no longer cause false parser failures

### What is now proven live from the direct repo runtime

- mail:
  - `list_messages` succeeds for the configured tenant user path
- calendar:
  - `list_events` succeeds
  - `get_schedule` succeeds when app-only input includes explicit `userId`
- service health:
  - the governed service-health overview path succeeds with the enabled directory executor roles
- Power Apps:
  - `list_powerapp_environments` succeeds through the `powerplatform` executor
- Power Automate:
  - `list_flows_admin` succeeds through the `powerplatform` executor and returns a truthful zero-flow result when no flows are present

### What F1 did not solve

`F1` did not certify the whole claimed surface. It removed the direct enablement blockers. The remaining work is now certification work:

- read-path certification across the supported surface
- mutation and approval-path certification
- truthful surface reduction where legacy stub behavior or crosswalk gaps still prevent honest certification

## F2 Read-Path Certification Results

`F2` certified the implemented non-mutating direct surface action by action and closed the phase with a truthful split between green reads and fenced reads.

### Locked F2 read surface

The `F2` read-path matrix used the implemented non-mutating capability-registry surface:

- `91` implemented non-mutating direct actions
- `45` certified green against the live direct runtime
- `46` fenced from the currently certified read surface

### Repo-local defects repaired during F2

Two real repo-local defects were exposed and fixed during `F2`:

- `GraphClient.list_directory_roles` stopped sending unsupported `$top` to `/directoryRoles`, which unblocked both `list_directory_roles` and `list_directory_role_members`
- `PowerAppsClient` now treats warning-only PowerShell stdout as empty data, which unblocked `list_powerapp_environment_role_assignments`

### Certified green read families

The following actions are now certified green on the direct repo runtime:

- identity:
  - `list_users`
  - `get_user`
  - `list_groups`
  - `get_group`
  - `list_group_members`
  - `list_directory_roles`
  - `list_directory_role_members`
  - `list_domains`
  - `get_organization`
  - `list_applications`
  - `get_application`
  - `list_service_principals`
- Teams / SharePoint:
  - `list_teams`
  - `get_team`
  - `list_channels`
  - `list_sites`
  - `get_site`
  - `list_site_lists`
  - `get_list`
  - `list_list_items`
- files:
  - `list_drives`
- mail / calendar / contacts:
  - `list_messages`
  - `get_message`
  - `list_mail_folders`
  - `get_mailbox_settings`
  - `list_events`
  - `get_event`
  - `get_schedule`
  - `list_contacts`
  - `get_contact`
  - `list_contact_folders`
- reports:
  - `get_report`
  - `get_usage_reports`
  - `get_activity_reports`
  - `list_powerbi_workspaces`
- Power Platform admin:
  - `list_powerapp_environments`
  - `get_powerapp_environment`
  - `list_powerapp_environment_role_assignments`
  - `list_powerapps_admin`
  - `get_powerapp_admin`
  - `list_powerapp_role_assignments`
  - `list_flows_admin`
  - `list_http_flows`
- provisioning:
  - `list_automation_recipes`
  - `get_automation_recipe`

### Fenced read families

The following actions are not part of the currently certified direct read surface and must not be implied to work until their blocker class is removed.

- files with no live sample:
  - `get_drive`
  - `list_drive_items`
  - `get_drive_item`
  - reason: the governed site probe returned `0` drives, so dependent drive reads could not be certified truthfully
- Planner:
  - `list_plans`
  - `list_plan_buckets`
  - reason: the live group-plan probe returns Graph `403` (`You do not have the required permissions to access this item.`)
- approvals:
  - `get_approval_solution`
  - `list_approval_items`
  - `get_approval_item`
  - `list_approval_item_requests`
  - reason: the current approvals app surface requires delegated or hybrid auth mode
- Power Platform flow-specific reads with no live sample:
  - `get_flow_admin`
  - `list_flow_owners`
  - `list_flow_runs`
  - reason: the certified environment currently returns `0` admin-visible flows
- external connections:
  - `list_external_connections`
  - `get_external_connection`
  - `get_external_item`
  - reason: the live external-connections probe returns Graph `401 UnknownError`
- devices:
  - `list_devices`
  - `get_device`
  - `list_device_compliance_summaries`
  - reason: the current executor token is missing the required Intune application roles
- identity security:
  - `list_conditional_access_policies`
  - `get_conditional_access_policy`
  - `list_named_locations`
  - `list_risk_detections`
  - reason: the current token is missing the required Conditional Access / Identity Protection scopes
- security:
  - `list_security_alerts`
  - `get_security_alert`
  - `list_security_incidents`
  - `get_security_incident`
  - `list_secure_scores`
  - `get_secure_score_profile`
  - reason: the current tenant and token state is not provisioned for these Microsoft security surfaces, and there is no discoverable secure-score-profile sample in the claimed read surface
- access reviews:
  - `list_access_reviews`
  - `get_access_review`
  - `list_access_review_decisions`
  - reason: the governed live probe remained in the Graph retry/backoff path and did not resolve within the probe window
- eDiscovery compliance:
  - `list_ediscovery_cases`
  - `get_ediscovery_case`
  - `list_ediscovery_case_searches`
  - `get_ediscovery_case_search`
  - `list_ediscovery_case_custodians`
  - `list_ediscovery_case_legal_holds`
  - reason: the governed live probe remained in the Graph retry/backoff path and did not resolve within the probe window
- Power BI reads with no live sample:
  - `get_powerbi_workspace`
  - `list_powerbi_datasets`
  - `get_powerbi_dataset`
  - `list_powerbi_dataset_refreshes`
  - `list_powerbi_reports`
  - `get_powerbi_report`
  - `list_powerbi_dashboards`
  - `get_powerbi_dashboard`
  - reason: the certified tenant probe returned `0` Power BI workspaces, so dependent reads could not be certified truthfully
- misclassified read claim:
  - `refresh_powerbi_dataset`
  - reason: this is a mutating action and is explicitly fenced out of `F2` read certification

### F2 closeout

`F2` is green at the phase level because the read surface is now truthfully split between:

- certified live reads that actually work from this repo version
- fenced reads that still require permission changes, delegated auth, live sample objects, or a future retry-path investigation

## F3 Mutation / Approval Certification Results

`F3` closed the bounded live mutation and approval certification window for the direct repo runtime. The phase goal was not to force every high-impact write to execute live. The goal was to prove the truthful split between:

- low-risk direct mutations that really execute
- high-impact writes that correctly stop at governed approval creation
- fenced write families that still hit external permission blockers

### Certified green live mutation families

The following low-risk direct write actions are now certified green on the live repo runtime:

- mail / calendar / contacts:
  - `send_mail`
  - `move_message`
  - `delete_message`
  - `update_mailbox_settings`
  - `create_event`
  - `update_event`
  - `delete_event`
  - `create_contact`
  - `update_contact`
  - `delete_contact`
- SharePoint / files / Office generation:
  - `create_folder`
  - `upload_file`
  - `create_document`
  - `update_document`
  - `create_workbook`
  - `update_workbook`
  - `create_presentation`
  - `update_presentation`
  - `create_list_item`

### Certified green approval and actor-tier boundaries

The governed runtime boundaries are now also certified green:

- actor-tier deny:
  - a `standard_user` actor is denied on `users.disable` with a truthful `tier_blocked` response before approval or execution
- approval-required boundary:
  - `sites.provision` returns `pending_approval` and persists a real approval record in the approvals store
  - `ca.policy_create` returns `pending_approval` and persists a real approval record in the approvals store

This means the direct runtime now proves the two critical governance guarantees required for high-impact writes:

- low-tier actors do not silently escalate
- high-impact writes stop at approval creation instead of mutating live tenant state

### Fenced mutation families

The following write family is still fenced out of the certified live mutation surface:

- Planner:
  - `create_plan`
  - `create_plan_bucket`
  - `create_plan_task`
  - reason: the live team/group probe still returns Graph `403` (`You do not have the required permissions to access this item.`), so the Planner write family cannot be certified truthfully in the current tenant state

### What F3 did not require

`F3` did not require live execution of destructive high-impact writes after approval. Those actions were certified at the governed boundary instead:

- the runtime reaches the correct pending-approval state
- the approval record persists with actor, tier, persona, executor, and risk metadata
- no mutation occurs before approval

### F3 closeout

`F3` is green at the phase level because the bounded mutation / approval slices are now truthfully split between:

- live low-risk writes that execute successfully from this repo version
- governed high-impact writes that correctly stop at `pending_approval`
- fenced Planner writes that still fail for an external tenant permission reason

No repo-local runtime defect required extraction during `F3`. The initial mail follow-up failures were probe-input issues, not code defects: mailbox settings needed a writable payload shape, and message deletion needed the moved message identifier returned by `move_message`.

## F4 Final Support Matrix

`F4` closes the initiative by collapsing the phase evidence into one truthful direct support matrix.

### Final direct instruction totals

Across the repo-direct instruction surface in `src/provisioning_api/routers/m365.py`:

- `155` total direct instruction actions claimed
- `64` certified live-green direct actions
- `91` fenced direct actions

The certified live-green total is the sum of:

- `45` certified read actions from `F2`
- `19` certified low-risk write actions from `F3`

The fenced total is the sum of:

- `46` fenced read actions from `F2`
- `3` fenced Planner write actions from `F3`
- `42` additional direct write actions now explicitly reduced out of the certified surface in `F4`

### Certified live-green direct surface

The final certified direct surface is:

- reads:
  - all `45` actions already listed in the `F2` green matrix
- writes:
  - all `19` actions already listed in the `F3` live-green mutation matrix

### Supplemental governance evidence

The direct instruction totals above do not count the ops-adapter governance proofs, because those use the persona/action alias layer rather than the direct instruction action names. They still matter and are part of the final closeout evidence:

- `standard_user` deny proof:
  - `users.disable`
- `pending_approval` proof:
  - `sites.provision`
  - `ca.policy_create`

These proofs certify that the governed runtime denies low-tier actors and persists real approval records before high-impact execution.

### Final fenced direct surface

The final fenced direct surface includes all `46` read actions already fenced in `F2`, the `3` Planner mutations fenced in `F3`, and the following `42` additional direct write actions that remain outside the certified direct surface.

- workspace and admin writes requiring dedicated post-approval live execution evidence:
  - `add_channel`
  - `create_channel`
  - `create_site`
  - `create_team`
  - `provision_service`
  - `create_user`
  - `update_user`
  - `disable_user`
  - `create_group`
  - `add_group_member`
  - `remove_group_member`
  - `assign_user_license`
  - `update_application`
  - `reset_user_password`
  - reason: these are high-impact or destructive admin/workspace mutations, and this program only certified the governed approval boundary for that class rather than live post-approval execution
- approvals mutations:
  - `create_approval_item`
  - `respond_to_approval_item`
  - reason: the approvals surface still requires delegated or hybrid auth mode
- Power Platform write mutations without live certification evidence:
  - `set_flow_owner_role`
  - `remove_flow_owner_role`
  - `enable_flow`
  - `disable_flow`
  - `delete_flow`
  - `restore_flow`
  - `invoke_flow_callback`
  - `set_powerapp_owner`
  - `remove_powerapp_role_assignment`
  - `delete_powerapp`
  - `set_powerapp_environment_role_assignment`
  - `remove_powerapp_environment_role_assignment`
  - reason: `F1` and `F2` proved the Power Platform read/admin boundary, but this initiative did not gather bounded live write evidence for these mutation paths
- access review mutations:
  - `create_access_review`
  - `record_access_review_decision`
  - reason: the underlying access-review surface remained in the Graph retry/backoff path during certification
- external connection and external item mutations:
  - `create_external_connection`
  - `register_external_connection_schema`
  - `upsert_external_item`
  - `create_external_group`
  - `add_external_group_member`
  - reason: the live external-connections surface returns Graph `401 UnknownError` and is not provisioned truthfully for certification
- identity-security mutations:
  - `create_conditional_access_policy`
  - `update_conditional_access_policy`
  - `delete_conditional_access_policy`
  - reason: the underlying identity-security execution surface still lacks the required scopes for truthful direct execution; only the approval boundary was certified
- device and security mutations:
  - `execute_device_action`
  - `update_security_incident`
  - reason: the device and security execution surfaces are not provisioned in the current tenant/token state
- eDiscovery mutations:
  - `create_ediscovery_case`
  - `create_ediscovery_case_search`
  - reason: the underlying eDiscovery surface remained in the Graph retry/backoff path during certification

### What this initiative did and did not certify

This initiative certifies the repo-direct instruction surface only after truthful reduction. It does not certify the full persona-alias layer.

The remaining persona-alias truth from `F0` still matters:

- `125` persona-facing aliases remain outside the current direct crosswalk
- `41` actions across `8` agents remain legacy stub behavior in `src/ops_adapter/actions.py`

Those surfaces are not part of the certified direct support matrix and must not be implied to work as real M365 execution.

### Final closeout

`F4` is green because the direct surface is now closed truthfully:

- the direct instruction surface is fully classified
- every claimed direct action is either certified live-green or explicitly fenced with a reason
- the runtime’s approval and actor-tier boundaries have real evidence
- no repo-local runtime defect remains open inside this initiative

The direct full-surface certification initiative is complete. Any future widening of the fenced surface requires a new governed initiative.
