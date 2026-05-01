# L107 - M365 Capability Pack B5 Directory & Teams Reads v1

**Lemma id:** `L107_m365_cps_b5_directory_teams_v1`
**Plan reference:** `plan:m365-cps-trkB-p5-directory-and-teams:T2`
**Predecessor:** `L106_m365_cps_b4_health_reports_v1`

## Mission

Add directory and teams read coverage: 5 new ActionSpec entries.

## Predicate

`DirectoryTeamsCovered = L_NEW_ENTRIES_REGISTERED ∧ L_ALIASES_RESOLVE ∧ L_NO_REGRESSION`

## Registry entries

- `graph.directory.domains` → `/domains`, `Domain.Read.All`
- `graph.directory.roles` → `/directoryRoles`, `RoleManagement.Read.Directory`
- `graph.teams.get` → `/teams/{teamId}`, `Team.ReadBasic.All`
- `graph.channels.list` → `/teams/{teamId}/channels`, `Channel.ReadBasic.All`
- `graph.channels.get` → `/teams/{teamId}/channels/{channelId}`, `Channel.ReadBasic.All`

## Aliases

- `directory.domains` → `graph.directory.domains`
- `directory.roles` → `graph.directory.roles`
- `teams.get` → `graph.teams.get`
- `channels.list` → `graph.channels.list`
- `channels.get` → `graph.channels.get`
