# M365 Standalone Graph Runtime Integration Pack - P0B/P0C/P0D/P0E Intent And Boundary

**Plan:** `plan:m365-standalone-graph-runtime-integration-pack:R1`
**Phases covered:** `P0B` Target-state intent, `P0C` M365/UCP boundary lock, `P0D` Acceptance language, `P0E` Approval packet.
**Date:** 2026-04-25
**Owner:** SMARTHAUS
**Predecessor:** `docs/commercialization/m365-standalone-graph-runtime-integration-pack-current-artifact-autopsy.md` (P0A).

## P0B - Target-State Intent

### What we are building

A **real standalone Microsoft 365 Integration Pack**: a single distributable `.ucp.tar.gz` artifact that contains, inside its own payload, a local Microsoft Graph runtime service, the Microsoft auth flows it needs, secure local token storage policy, a launcher, the UCP-facing contracts (setup, auth, health, readiness, action, lifecycle), a read-only Graph action runtime, and the packaging evidence required for marketplace distribution. After the artifact is installed under `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/<version>/`, UCP must be able to install, enable, launch, configure, sign in, health-check, and execute read-only Microsoft Graph actions without the M365 source repository being present on disk.

### Why we are building it

The current packaged artifact (see P0A) is truthfully a UCP-facing client/contract pack. It is not yet a real Microsoft integration: it points at an unpackaged external service, walks parent directories for the M365 source tree, and contains zero Microsoft Graph or OAuth implementation. Marketing the current bundle as "the M365 integration pack" is a readiness over-claim. The product target requires that UCP be able to install one artifact from the marketplace and have a working Microsoft 365 integration. That promise can only be kept by packaging the runtime itself, not by hand-waving an external dependency.

### What problem this solves

- A marketplace-installed M365 pack must be self-contained. Today it is not.
- A UCP host must not need to know how to launch M365's internal service. Today it does, because the launcher imports `ops_adapter.main` and walks `UCP_ROOT` / `REPOS_ROOT`.
- A real Microsoft integration must hold tokens responsibly, classify Graph errors deterministically, and prove readiness through real signals. Today it does not.
- An installed artifact must remain proof-clean if the source repo is renamed, hidden, or removed. Today it would break.

### Boundaries and non-goals

In scope (this plan):

- Microsoft Graph runtime service packaged inside the artifact.
- Authorization Code + PKCE delegated auth, device-code fallback where approved, and app-only client-credentials / certificate flow.
- Secure local token storage (Keychain-first, encrypted pack-local fallback only if explicitly approved).
- Setup schema for tenant ID, client ID, auth mode, redirect/device-code policy, app-only credential references, and actor UPN.
- UCP contracts for setup, auth start/check/clear/status, health, readiness, action invocation, and lifecycle (install, enable, launch, stop, restart, clear-auth, uninstall).
- Read-only Microsoft Graph action acceptance (org profile, current user, users list, groups list, sites root, site search, Teams list, drives list, mail/calendar health where permitted).
- Reproducible marketplace artifact with manifest, payload, signatures, SHA256SUMS, provenance, and conformance evidence.
- Acceptance proof that the installed artifact runs without the M365 source repo on disk.

Explicitly out of scope (other plans, or future phases):

- Username/password capture or storage. Forbidden.
- UCP embedding any Microsoft Graph implementation. Forbidden by boundary lock (see P0C).
- Sibling repo lookup or `M365_REPO_ROOT` from packaged runtime behavior.
- Write or mutation Graph actions. Stays fenced until a separate mutation-governance plan approves them.
- Public SaaS hosting, webhook receivers, multi-tenant marketplace publishing, and enterprise tenant rollout. These are deferred to follow-on plans.

### Required guarantees

- **Self-containment:** the installed artifact contains every file it needs to run, including the runtime service and launcher.
- **No source repo dependency:** runtime behavior never reads from the M365 source tree, never resolves `M365_REPO_ROOT`, never walks parent directories searching for `registry/agents.yaml` or `src/ops_adapter`.
- **Auth safety:** no username/password storage, no token logging, no secret leakage in audit, log, or evidence files.
- **Fail-closed readiness:** `Ready=true` is reported only when artifact, launch, auth, token, Graph reachability, permission, and UCP contract predicates are all true.
- **Deterministic state classes:** every readiness, auth, action, and health response resolves to one of a finite, declared failure-class set.
- **Reproducible packaging:** identical source commit + lockfile + build inputs produce identical SHA256 sums.
- **Audit envelope on every transition:** setup, auth, health, action invocation, and lifecycle changes produce a bounded audit record with strict redaction.
- **Mutation fence:** write actions are explicitly denied at the runtime layer until a separate plan approves them.

### Success criteria

- The installed artifact at `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/<version>/` launches its runtime service from its own root, with `M365_REPO_ROOT` unset and the M365 source tree renamed or moved.
- The runtime exposes the declared health, auth, and action contracts on a local socket/port. UCP resolves contracts from the installed artifact only.
- A delegated OAuth sign-in completes against the configured tenant. The acquired tokens are stored in macOS Keychain by default (or the explicitly approved encrypted pack-local store) and never appear in logs or audit.
- Readiness reports `false` until each predicate is independently proven true. After the predicates are true, readiness reports `true` and the read-only Graph action acceptance suite executes against Microsoft Graph.
- The packaged manifest, payload, signatures, SHA256SUMS, provenance, and conformance evidence are reproducible and inspectable.

