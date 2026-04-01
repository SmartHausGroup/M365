# User Manual — M365 Marketplace Pack

## Install Model

The supported UCP-facing M365 integration pack is distributed as a marketplace bundle, not as a source checkout.

Operator flow:

1. review the M365 pack in Marketplace
2. admit the pack for the tenant
3. install and enable it in UCP
4. confirm it appears in Integrations only after install plus admission

## Required Setup

The pack requires:

- M365 service URL
- caller JWT secret
- actor UPN

These are declared in the bundled `setup_schema.json` and are required for live UCP-to-M365 service execution.

## Runtime Model

The installed pack surface delegates live work to the dedicated M365 service runtime. UCP does not execute Microsoft Graph operations directly from the desktop app or from a sibling source checkout.
