# Changelog

All notable changes to the SMARTHAUS Microsoft 365 Integration Pack are
documented here. Versions follow semantic versioning relative to the pack
manifest declared in `dist/m365_pack/manifest.json` and shipped under
`com.smarthaus.m365@<version>.ucp.tar.gz`.

## 1.2.0 — 2026-05-02

### Capability surface remediation (Tracks A + B + C)

- **Honest denial semantics.** `unknown_action` is now distinct from
  `mutation_fence`; callers can tell "I don't know that action" apart
  from "I refused to write." Status taxonomy extended with
  `tier_insufficient` and `not_yet_implemented`.
  Reference: `plan:m365-capability-pack-surface-remediation`,
  lemmas L100–L113.
- **Read-only Graph runtime registry: 11 → 36 actions.** Added
  SharePoint (sites / lists / list items / drives / drive children),
  Calendar (calendar list / get / availability, events list), Mail
  (list / message-get / attachments), Health & Reports (overview,
  issues, messages, users-active, email-activity, teams-activity,
  sharepoint-usage, onedrive-usage), Directory & Teams (domains,
  roles, teams get, channels list/get).
- **Auth tier hierarchy.** `read-only < standard < admin`. `auth_start`
  validates and persists tier in the keychain via `TokenStore`; tier
  survives runtime rebuild.
- **Capability inventory + preflight.** New `GET /v1/inventory` and
  `POST /v1/auth/preflight` endpoints partition advertised actions
  into `invokable / blocked_by_auth_mode / blocked_by_scopes` against
  the active session.
- **Planned-action short-circuit.** `ucp_m365_pack/client.py` now
  returns `coverage_status: planned` envelopes for advertised-but-
  unimplemented actions without an HTTP round-trip; aliased actions
  pass through to the runtime registry id.
- **Operator capability map.** `docs/m365_capability_map.md` (936
  lines) classifies every advertised action as
  `implemented / aliased / planned / deprecated`, mirrored into UCP
  via `scripts/sync_m365_capability_map.py`.
- **MCP tool docstring coverage markers.** Each `m365_*` tool's
  `Actions:` block now annotates per-action coverage status.

### Releases

- Marketplace artifact: `com.smarthaus.m365-1.2.0.ucp.tar.gz`
- Bundle SHA256: `8dc225173a978f3095dac06ace482c122c366fceeab35b83b5ab5bca84e7fb13`
- UCP pin: `M365_120_RELEASE_SPEC` in
  `src/ucp/runtime/release_artifacts.py`; alias
  `M365_RELEASE_SPEC = M365_120_RELEASE_SPEC`. Lock at
  `configs/marketplace/release_artifacts/m365-1.2.0.lock.json`.
- Release plan reference: `plan:m365-cps-trkB-p7-end-to-end-and-repackage:R4`.

### Live-tenant verification

- All Track B parent phases (B1..B6) recorded `live-pass` against the
  `smarthausgroup.com` tenant; consolidated diagnostic at
  `artifacts/diagnostics/m365_cps_trkB_full_coverage.json`. UCP GATE
  C0 integration test:
  `tests/integration/m365_cps_trkB_full_coverage.py`.

## 0.1.3 — 2026-04-15

- Standalone Microsoft Graph runtime initial public release. Read-only
  Graph action runtime; OAuth/app-only auth flows; secure token store;
  `/v1/auth/{start,check,status,clear}` lifecycle; UCP-facing client +
  contracts; packaging evidence.
