# SMARTHAUS Microsoft 365 Integration Pack

This artifact contains the standalone Microsoft Graph runtime service, OAuth and app-only auth flows, secure token storage policy, health and readiness contracts, a bounded read-only Graph action runtime, the UCP-facing pack contracts, and packaging evidence.

Read-only Graph actions are the only mutating surface authorized for v1.
Microsoft Graph write actions require a separate mutation-governance plan.

Run `python -m m365_runtime` from the installed pack directory to launch.
