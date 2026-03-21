# Codex Profile for SmartHaus M365 AI Workforce by SMARTHAUS

- **Repository:** LocalHelp
- **Primary Languages:** TypeScript/JavaScript (Node.js), Swift (iOS), Python (notebooks/scripts)
- **Primary Runtime(s):** Node.js 18+, iOS 17+, Python 3.14 (preferred), 3.13, or 3.12 (for notebooks)
- **Owner / Point of Contact:** SMARTHAUS
- **Status:** active

**Maintenance Note:** This document reflects the repository structure and practices as of 2025-01-06. Paths, commands, and organizational patterns are authoritative; specific counts may change over time. When in doubt, verify current state by inspecting the repository.

---

## Purpose

SmartHaus M365 AI Workforce by SMARTHAUS is a hyper-local neighbor-to-neighbor help marketplace that connects people who need small home tasks done with people who have the time and ability to do them.

**Key responsibilities:**

- Hyper-local gig marketplace (iOS-first, web secondary)
- Simple, safe task scope (no permits, no licensed work)
- Self-service platform (SMARTHAUS maintenance-only)
- Service-Oriented Architecture (SOA) with Firebase backend
- App-first development priority

**What this repo is NOT responsible for:**

- TAI code (lives in TAI repository)
- Other SMARTHAUS products (separate repositories)

**Normative design:** `Operations/NORTHSTAR.md` is the source of truth that guides all code.

---

## Source of Truth Hierarchy

Codex MUST treat this order as the authority for behavior:

1. **Specs / Design Docs**
   - Location(s): `Operations/NORTHSTAR.md` (normative), `docs/architecture/`, `docs/design/`
   - **MANDATORY:** All code must align with North Star

2. **Math / Algorithms (MA Process for Matching/Pricing) - v2+ ONLY**
   - Location(s): `notebooks/algorithms/` or `notebooks/math/` (v2+ only), `docs/algorithms/` (if needed)
   - **v1 Scope Gate:** MA process is PROHIBITED in v1. v1 matching is location + category filtering only (see `Operations/NORTHSTAR.md` → "Authorized Capabilities (v1)" → "Explicitly Unauthorized in v1").
   - **v2+ Scope:** The Mathematical Autopsy (MA) process applies to all **new or modified** matching algorithms, pricing models, or recommendation engines (v2+ only)
   - **Process:** For v2+ algorithm changes, Phases 1-5 must complete before promoting code to staging/main
   - **Notebook-First:** v2+ algorithm code is written in notebooks first, then extracted to codebase (see `.cursor/rules/notebook-first-mandatory.mdc`)

3. **Notebooks**
   - Location(s): `notebooks/` (math, analytics, diagnostics)
   - **MANDATORY:** Implementation notebooks MUST NOT import from codebase (`from services.`, `from apps.`, etc.)
   - **Exception:** Verification notebooks may import from codebase to validate extracted code

4. **Code**
   - Location(s): `apps/` (iOS, web), `services/` (backend services), `shared/` (shared libraries)
   - **MANDATORY:** Code extracted from notebooks (for algorithms) or written directly (for non-algorithmic code)

5. **Tests**
   - Location(s): `tests/` (unit, integration, e2e)
   - **MANDATORY:** Tests must validate real implementations, not mocks

6. **Configuration**
   - Location(s): `infrastructure/` (Firebase, integrations), `.env` (environment variables)
   - **MANDATORY:** Never commit secrets; use `.env` and `.env.example`

---

## Project Structure

```
LocalHelp/
├── apps/                          # Client Applications
│   ├── ios/                       # Native iOS App (SwiftUI) - PRIMARY
│   └── web/                       # Web Landing Page (Next.js) - SECONDARY
│
├── services/                      # Backend Services (SOA)
│   ├── api-gateway/              # API Gateway (Vercel Edge Functions)
│   ├── user-service/             # User Management
│   ├── request-service/          # Request/Job Management
│   ├── matching-service/          # Job Matching
│   ├── messaging-service/         # In-App Messaging
│   ├── payment-service/           # Payment Processing (v2+)
│   ├── notification-service/      # Push/SMS/Email Notifications
│   ├── moderation-service/        # Automated Moderation
│   └── analytics-service/         # Analytics & Tracking
│
├── shared/                        # Shared Libraries & Utilities
│   ├── types/                     # TypeScript type definitions
│   ├── utils/                     # Shared utilities
│   ├── config/                    # Shared configuration
│   └── models/                    # Shared data models
│
├── infrastructure/                # Infrastructure Configuration
│   ├── firebase/                  # Firebase configuration
│   ├── integrations/              # Third-party integrations
│   └── monitoring/                # Monitoring & observability
│
├── notebooks/                     # Jupyter Notebooks (MA Process)
│   ├── math/                      # Mathematical validation (matching, pricing)
│   ├── analytics/                 # Data analysis
│   └── diagnostics/               # Diagnostic notebooks
│
├── docs/                          # Documentation
├── scripts/                       # Utility scripts
├── tests/                         # Integration & E2E tests
│
├── Operations/                    # Project Operations
│   ├── NORTHSTAR.md              # North Star (source of truth)
│   ├── EXECUTION_PLAN.md         # Execution plan
│   ├── ACTION_LOG.md             # Action log
│   └── PLAN_STATUS.md            # Plan status
│
└── Financial/                     # Financial docs
    └── FINANCIAL_PLAN.md
```

