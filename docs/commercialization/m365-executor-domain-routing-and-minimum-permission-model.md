# M365 Executor-Domain Routing and Minimum-Permission Model

## Purpose

Replace the single giant executor target with a bounded executor-domain architecture.

## Decision

SMARTHAUS should use a small set of bounded executor domains, not one god-mode executor and not one app per persona.

## Recommended Domain Split

### Operator Identity App

- purpose: human Entra login only
- not the app-only Microsoft executor

### SharePoint / Files Executor

- approvals
- sites, lists, libraries
- document storage and file workflows

### Collaboration Executor

- Teams
- groups
- Planner
- channels

### Messaging / Calendar Executor

- mail
- calendar
- communications workflows

### Directory / Admin Executor

- users
- licenses
- directory administration

### Power Platform / Analytics Executor

- Power Automate
- Power Apps
- Power BI
- only when that surface is explicitly in scope

## Routing Rule

Every governed action must map deterministically to one executor domain.

`Executor(action) -> exactly_one_domain`

No action may fan out into ambiguous app selection.

## Permission Rule

Each executor domain must target the minimum viable permission envelope for its supported actions.

The product must avoid:

- tenant-wide god-mode permissions where narrower domain permissions are sufficient
- token bloat from irrelevant Microsoft Graph roles
- certification against a permission posture broader than the supported surface

## Long-Term SharePoint Rule

The approvals backend belongs to the SharePoint / Files executor.

This domain should be the first proof point for narrow routing, bounded permissions, and stable certification.
