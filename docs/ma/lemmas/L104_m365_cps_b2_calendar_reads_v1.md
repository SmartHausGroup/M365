# L104 - M365 Capability Pack B2 Calendar Reads v1

**Lemma id:** `L104_m365_cps_b2_calendar_reads_v1`
**Plan reference:** `plan:m365-cps-trkB-p2-calendar-reads:T2`
**Status:** Active
**Owner:** SMARTHAUS
**Module notebook:** `notebooks/m365/INV-M365-CPS-B2-calendar-reads-v1.ipynb`
**Predecessor:** `L103_m365_cps_b1_sharepoint_reads_v1`

## Mission

Add calendar read coverage: 4 new ActionSpec entries (`graph.calendar.list`,
`graph.calendar.get`, `graph.events.list`, `graph.calendar.availability`)
and 4 new aliases.

## Predicate

```
CalendarReadsCovered =
    L_NEW_ENTRIES_REGISTERED
  ∧ L_ALIASES_RESOLVE
  ∧ L_NO_REGRESSION
```

## L_NEW_ENTRIES_REGISTERED

Registry contains:
- `graph.calendar.list` → `/me/events`, scopes `Calendars.Read`, modes delegated
- `graph.calendar.get` → `/me/events/{eventId}`, scopes `Calendars.Read`, modes delegated
- `graph.events.list` → `/users/{userId}/events`, scopes `Calendars.Read`, modes app-only + pkce
- `graph.calendar.availability` → `/me/calendar/getSchedule`, scopes `Calendars.Read`, modes delegated

## L_ALIASES_RESOLVE

- `calendar.list` → `graph.calendar.list`
- `calendar.get` → `graph.calendar.get`
- `events.list` → `graph.events.list`
- `availability.check` → `graph.calendar.availability`
