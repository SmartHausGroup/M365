# L106 - M365 Capability Pack B4 Service Health & Reports v1

**Lemma id:** `L106_m365_cps_b4_health_reports_v1`
**Plan reference:** `plan:m365-cps-trkB-p4-health-and-reports:T2`
**Predecessor:** `L105_m365_cps_b3_mail_reads_v1`

## Mission

Add service health and reports coverage: 7 new ActionSpec entries
covering modern serviceAnnouncement endpoints and 5 standard reports
(period D7).

## Predicate

`HealthReportsCovered = L_NEW_ENTRIES_REGISTERED ∧ L_ALIASES_RESOLVE ∧ L_NO_REGRESSION`

## Registry entries

- `graph.health.overview` → `/admin/serviceAnnouncement/healthOverviews`
- `graph.health.issues` → `/admin/serviceAnnouncement/issues`
- `graph.health.messages` → `/admin/serviceAnnouncement/messages`
- `graph.reports.users_active` → `/reports/getOffice365ActiveUserCounts(period='D7')`
- `graph.reports.email_activity` → `/reports/getEmailActivityCounts(period='D7')`
- `graph.reports.teams_activity` → `/reports/getTeamsUserActivityCounts(period='D7')`
- `graph.reports.sharepoint_usage` → `/reports/getSharePointSiteUsageDetail(period='D7')`
- `graph.reports.onedrive_usage` → `/reports/getOneDriveUsageAccountDetail(period='D7')`

All app-only (no delegated) since they are tenant-wide admin reads.

## Aliases

- `health.overview` → `graph.health.overview`
- `health.issues` → `graph.health.issues`
- `health.messages` → `graph.health.messages`
- `reports.users_active` → `graph.reports.users_active`
- `reports.email_activity` → `graph.reports.email_activity`
- `reports.teams_activity` → `graph.reports.teams_activity`
- `reports.sharepoint_usage` → `graph.reports.sharepoint_usage`
- `reports.onedrive_usage` → `graph.reports.onedrive_usage`
