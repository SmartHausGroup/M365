# M365 Marketplace Bundle Packaging

This document defines the canonical marketplace bundle produced by this repository for the standalone UCP-facing M365 integration pack.

## Scope

- authoritative runtime surface: `src/ucp_m365_pack/`
- bundle payload includes:
  - `ucp_m365_pack/__init__.py`
  - `ucp_m365_pack/contracts.py`
  - `ucp_m365_pack/client.py`
  - `setup_schema.json`
  - `registry/agents.yaml`
- final distributable artifact: `dist/m365_pack/com.smarthaus.m365-1.0.0.ucp.tar.gz`

## Identity

- public marketplace pack id: `com.smarthaus.m365`
- host catalog pack id: `m365_pack`
- version: `1.0.0`
- distribution mode: `marketplace`
- entitlement SKU: `com.smarthaus.m365.enterprise`

The distinction between public marketplace pack id and host catalog pack id is intentional. The bundle follows the public reverse-domain pack manifest contract, while UCP’s current host catalog still routes the installed pack through the existing `m365_pack` catalog entry.

## Bundle Structure

The generated bundle contains:

- `manifest.json`
- `payload.tar.gz`
- `signatures/manifest.sig`
- `signatures/payload.sig`
- `evidence/conformance.json`
- `assets/README.md`

## Production Rule

The final production install model must treat this bundle artifact as the source of truth. UCP must not materialize the installed M365 pack from sibling-repo source copying once the marketplace bundle flow is active.

## Operator Truth

Marketplace is the discovery, review, install, and admission lane.

Integrations is the post-install, post-admission runtime lane.

The M365 pack should not appear as an active integration dashboard until the bundle has been reviewed, admitted, installed, and enabled in UCP.
