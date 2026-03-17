# M365 v1 Positioning and North Star Delta

**Status:** `P0B` complete
**Date:** 2026-03-17
**Plan refs:** `plan:m365-enterprise-commercialization-readiness:R6`, `plan:m365-enterprise-commercialization-readiness:P0B`

This document defines who the standalone SmartHaus M365 module v1 is for, who operates it, how it should be positioned, and how the repo North Star must be interpreted after the `P0A` supported-surface lock.

Deterministic decision rule for this repository state:

`NorthStarUpdateRequired = true` if the governing North Star implies a broader commercial v1 scope than `docs/commercialization/m365-v1-supported-surface.md`.

For the current repository state, that decision is `true`, so the North Star delta is required and applied in `Operations/NORTHSTAR.md`.

## Target Buyer

The primary buyer for standalone M365 v1 is the enterprise owner of Microsoft 365 operations, typically one of:

1. Head of IT
2. M365 platform owner
3. Identity and collaboration lead
4. Enterprise automation owner with direct responsibility for Microsoft 365 governance

The buying problem is not "replace Microsoft 365" or "buy a general AI workforce." The buying problem is narrower:

1. Reduce manual M365 administrative work in a governed way.
2. Add deterministic, policy-gated operational automation without introducing extra software sprawl.
3. Keep the control boundary native to Microsoft 365 and existing enterprise governance.

The standalone buyer is not:

1. A department-level business end user.
2. A general productivity buyer looking for broad AI agent coverage.
3. A buyer expecting full Microsoft Graph or full M365 admin coverage on day 1.

## Target Operator

The expected operator for standalone M365 v1 is the customer's internal M365 administration or platform operations team.

Operator responsibilities:

1. Configure tenant access and credentials.
2. Control mutation gates and approval boundaries.
3. Review audit trails and policy outcomes.
4. Decide when supported actions are enabled for production use.

SmartHaus is not the day-to-day operator. The intended model remains self-service and maintenance-only from the SmartHaus side after setup and support handoff.

The standalone operator is not:

1. A general employee end user.
2. A line-of-business department without M365 administrative ownership.
3. A fully hands-off autonomous system with no human governance.

## Positioning

Standalone M365 v1 should be positioned as a narrow, deterministic M365 operations module.

Positioning statement:

SmartHaus M365 v1 is a governed Microsoft 365 operations module that exposes exactly 9 supported actions across identity, Teams, and SharePoint, with policy-gated mutations, auditability, and native M365 alignment.

This module is:

1. A narrow enterprise operations capability.
2. A commercialization-ready entry point for governed M365 automation.
3. A fail-closed product boundary tied to current repository evidence.

This module is not:

1. The full 39-agent SmartHaus AI Workforce product vision.
2. A general-purpose Graph super-connector.
3. A claim of complete M365 operational coverage.

## Deployment Model

The module should be understandable and sellable as a standalone M365 capability, but operationally it remains compatible with the TAI licensed-module pattern.

Deployment model rules:

1. A buyer can review, pilot, and purchase the M365 capability as its own bounded module.
2. The module can still be packaged inside the broader TAI runtime and entitlement model described in `docs/TAI_LICENSED_MODULE_MODEL.md`.
3. Customer operations remain self-service after setup, with SmartHaus providing maintenance, updates, and governed support rather than daily operation.

Commercially, the right message is:

1. Standalone module for narrow M365 operations value.
2. Compatible with the larger TAI module model if the customer expands later.

## North Star Delta

Decision: `NorthStarUpdateRequired = true`

Reason:

1. `Operations/NORTHSTAR.md` still presents this repo primarily as the broad 39-agent M365 AI Workforce.
2. `P0A` locked the standalone commercial v1 surface to exactly 9 actions.
3. Leaving North Star unchanged would create a governing contradiction between repo vision and current sellable scope.

Required North Star changes:

1. Add a commercialization-scope clarification that points standalone M365 claims to the docs under `docs/commercialization/`.
2. Preserve the broader workforce vision, but state explicitly that it is not the launch-scope authority for standalone M365 v1.
3. Reframe the existing "Authorized Capabilities (v1)" section as broader workforce vision rather than standalone module scope.

Applied result:

1. `Operations/NORTHSTAR.md` now distinguishes repo-wide workforce ambition from standalone M365 commercialization.
2. The standalone product claim remains bounded to the `P0A` supported-surface document.
3. Future commercialization phases can build on this narrower buyer/operator frame without revisiting the full product definition unless the supported surface expands.