---

## Key Commands

**Development:**

- `make dev-setup` - Complete development environment setup (Node.js + Python)
- `make dev-web` - Start web app (Next.js)
- `make dev-ios` - Open iOS app in Xcode
- `make dev-services` - Start all backend services

**Quality:**

- `make lint` - Run all linting
- `make test` - Run tests
- `make quality-gate` - Full quality check (lint + test + type-check)
- `make type-check` - TypeScript type checking

**Deployment:**

- `make deploy-web` - Deploy web app to Vercel
- `make deploy-firebase` - Deploy Firebase configuration

---

## Environment Variables

Key environment variables (see `.env.example` for complete list):

- `FIREBASE_PROJECT_ID` - Firebase project ID
- `FIREBASE_API_KEY` - Firebase API key
- `HUBSPOT_API_KEY` - HubSpot API key
- `STRIPE_SECRET_KEY` - Stripe secret key (v2+)
- `TWILIO_ACCOUNT_SID` - Twilio account SID
- `SENDGRID_API_KEY` - SendGrid API key
- `MIXPANEL_TOKEN` - Mixpanel token
- `SENTRY_DSN` - Sentry DSN

---

## Architecture Principles

- **App-First:** iOS native app is primary, web is secondary
- **Service-Oriented Architecture (SOA):** Modular backend services
- **Monorepo with Turborepo:** Single repository for all code
- **Shared Firestore Database:** Centralized data storage
- **Vercel API Gateway:** Unified entry point for all clients
- **Firebase Cloud Functions:** Backend services
- **Notebook-First for Algorithms:** Matching, pricing, recommendations

---

## Mathematical Autopsy (MA) Process

**When MA Applies:**

- Matching algorithms (job-to-helper matching)
- Pricing models (dynamic pricing, estimates)
- Recommendation engines (proactive task suggestions)
- Any algorithm with performance guarantees

**MA Phases (MANDATORY):**

1. **Phase 1:** Intent & Description
2. **Phase 2:** Mathematical Foundation
3. **Phase 3:** Lemma Development (Invariant + Lemma)
4. **Phase 4:** Verification (Notebook-first implementation)
5. **Phase 5:** CI Enforcement

**Exception:** Trivial bugfixes, UI changes, and non-algorithmic features don't require MA process.

**Reference:** `.cursor/rules/ma-process-mandatory.mdc` for complete details

---

## Notebook-First Development

**MANDATORY for Algorithms:**

- Write algorithm code in notebooks first (`notebooks/math/`)
- Test and debug in notebooks
- Extract code to services only after all tests pass
- NEVER edit extracted algorithm code directly - fix in notebooks and re-extract

**Exception:** Non-algorithmic code (UI, API routes, utilities) can be written directly in codebase.

**Reference:** `.cursor/rules/notebook-first-mandatory.mdc` for complete details

---

## Testing Requirements

**MANDATORY:**

- Test real implementations, not mocks (for core behavior)
- Unit tests for all services
- Integration tests for service interactions
- E2E tests for critical user flows

**Reference:** `.cursor/rules/testing-no-workarounds.mdc` for complete details

---

## Codex Operating Rules

Codex MUST follow:

- Context awareness (read files, never assume)
- Minimal scope / least-diff principle
- Patch-first requirement
- Verification-first principle
- Architecture preservation
- Security & secret handling
- Notebook-first development (for algorithms)

**Reference:** `codex/CODEX_OPERATING_RULE.mdc` for complete details

---

## Related Documents

- **North Star:** `Operations/NORTHSTAR.md` ⭐ **START HERE**
- **Execution Plan:** `Operations/EXECUTION_PLAN.md`
- **Action Log:** `Operations/ACTION_LOG.md`
- **Financial Plan:** `Financial/FINANCIAL_PLAN.md`
- **Agent Specifications:** `AGENTS.md`
- **Codex Operating Rule:** `codex/CODEX_OPERATING_RULE.mdc`
- **Codex Playbook:** `codex/CODEX_PLAYBOOK.md`

---

**Last Updated:** 2025-01-06
**Version:** 1.0
