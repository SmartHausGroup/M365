# TAI Licensed Module Model (Plain-English Guide)

This document explains the commercial model in business language.

## What You Are Selling

You are selling **one product**: TAI.

Customers do not buy "five separate systems." They buy one core runtime, then add licensed modules.

Think of it like this:
- TAI is the platform.
- CAIO, MAIA, VFE, and M365 are licensed capabilities that plug into TAI.
- The customer turns capabilities on and off based on license and need.

## What the Customer Experience Should Feel Like

From the customer point of view, this should feel simple:

1. Install TAI.
2. Enter license key.
3. Enable the modules included in that license.
4. Use the capability immediately.

No manual cross-service wiring in day-to-day operations.

## Why This Is the Right Commercial Approach

This model is strong commercially because it supports:
- Clear packaging: Base platform + add-on modules.
- Clear upsell: Add MAIA, add VFE, add M365, etc.
- Clear operations: One control plane, one place to manage entitlements.
- Cleaner enterprise story: policy, audit, and governance remain centralized.

## How It Maps to What We Built

Today, the architecture supports this direction:
- TAI has module lifecycle and entitlement checks.
- CAIO, MAIA, VFE, and M365 now expose module contracts/capabilities.
- M365 keeps strict safety controls (auth context, mutation gate, idempotency, audit).

So the system is no longer "just APIs floating around." It is now a module-based platform pattern centered on TAI.

## What "Enabled" Means Operationally

A module being enabled means:
- TAI recognizes the capability.
- Entitlements allow it.
- Calls route through the capability contract.
- Governance/audit controls still apply.

If entitlement is missing, the module stays off.

## Standard Packaging Pattern

Recommended product packaging:
- Base TAI: core runtime, control plane, baseline chat/voice operations.
- Orchestration Pack: CAIO.
- Intent Pack: MAIA.
- Inference Pack: VFE.
- M365 Operations Pack: M365 connector/actions.

You can also bundle packs by market segment (SMB, Enterprise, Regulated, etc.).

## Expansion Rule for Other Repos

For each service family, keep the same standard:
- `core` repo: runtime implementation + internal docs.
- `sdk` repo: client SDK only.
- public repo: public-facing docs only.

That keeps commercial packaging clean and avoids mixing internal runtime code with customer-facing docs.

## Current Status (As of 2026-02-06)

The licensed modular runtime path has been implemented across the five repos:
- TAI Core
- CAIO Core
- MAIA
- VFE Core
- M365

M365 is now available as an embeddable connector module under the same entitlement-driven model.
