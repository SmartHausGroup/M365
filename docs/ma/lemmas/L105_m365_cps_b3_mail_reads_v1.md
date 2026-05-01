# L105 - M365 Capability Pack B3 Mail Reads v1

**Lemma id:** `L105_m365_cps_b3_mail_reads_v1`
**Plan reference:** `plan:m365-cps-trkB-p3-mail-reads:T2`
**Predecessor:** `L104_m365_cps_b2_calendar_reads_v1`

## Mission

Add mail read coverage: 3 new ActionSpec entries (`graph.mail.list`,
`graph.mail.message_get`, `graph.mail.attachments`) and 3 new aliases.

## Predicate

`MailReadsCovered = L_NEW_ENTRIES_REGISTERED ∧ L_ALIASES_RESOLVE ∧ L_NO_REGRESSION`

## Registry entries

- `graph.mail.list` → `/me/messages`, `Mail.Read`, delegated
- `graph.mail.message_get` → `/me/messages/{messageId}`, `Mail.Read`, delegated
- `graph.mail.attachments` → `/me/messages/{messageId}/attachments`, `Mail.Read`, delegated

## Aliases

- `mail.list` → `graph.mail.list`
- `mail.read` → `graph.mail.message_get`
- `mail.attachments` → `graph.mail.attachments`
- `mail.folders` → `graph.mail.health` (existing — operators called this in the original probe)
