# M365 Certification Rebase — Digital Employee Multi-Executor Model

## Purpose

Rebase standalone M365 certification so it proves the intended digital-employee and bounded-executor architecture instead of the current transitional single-executor posture.

## Root Cause

The current transitional executor app can authenticate and read non-SharePoint Graph surfaces, but SharePoint-backed Graph routes return `503` under app-only execution while delegated access succeeds. The executor token also carries an oversized role surface that exceeds the intended supported-surface boundary.

## Rebased Rule

`C1A` and downstream certification may not certify the product against the current single giant executor assumption.

Certification must instead target:

- digital employees as the delegation surface
- bounded executor domains
- minimal permission envelopes per domain
- deterministic persona-to-domain routing

## Consequence for the Plan

`C1A` must remain blocked until:

1. the digital-employee architecture is locked
2. the multi-executor implementation track is defined
3. the approval backend and certification path are retested under the corrected model

## Consequence for Release Claims

No enterprise readiness claim may imply:

- one executor app safely represents the full M365 capability universe
- generic agent terminology is the final operator model
- the current certificate-backed single executor is the final certification target
