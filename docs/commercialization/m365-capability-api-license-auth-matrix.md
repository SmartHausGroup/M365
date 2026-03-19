# M365 Capability / API / License / Auth Matrix

## Purpose

Define what “anything in M365” means for the SMARTHAUS workforce product and separate licensing, API surface, and auth requirements.

## Core Rule

Licensed does not mean directly automatable, and automatable does not mean app-only.

Each capability must be mapped across:

- workload
- API surface
- required license or product dependency
- auth posture
- executor domain

## Workload Classes

### SharePoint / OneDrive / Files

- primary APIs: Microsoft Graph, SharePoint-native APIs where needed
- typical auth: app-only executor
- notes: approvals, files, libraries, lists, and document storage belong here

### Teams / Groups / Planner / Collaboration

- primary APIs: Microsoft Graph
- typical auth: app-only executor with bounded collaboration scope
- notes: team provisioning, channels, group membership, planner surfaces

### Mail / Calendar / Communications

- primary APIs: Microsoft Graph
- typical auth: app-only for service actions, delegated where user-context fidelity is required

### Directory / Identity / Admin

- primary APIs: Microsoft Graph plus admin surfaces
- typical auth: tightly bounded app-only executor with the narrowest possible privileged roles

### Power Platform / BI

- primary APIs: mixed, not purely the same Graph story
- typical auth: separate executor domain when this surface is truly in scope

### Documents / Spreadsheets / Presentations

- primary APIs: file storage plus workload-specific automation patterns
- notes:
  - Excel is relatively automatable
  - Word and PowerPoint are more template and workflow oriented than one uniform API surface

## Architectural Consequence

The platform must model capability routing explicitly instead of assuming one universal executor can safely or reliably perform every M365 action.

## Certification Consequence

Certification must prove:

- which capabilities are in scope
- which auth mode each capability uses
- which executor domain handles that capability
- which capabilities remain partial, delegated-only, or out of scope