### Determinism

- **Artifact determinism.** Reproducibility is enforced by lockfiles, deterministic file ordering in `payload.tar.gz`, and recorded SHA256 sums.
- **Runtime determinism.** Service startup, config validation, contract resolution, action routing, error taxonomy, and audit shape are deterministic for the same inputs. Unknown state resolves to a specific failure class.
- **Microsoft Graph nondeterminism.** Network latency, throttling, tenant policy, consent state, and Graph service state are bounded by explicit timeouts, retry budgets, normalized response classes, and recorded evidence. Microsoft Graph cannot be made deterministic; its variation is fenced by the runtime contract.
- **Auth nondeterminism.** Production OAuth state, nonce, PKCE verifier, and token material use secure randomness. Tests must not seed production crypto. Deterministic tests use mocked providers and redacted fixtures.
- **Fail-closed rule.** Unknown, missing, expired, permission-denied, or ambiguous states resolve to `not_ready` or `denied`. Implicit success is forbidden.

## P0C - M365 Versus UCP Boundary Lock

### M365 owns

- Microsoft Graph runtime service: code, process model, port/socket contract, configuration validation, and stop/restart behavior.
- Microsoft auth flows: Authorization Code + PKCE, device-code fallback, app-only client-credentials and certificate flows, including all OAuth state, PKCE verifiers, redirects, code exchange, and refresh.
- Token storage policy and implementation: Keychain-first with the explicitly approved encrypted pack-local fallback, and never username/password.
- Microsoft Graph client: timeouts, retry budgets, throttling handling, request IDs, normalized error classes, and audit redaction.
- Action registry: action IDs, workload, Graph endpoint family, auth mode, scopes, risk class, and read/write classification.
- Permission matrix: per-action scope/role declarations, with fail-closed denial when a required scope or role is absent.
- UCP-facing contract surface: setup schema, auth contract, health contract, readiness contract, action contract, lifecycle contract, and audit envelope.
- Packaging artifact: manifest, payload, signatures, SHA256SUMS, provenance, and conformance evidence.
- Operations: runbook, token recovery, rollback, version migration, support evidence policy.

### UCP owns

- Marketplace lifecycle: pack discovery, install, enable, disable, uninstall, and version pinning.
- Pack-host runtime: launching the M365 runtime service from the installed artifact, observing its health, projecting readiness into the UCP shell, and stopping it cleanly.
- Setup driving: rendering the M365 setup schema to the operator, persisting setup outputs back into the pack-local config surface, and clearing them on uninstall.
- Action invocation: routing authorized requests through the declared M365 action contract and surfacing normalized error classes.
- Cross-pack governance: license/entitlement gates, tenancy projection, and cross-pack contracts that the M365 pack does not own.

### What is forbidden across the boundary

- UCP must not embed Microsoft Graph implementation, OAuth code, token storage, or Graph error normalization.
- M365 must not mutate UCP source under this plan unless a sibling UCP plan explicitly opens that scope.
- The installed M365 runtime must not depend on the M365 source repository, `M365_REPO_ROOT`, sibling repo walks, or any path resolution that escapes the installed artifact root.
- UCP must not call Microsoft Graph directly. UCP calls the M365 pack's contracts; the pack calls Graph.

## P0D - Acceptance Language

This is the language `Ready=true` is allowed to use. Any acceptance claim that does not satisfy every clause below is a readiness over-claim and must be rejected.

A standalone M365 Graph runtime integration pack is **accepted** only when all of the following are independently proven:

1. **`ArtifactSelfContained(p, r)` -** The installed artifact `p` at root `r` contains the runtime service, launcher, setup schema, registry, action registry, manifest, payload, signatures, evidence, and dependencies. Removing or renaming the M365 source repository on the host has no effect on `p`'s ability to run from `r`.
2. **`RuntimeLaunchable(p, r)` -** The installed launcher starts the runtime service from `r` alone, listens on the declared local endpoint, and reports a deterministic launch state (started, port-conflict, config-invalid, dependency-missing, or unknown-failure). No state is silent.
3. **`AuthConfigured(c)` -** The setup configuration `c` includes tenant ID, client ID, auth mode, and the Microsoft credential references needed for the selected mode. Username/password is rejected at config validation. Missing fields fail closed.
4. **`TokenStoreSafe(c, r)` -** Tokens are stored in Keychain (or the explicitly approved encrypted pack-local store). No tokens, secrets, refresh tokens, authorization codes, client secrets, or certificate private keys appear in logs, audit, or packaging evidence.
5. **`GraphReachable(c, h)` -** The runtime can reach Microsoft Graph through the configured auth, with bounded retry/throttle/timeouts. Reachability is inferred only from real Graph responses, not from absence of errors.
6. **`PermissionsSufficient(A, c, h)` -** For every action in the bound action set `A`, the per-action scope/role declaration is satisfied by the current auth state. Where a scope is missing, the runtime fails closed with `permission_missing` and the audit records which scope is absent.
7. **`UcpContractsResolvable(p, u)` -** UCP `u` resolves the pack's setup, auth, health, readiness, action, and lifecycle contracts entirely from `p` at `r`. UCP does not import Microsoft Graph code, does not read `M365_REPO_ROOT`, and does not look for the M365 source tree.
8. **`AuditComplete(A, h)` -** Every setup, auth, health, action, and lifecycle transition produces a bounded audit record with strict redaction.
9. **`NoSourceRepoDependency(p, r)` -** Source-removal acceptance demonstrates that hiding or renaming the M365 source repository on disk does not change pack behavior at `r`. Repeating any acceptance step must succeed.

