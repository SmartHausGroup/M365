# Plan: M365 standalone UCP pack surface

**Plan ID:** `plan:m365-ucp-standalone-pack-surface`
**Status:** ✅ Complete
**Date:** 2026-03-31
**Owner:** SMARTHAUS
**Execution plan reference:** `plan:m365-ucp-standalone-pack-surface:R1`
**North Star alignment:** `Operations/NORTHSTAR.md` — keep M365 service/runtime ownership in the M365 repo while giving UCP a truthful standalone first-party pack surface instead of an embedded copy.

## Objective

Create the standalone UCP-facing M365 pack surface in this repo so the sibling UCP repo can consume `m365_pack` from its owner repo and remove the old embedded local copy.

## Scope

### In scope

- create the formal M365 plan/prompt package for the standalone pack surface
- add a standalone `ucp_m365_pack` package in this repo
- port the UCP-facing pack contracts and client logic into this repo
- remove direct-import fallback from the live executor path
- add focused tests and docs for the standalone pack surface
- update `Operations/EXECUTION_PLAN.md`, `Operations/ACTION_LOG.md`, and `Operations/PROJECT_FILE_INDEX.md`

### Out of scope

- sibling UCP repo edits
- Microsoft tenant permission changes
- new Graph action-surface work

## Requirements

- **R1 — Formal plan/prompt package plus notebook-backed governance evidence**
- **R2 — Standalone contracts package**
- **R3 — Standalone service-mode client package**
- **R4 — Focused tests and documentation**
- **R5 — Clean governance closure and ship**

## Execution Stack

### T1 — Lock the governed package

Create the plan triplet, prompt pair, notebook evidence, and verification artifact.

### T2 — Add standalone contracts package

Create `src/ucp_m365_pack/contracts.py` and `src/ucp_m365_pack/__init__.py`.

### T3 — Add standalone client package

Create `src/ucp_m365_pack/client.py` and focused client tests with no direct-import live fallback.

### T4 — Document and validate authoritative ownership

Add the standalone pack doc and focused proof that this repo is now the authoritative owner of the UCP-facing pack surface.

### T5 — Close governance and ship cleanly

Update Operations trackers, verify clean git state, commit, and push.