If any clause is unproven, ambiguous, missing, or implicit, readiness is `false`. There is no partial credit.

### Required evidence shapes

- **Notebook-backed proof** for readiness, auth-state classification, action-permission matrix, artifact-layout, and packaging invariants.
- **Scorecard** with notebook hash, invariant pass/fail, deterministic replay certification, and extraction readiness flag.
- **Source-removal acceptance log** showing the artifact running without the M365 source on disk.
- **Mock acceptance log** showing deterministic Graph replay covering the read-only action set.
- **Live read-only acceptance log** showing UCP invoking at least one Microsoft Graph read action through the installed artifact against the configured tenant.
- **Conformance and SHA256SUMS** showing the marketplace artifact bytes match the manifest and provenance.
- **Audit redaction proof** showing no token, secret, or refresh-token material appears in any logged record.

## P0E - Approval Packet

### Decision Summary
Build the M365 Integration Pack as a standalone Microsoft Graph runtime artifact (Option C in the plan's decision package), with Microsoft auth, secure token storage, health/readiness contracts, UCP host contracts, packaging evidence, and source-removal acceptance proof. Reject Option A (keep client-only artifact) and Option B (move Graph into UCP) on the grounds documented in `plans/m365-standalone-graph-runtime-integration-pack/m365-standalone-graph-runtime-integration-pack.md`.

### Options Considered (with truth)
- **Option A.** Keep the current client-only artifact and require an external M365 service URL. Pro: minimal packaging change. Con: not a real integration pack; readiness depends on an unshipped, ungoverned external service. Today's pack is exactly this.
- **Option B.** Put Microsoft Graph logic directly into UCP. Pro: fewer local hops. Con: violates the boundary lock, makes UCP a Microsoft integration implementation, breaks pack ownership, and is not how the marketplace contract is supposed to work.
- **Option C (chosen).** Build the M365 artifact as a standalone local Graph runtime pack. Pro: truthful, marketplace-portable, fail-closed, testable from the installed artifact. Con: requires real auth/runtime packaging work and admin/tenant cooperation for live acceptance.

### Evaluation Criteria
- Mathematical soundness: readiness becomes a deterministic predicate over artifact, auth, service, permission, and Graph health.
- Deterministic guarantees: nondeterministic Microsoft/network behavior is fenced by timeouts, retry, normalized errors, and replay fixtures.
- Invariant enforceability: self-containment, auth safety, action permission, audit, and no-cross-repo are all machine-checkable.
- Maintenance overhead: M365 owns Graph behavior; UCP owns marketplace lifecycle and invocation; cross-cutting concerns stay isolated.
- Deployment viability: installed artifact launches locally without source-tree assumptions.

### Why this choice
The product claim is "real M365 integration." That cannot be satisfied by a contract pack that calls an unspecified external service. The only truthful path is to package the runtime service itself, then let UCP install, configure, launch, and observe it through declared contracts.

### What risks remain
- Microsoft tenant setup still requires Entra app registration, consent, scopes, and possibly admin involvement that cannot be delivered by packaging alone.
- Production OAuth uses cryptographic randomness by design; tests must replay deterministic fixtures while production preserves secure randomness.
- Some Graph endpoints require licenses, admin roles, or tenant policies that cannot be guaranteed by packaging alone.
- UCP marketplace launch/setup UX may need a sibling UCP plan after the M365 artifact contract is defined.

### Next steps
- Mark `P0` complete in the parent plan, execution plan, project file index, and action log.
- Begin `P1` Governing Formula And Formal Calculus, producing the formal readiness/action calculus document.
- Continue strictly in phase order with MCP `validate_action` checks before every mutating action and stop on the first failed invariant, scorecard, or boundary violation.

### Governance closure for P0

- [x] `P0A` autopsy doc + notebook + verification artifact published.
- [x] `P0B` target-state intent fixed in this document.
- [x] `P0C` M365/UCP boundary lock fixed in this document.
- [x] `P0D` acceptance language fixed in this document.
- [x] `P0E` approval packet ready (this section).
- [x] User has explicitly authorized executing the full plan unless a hard blocker is encountered.
- [ ] Begin `P1` Governing Formula And Formal Calculus (next phase).

This document and `m365-standalone-graph-runtime-integration-pack-current-artifact-autopsy.md` together close `P0`. No code or runtime extraction is authorized in `P0`.
