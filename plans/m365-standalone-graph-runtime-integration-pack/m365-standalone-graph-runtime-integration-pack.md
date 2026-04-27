# Plan: M365 Standalone Graph Runtime Integration Pack

**Plan ID:** `m365-standalone-graph-runtime-integration-pack`  
**Parent plan ID:** `m365-marketplace-bundle-packaging-conformance`  
**Status:** Active - **Fix-Required / NO-GO**. The previous claim of `Complete (M365-side)` and release decision `GO` for `com.smarthaus.m365@1.1.0` is **withdrawn** as over-claimed. The later `1.1.1` fix snapshot proved real Microsoft delegated auth plus live read-only `graph.me`, but the 2026-04-27 installed-payload smoke still returned `not_ready/art`, so it is historical prerelease evidence rather than a formal ready artifact. The active corrective plan is `plans/m365-standalone-graph-runtime-pack-0-1-2-readiness-fix/m365-standalone-graph-runtime-pack-0-1-2-readiness-fix.md`, targeting `com.smarthaus.m365@0.1.2`. Phases `P5`-`P10` remain fix-required until that plan closes green.  
**Date:** 2026-04-25  
**Owner:** SMARTHAUS  
**Execution plan reference:** `plan:m365-standalone-graph-runtime-integration-pack:R1`  
**North Star alignment:** `Operations/NORTHSTAR.md` - M365-only tooling, self-service operation, policy enforcement, audit coverage, and truthful commercialization boundaries.  
**Governance mode:** AGENTS.md, `.cursor/rules/*.mdc`, MCP `validate_action`, plan-first execution, project-file index enforcement, action-log closure, and MA notebook-first extraction for runtime code.

## Current Status Truth

The current M365 marketplace artifact is not a complete Microsoft integration pack. It is installable as a UCP-facing client/contract artifact, but it does not contain the full Microsoft Graph auth/runtime service. A truthful real integration pack must be able to operate from the installed artifact itself, without a sibling repo lookup, hidden `M365_REPO_ROOT`, or external service assumption that is not packaged, launched, governed, and health-checked by the pack.

2026-04-27 correction: the active release target is `0.1.2`, not `1.1.x`. The `1.1.1` artifact is useful evidence because it proves live SmartHaus device-code sign-in and `graph.me` can work, but it is still `NO-GO` for formal readiness because installed-payload readiness fails `art=false`, dependency closure is implicit, release acceptance must move to an unpatched real local socket path, and provenance must be clean-source reproducible.

The correct product target is:

`M365 source repo -> standalone M365 Graph runtime pack artifact -> copied to /Users/smarthaus/Projects/GitHub/IntegrationPacks/ -> UCP Marketplace installs/enables/launches it -> UCP drives setup/auth/health/actions through the installed artifact`

## Decision Package

🥇 Decision Summary
- Build a standalone M365 Integration Pack that includes the Microsoft Graph runtime service, OAuth/app-only auth setup, secure token handling, launcher, health checks, UCP contracts, and reproducible marketplace packaging inside the distributable artifact.

📊 Options Considered
- Option A: Keep the current client-only artifact and require an external M365 service URL. Pro: minimal packaging change. Con: not a real integration pack; readiness depends on an unshipped service.
- Option B: Put Microsoft Graph logic directly into UCP. Pro: fewer local service hops. Con: violates pack ownership and makes UCP a Microsoft integration implementation instead of a governed host.
- Option C: Build the M365 artifact as a standalone local Graph runtime pack. Pro: truthful integration, marketplace-portable, fail-closed, testable from the installed artifact. Con: requires real auth/runtime packaging work.

📈 Evaluation Criteria
- Mathematical soundness: readiness must be a deterministic predicate over artifact, auth, service, permissions, and Graph health.
- Deterministic guarantees: nondeterministic Microsoft/network behavior must be bounded by timeouts, retry policy, normalized error classes, and replay fixtures.
- Invariant enforceability: self-containment, auth safety, action permission, audit, and no-cross-repo rules must be machine-checkable.
- Maintenance overhead: M365 owns Graph behavior; UCP owns marketplace lifecycle and invocation.
- Deployment viability: installed artifact must launch locally without source-tree assumptions.

🔍 Why This Choice
- The product claim is "real M365 integration." That cannot be satisfied by a contract pack that calls an unspecified external service. The only truthful path is to package the runtime service itself, then let UCP install, configure, launch, and observe it through declared contracts.

📌 What Risks Remain
- Microsoft tenant setup still requires Entra app registration, consent, scopes, and possibly admin involvement.
- Production OAuth uses cryptographic randomness by design; tests must replay deterministic fixtures while production preserves secure randomness.
- Some Graph endpoints require licenses, admin roles, or tenant policies that cannot be guaranteed by packaging alone.
- UCP Marketplace launch/setup UX may need a sibling UCP plan after the M365 artifact contract is defined.

🛠 Next Steps
- Approve Phase `P0` intent.
- Execute phases one at a time, with MCP validation before every write or command execution.
- Stop at every parent gate until the CTO explicitly advances the next phase.

## Scope

### In Scope

- Formal MA definition for a real standalone M365 Graph runtime pack.
- Auth modes: delegated OAuth Authorization Code + PKCE, device-code fallback where appropriate, and app-only client credentials/certificate setup.
- Secure token storage policy: macOS Keychain first, encrypted pack-local fallback only if explicitly approved.
- Local runtime service launched from the installed artifact.
- UCP-facing contracts for setup, auth, health, readiness, action invocation, and audit.
- Graph action layer with a read-only acceptance slice first.
- Reproducible `.ucp.tar.gz` marketplace artifact with manifest, payload, signatures, evidence, checksums, and conformance.
- Acceptance proof that the installed artifact works without the M365 source repo.

### Out of Scope

- Username/password credential capture or storage.
- UCP embedding Microsoft Graph implementation logic.
- Sibling repo lookup from the installed pack.
- Claiming `Ready=true` before service/auth/Graph health pass.
- Write/mutation Graph actions before read-only acceptance and separate mutation-governance approval.
- Public SaaS hosting, webhook receivers, or multi-tenant commercial marketplace publishing unless added by a later plan.

### File Allowlist For Planning Package

- `plans/m365-standalone-graph-runtime-integration-pack/**`
- `docs/prompts/codex-m365-standalone-graph-runtime-integration-pack.md`
- `docs/prompts/codex-m365-standalone-graph-runtime-integration-pack-prompt.txt`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### Future Implementation Candidate Surfaces

These are not authorized for modification by this planning slice, but are expected candidate surfaces after future phase approval:

- `src/m365_server/**`
- `src/smarthaus_graph/**`
- `src/ucp_m365_pack/**`
- `src/ops_adapter/**`
- `registry/**`
- `invariants/**`
- `docs/ma/**`
- `notebooks/m365/**`
- `notebooks/lemma_proofs/**`
- `artifacts/scorecards/**`
- `configs/generated/**`
- `scripts/ci/**`
- `tests/**`
- `dist/m365_pack/**`

## Governing Readiness Formula

Define a pack artifact `p`, tenant/setup configuration `c`, installed runtime root `r`, UCP host `u`, Graph action set `A`, and observed health vector `h`.

The standalone pack is ready only if:

```text
Ready(p, c, r, u, A, h) =
  ArtifactSelfContained(p, r)
  and RuntimeLaunchable(p, r)
  and AuthConfigured(c)
  and TokenStoreSafe(c, r)
  and GraphReachable(c, h)
  and PermissionsSufficient(A, c, h)
  and UcpContractsResolvable(p, u)
  and AuditComplete(A, h)
  and NoSourceRepoDependency(p, r)
```

If any predicate is false or unknown, `Ready=false`. No partial evidence may be converted into readiness.

## Determinism Model

- Artifact determinism: the same source commit, lockfiles, manifest, and build inputs must produce the same file list, checksums, and conformance evidence.
- Runtime determinism: service startup, config validation, contract resolution, action routing, error taxonomy, and audit shape must be deterministic for the same inputs.
- Microsoft Graph nondeterminism: network latency, throttling, tenant policy, consent state, and Graph service state are bounded by explicit timeouts, retry budgets, normalized response classes, and recorded evidence.
- Auth nondeterminism: production OAuth state, nonce, PKCE verifier, and token material must use secure randomness. Tests must not seed production crypto; deterministic tests use mocked providers and redacted fixtures.
- Fail-closed rule: unknown, missing, expired, permission-denied, or ambiguous states resolve to not-ready or denied, never implicit success.

## Language Selection Framework

| Criteria | Python | Rust | Go | C++ | TypeScript |
| --- | --- | --- | --- | --- | --- |
| Deterministic guarantees | 3 | 5 | 4 | 3 | 3 |
| Memory safety | 3 | 5 | 4 | 2 | 3 |
| Concurrency model | 3 | 5 | 4 | 3 | 4 |
| Numerical precision | 4 | 5 | 4 | 5 | 3 |
| Graph/MSAL library availability | 5 | 2 | 3 | 2 | 5 |
| Performance boundaries | 3 | 5 | 4 | 5 | 3 |
| Deployability | 3 | 4 | 5 | 2 | 3 |
| Operational maintainability | 4 | 3 | 4 | 2 | 4 |
| Enterprise support | 4 | 4 | 4 | 3 | 4 |

**Recommendation:** Python for the first standalone runtime service, with an optional small Rust or Go launcher later only if packaging or process supervision requires it. This repo already has Python Graph/runtime code, tests, and packaging flow. TypeScript has strong Graph SDK support but would add a second runtime stack and duplicate existing service logic. Rust/Go are stronger for static binaries, but Microsoft auth ecosystem fit and current repo alignment are weaker for the first real integration pack.

## Parent And Child Phase Plan

### P0 - Intent Definition And Baseline Lock

**Goal:** Get CTO approval for the exact product intent before math or runtime work.

Child phases:

- `P0A` Current artifact autopsy: document the exact current bundle contents and prove the missing Graph runtime service.
- `P0B` Target-state intent: define what "real M365 integration" means and what claims are forbidden.
- `P0C` Boundary lock: define M365-owned artifact responsibilities versus UCP-owned marketplace host responsibilities.
- `P0D` Acceptance language: define what evidence is required before `Ready=true`.
- `P0E` Approval packet: present Phase 0 for CTO approval and stop.

Exit gate:

- CTO approves intent explicitly.
- Current artifact truth is documented without readiness over-claim.
- No implementation begins in `P0`.

### P1 - Governing Formula And Formal Calculus

**Goal:** Convert the product target into mathematical readiness, launch, auth, and action-execution predicates.

Child phases:

- `P1A` Define domains: artifacts, runtime roots, setup configs, auth states, action requests, Graph responses, UCP contracts.
- `P1B` Define readiness formula: formalize `Ready(p,c,r,u,A,h)`.
- `P1C` Define action execution function: `Execute(action, actor, auth_state, policy, graph_state) -> result | denial`.
- `P1D` Define failure lattice: success, not_configured, auth_required, consent_required, permission_missing, throttled, graph_unreachable, policy_denied, internal_error.
- `P1E` Define deterministic boundaries for Graph and OAuth nondeterminism.

Exit gate:

- Formal calculus document exists.
- Every readiness and action state has a deterministic result class.
- No runtime extraction is allowed yet.

### P2 - Lemmas And Machine Invariants

**Goal:** Turn the calculus into provable lemmas and executable invariants.

Child phases:

- `P2A` Lemma L-STANDALONE: installed artifact requires no source repo.
- `P2B` Lemma L-LAUNCH: installed artifact deterministically launches or reports a launch error.
- `P2C` Lemma L-AUTH: auth setup never stores passwords and never exposes tokens in logs.
- `P2D` Lemma L-PERMISSIONS: each action declares required Graph scopes/roles and fails closed when absent.
- `P2E` Lemma L-READINESS: readiness is true only when artifact, launch, auth, Graph, permission, and UCP contract predicates are true.
- `P2F` Lemma L-AUDIT: every setup/auth/health/action transition produces a bounded audit record.
- `P2G` Lemma L-PACKAGING: artifact checksums, signatures, evidence, and payload inventory match the declared manifest.

Exit gate:

- Lemma docs and invariant YAML are approved.
- CI/test bindings are declared before notebook work.

### P3 - Notebook Proof And Scorecard Gate

**Goal:** Build proof notebooks before runtime extraction.

Child phases:

- `P3A` Create notebook headers mapping purpose, lemmas, invariants, expected results.
- `P3B` Prototype pure readiness and state-classification functions in notebooks.
- `P3C` Prototype auth-state and token-store policy checks with mocked providers.
- `P3D` Prototype Graph action registry and permission matrix checks.
- `P3E` Prototype artifact-layout and no-source-repo checks.
- `P3F` Emit `scorecard.json` with invariant pass/fail, notebook hash, deterministic replay, and extraction certification.

Exit gate:

- Scorecard green.
- Notebook hash recorded.
- No code extraction until this gate is green.

### P4 - Runtime Service And Auth Foundation

**Goal:** Build the real local Microsoft Graph runtime service from notebook-proven logic.

Child phases:

- `P4A` Service layout: define packaged runtime entrypoint, process model, local port/socket contract, and stop/restart behavior.
- `P4B` Config schema: define tenant ID, client ID, auth mode, redirect/device-code policy, app-only credential references, and actor UPN fields.
- `P4C` Delegated auth: implement Authorization Code + PKCE and device-code fallback as approved.
- `P4D` App-only auth: implement client secret or certificate flow using secure secret references.
- `P4E` Token storage: implement Keychain-first storage and encrypted fallback only if approved.
- `P4F` Auth endpoints: `start_sign_in`, `check_sign_in`, `clear_sign_in`, `auth_status`.
- `P4G` Secret redaction: prove no token, secret, assertion, or refresh token reaches logs, audit payloads, or package evidence.

Exit gate:

- Runtime starts from installed-artifact layout.
- Auth endpoints return deterministic states.
- No live write actions included.

### P5 - Microsoft Graph Action Runtime

**Goal:** Add real Graph-backed actions with registry, permission, retry, audit, and error-normalization discipline.

Child phases:

- `P5A` Action registry: declare action IDs, workload, Graph endpoint family, auth mode, scopes, risk, and read/write class.
- `P5B` Read-only slice: org profile, current user, users list, groups list, sites root, site search, Teams list, drives list, mail/calendar health where permitted.
- `P5C` Graph client: timeouts, retry budget, throttle handling, request IDs, and normalized errors.
- `P5D` Permission matrix: prove action-specific scope/role requirements before execution.
- `P5E` Audit envelope: request, actor, auth mode, action ID, normalized result, Graph correlation IDs, and redaction.
- `P5F` Mutation fence: explicitly deny write actions until a separate mutation-governance plan approves them.

Exit gate:

- Read-only action acceptance works against mocked Graph and live tenant where configured.
- Write actions remain fenced.

### P6 - UCP Pack Contract And Local Lifecycle

**Goal:** Make the installed pack expose a complete host contract to UCP.

Child phases:

- `P6A` Manifest vNext: declare runtime service, launch command, setup schema, auth contract, health contract, action contract, and evidence paths.
- `P6B` Launcher: start the service from the installed artifact root without source repo assumptions.
- `P6C` Health contract: service health, auth health, token health, Graph connectivity, permission matrix, and last action proof.
- `P6D` UCP client/contracts: update `ucp_m365_pack` to call the installed runtime service and report exact readiness.
- `P6E` Lifecycle: install, enable, launch, stop, restart, clear-auth, and uninstall boundaries.
- `P6F` No-cross-repo verifier: fail if contracts resolve through sibling repo paths.

Exit gate:

- UCP can resolve contracts from the installed artifact.
- Runtime import and service launch do not require the M365 source checkout.

### P7 - Packaging And Distribution

**Goal:** Produce a reproducible standalone marketplace artifact.

Child phases:

- `P7A` Payload layout: include `ucp_m365_pack`, runtime service, setup schema, registry, launcher, locked dependencies, docs, and evidence.
- `P7B` Dependency lock: freeze runtime dependencies and platform constraints.
- `P7C` Manifest and signatures: produce manifest, payload digest, signatures, and checksums.
- `P7D` SBOM/provenance: record source commit, build inputs, dependency set, and conformance results.
- `P7E` Reproducible bundle: emit `.ucp.tar.gz` and `SHA256SUMS`.
- `P7F` Local store copy: copy only the completed artifact to `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/<version>/`.

Exit gate:

- `SHA256SUMS` passes.
- Payload inventory proves runtime service is present.
- No source repo path appears in install/runtime metadata.

### P8 - UCP Marketplace Activation Boundary

**Goal:** Define and execute the cross-repo handoff only after M365 artifact readiness.

Child phases:

- `P8A` M365 handoff packet: artifact path, manifest digest, conformance evidence, setup schema, and launch contract.
- `P8B` UCP plan dependency: open or reference a sibling UCP plan for generic local Integration Pack Store scanning and service lifecycle.
- `P8C` Install proof: UCP installs the artifact from the local store into runtime state.
- `P8D` Launch proof: UCP starts the installed service and health endpoint responds.
- `P8E` Setup/auth proof: UCP drives the declared setup/auth flow without hidden env-only assumptions.
- `P8F` Readiness projection: UCP shows M365 ready only after pack health reports true.

Exit gate:

- Cross-repo work is governed by a UCP plan.
- M365 does not mutate UCP source in this plan unless explicitly re-scoped.

### P9 - Acceptance, Evidence, And Release

**Goal:** Prove the pack works as a real Microsoft integration before release claims.

Child phases:

- `P9A` Source-removal test: rename or hide the M365 source repo and prove installed artifact still works.
- `P9B` Mock acceptance: deterministic Graph replay suite passes.
- `P9C` Live read-only acceptance: execute approved read-only Graph actions through UCP into the installed pack.
- `P9D` Readiness proof: capture health vector showing service/auth/token/Graph/permission readiness.
- `P9E` Evidence packet: diagnostics, screenshots/log snippets as applicable, audit excerpts with redaction, checksums, and scorecards.
- `P9F` Release decision: GO only if every invariant and acceptance criterion is green.

Exit gate:

- `Ready=true` is proven from installed artifact.
- At least one read-only Graph action executes through UCP against Microsoft Graph.
- Release docs state any tenant/license limitations.

### P10 - Operations, Rollback, And Maintenance

**Goal:** Make the integration maintainable after first release.

Child phases:

- `P10A` Operator runbook: setup, sign-in, app-only setup, health, restart, logs, and support boundaries.
- `P10B` Token recovery: clear sign-in, revoke token, rotate app secret/certificate, and reset local state.
- `P10C` Rollback: disable pack, stop service, restore previous artifact, and verify ready false/previous ready.
- `P10D` Version migration: config and token-state migration rules.
- `P10E` Support evidence: bug report packet without secrets.
- `P10F` Roadmap gate: define separate plans for write actions, webhooks, subscriptions, and enterprise deployment.

Exit gate:

- Runbook complete.
- Rollback tested.
- Maintenance ownership documented.

## Requirements

- `R0` Create this governed plan package and stop before implementation.
- `R1` Approve intent and current-state truth before math or code.
- `R2` Produce formal readiness/action calculus.
- `R3` Produce lemmas and executable invariants.
- `R4` Produce green notebooks and scorecard before extraction.
- `R5` Build installed-artifact runtime service with real Microsoft auth.
- `R6` Build read-only Graph action runtime with permission matrix and audit.
- `R7` Build UCP contracts and local lifecycle launch/health behavior.
- `R8` Produce reproducible standalone marketplace artifact.
- `R9` Complete UCP activation and read-only live acceptance.
- `R10` Publish operations, rollback, and release evidence.

## Acceptance Criteria

- The artifact contains the Graph runtime service, launcher, setup schema, auth contract, health contract, action registry, and UCP client/contracts.
- The installed artifact can launch and respond without the M365 source repo present.
- Auth is Microsoft OAuth/app-only, never username/password storage.
- Tokens are stored securely and never logged.
- `Ready=false` until service, auth/token, Graph connectivity, and permissions pass.
- Read-only Graph actions execute through UCP against the installed artifact.
- Every package file has checksum/signature/provenance/conformance evidence.
- No sibling repo lookup, `M365_REPO_ROOT`, or `../M365` runtime dependency exists.

## Stop Conditions

- Any attempt to mark the current client-only artifact as a complete integration.
- Any attempt to store Microsoft username/password credentials.
- Any missing MA phase before runtime extraction.
- Any source repo dependency in packaged runtime behavior.
- Any readiness path that succeeds when auth, token, Graph, or permission state is unknown.
- Any mutation/write action before separate mutation-governance approval.

## Validation Strategy

- YAML/JSON parse checks for plan and generated authority files.
- Notebook replay for readiness, auth-state, permission, audit, and packaging invariants.
- Unit tests for pure state functions and runtime contracts.
- Mock Graph replay tests for deterministic action behavior.
- Live read-only tenant acceptance after explicit approval.
- Installed-artifact source-removal acceptance.
- `SHA256SUMS` and conformance proof inside the Integration Pack store.

## Governance Closure For This Planning Slice

- [x] `Operations/ACTION_LOG.md` updated.
- [x] `Operations/EXECUTION_PLAN.md` updated.
- [x] `Operations/PROJECT_FILE_INDEX.md` updated.
- [x] Plan triplet created.
- [x] Prompt pair created.
- [x] Implementation approval obtained (user explicit "continue through the whole plan unless there is a hard blocker", 2026-04-25).

## Phase Status

- `P0` Intent Definition And Baseline Lock - **Complete** (2026-04-25). Backed by `notebooks/m365/INV-M365-DK-standalone-graph-runtime-pack-p0-current-artifact-autopsy-v1.ipynb`, `configs/generated/standalone_graph_runtime_integration_pack_p0_current_artifact_autopsy_v1_verification.json`, `docs/commercialization/m365-standalone-graph-runtime-integration-pack-current-artifact-autopsy.md`, and `docs/commercialization/m365-standalone-graph-runtime-integration-pack-intent-and-boundary.md`. All five autopsy invariants `I1`-`I5` are green. Current artifact is truthfully a UCP client/contract pack only.
- `P1` Governing Formula And Formal Calculus - **Complete** (2026-04-26). Backed by `notebooks/m365/INV-M365-DL-standalone-graph-runtime-pack-p1-formal-calculus-v1.ipynb`, `configs/generated/standalone_graph_runtime_integration_pack_p1_formal_calculus_v1_verification.json`, and `docs/ma/m365-standalone-graph-runtime-integration-pack-formal-calculus.md`. Domains, readiness predicate, action-execution function, failure lattice, and deterministic boundaries are fixed; green base case Ready=true and 11 negative clause cases drive Ready=false; Execute() outcome set is `{success, auth_required, permission_missing, throttled, graph_unreachable, policy_denied, mutation_fence, internal_error}` and is a subset of the declared lattice; mutation fence theorem holds; redaction regex proof passes.
- `P2` Lemmas And Machine Invariants - **Complete** (2026-04-26). Backed by `docs/ma/lemmas/L98_m365_standalone_graph_runtime_pack_lemmas_v1.md`, `invariants/lemmas/L98_m365_standalone_graph_runtime_pack_lemmas_v1.yaml`, `notebooks/m365/INV-M365-DM-standalone-graph-runtime-pack-p2-lemmas-v1.ipynb`, `notebooks/lemma_proofs/L98_m365_standalone_graph_runtime_pack_lemmas_v1.ipynb`, `artifacts/scorecards/scorecard_l98.json`, and `configs/generated/standalone_graph_runtime_integration_pack_p2_lemmas_v1_verification.json`. Seven lemmas (`L_STANDALONE`, `L_LAUNCH`, `L_AUTH`, `L_PERMISSIONS`, `L_READINESS`, `L_AUDIT`, `L_PACKAGING`) are stated, bound to the readiness predicate, given green base proofs, and given 17 negative-case rejections. Bundled `StandaloneRuntimeTruth` predicate equals their conjunction.
- `P3` Notebook Proof And Scorecard Gate - **Complete** (2026-04-26). Backed by `notebooks/m365/INV-M365-DN-standalone-graph-runtime-pack-p3-prototypes-v1.ipynb`, `configs/generated/standalone_graph_runtime_integration_pack_p3_prototypes_v1_verification.json`, and `artifacts/scorecards/scorecard_standalone_graph_runtime_pack_p3.json` (`status=green`). Pure-Python prototypes for readiness, auth-state classification, token-store policy, action registry + permission matrix (11 read-only Graph actions), and artifact-layout / no-source-repo checks all pass deterministically. The scorecard certifies `ready_for_extraction=true` and lists the exact extraction target paths under `src/m365_runtime/`. Runtime extraction in P4 is now authorized under MA gate `map-2-code-notebook-required`.
- `P4` Runtime Service And Auth Foundation - **Complete** (2026-04-26). Extracted the bounded standalone runtime package `src/m365_runtime/` from the P3 prototypes: `__init__.py` (constants), `__main__.py` (CLI), `launcher.py` (`plan_launch` + FastAPI app builder + `run`), `setup.py` (`SetupConfig`, `load_setup`, `load_setup_from_env`, `write_default_schema`, password rejected at validation, token-store policy enforced), `state.py` (HealthVector + readiness function), `audit.py` (redaction regex + bounded 8 KB envelopes), `health.py` (`compose_readiness` over service/auth/token/graph/permission/contract/artifact/source/audit probes), `_forbidden_tokens.py` (single localized list of source-repo / sibling-repo names), `auth/oauth.py` (PKCE/auth_code/device_code/refresh with secure `os.urandom`), `auth/app_only.py` (client-credentials secret + certificate JWT assertion), `auth/token_store.py` (Keychain + encrypted_pack_local backends, plaintext rejected), `graph/client.py` (timeouts, 5xx + throttle retry budgets, normalized errors), `graph/errors.py` (lattice projection from HTTP/Graph status), `graph/registry.py` (read-only action registry of 11 actions; mutation fenced). Focused regressions in `tests/test_m365_runtime_p4_runtime_and_auth.py` cover constants, password rejection, app-only certificate refs, token store unsafe rejection, audit redaction + 8 KB cap, PKCE secure randomness + state, authorize URL shape, device-code request + pending poll, auth-code exchange, refresh failure, app-only secret success + empty-secret rejection, registry consistency, admit/deny over scope/mode/unknown action, Graph error normalization across the lattice, readiness state classification, plan_launch resolves installed root without forbidden env vars, plan_launch preserves lattice for invalid setup, and the no-forbidden-source-repo-token regression scan. Result: `24 passed`. Combined regression `PYTHONPATH=src pytest tests/test_m365_runtime_p4_runtime_and_auth.py tests/test_ucp_m365_pack_contracts.py tests/test_ucp_m365_pack_client.py` returns `39 passed`. `python3 -m py_compile` passes for all new modules.
- `P5` Microsoft Graph Action Runtime - **Complete** (2026-04-26). Added `src/m365_runtime/graph/actions.py` (`invoke()` and `list_actions()`) and wired `/v1/actions` and `/v1/actions/{action_id}/invoke` into the launcher FastAPI app. `invoke()` is a single bounded entry point that runs `admit()` first, fences mutations, returns deterministic lattice nodes (`auth_required`, `permission_missing`, `consent_required`, `policy_denied`, `throttled`, `graph_unreachable`, `internal_error`, `mutation_fence`, `success`), calls `graph_get` with the existing retry/throttle budgets, and emits a redacted bounded audit envelope per call with a fresh correlation ID. The endpoint returns `mutation_fence` for any action_id not in `READ_ONLY_REGISTRY`, refusing to forward unknown action IDs to Graph. Focused regressions in `tests/test_m365_runtime_p5_graph_actions.py` (`12 passed`) cover the admit path, unknown action denial, missing-scope denial, mode-mismatch denial, no-token denial, 403/ConsentRequired -> `consent_required`, 403/Forbidden -> `policy_denied`, 429 throttle-then-success retry path, exhausted-5xx -> `graph_unreachable`, audit redaction of params containing secrets, and `ActionInvocation` correlation-id consistency. Launcher smoke regressions in `tests/test_m365_runtime_p5_launcher_app.py` (`5 passed`) cover `/v1/runtime/version`, `/v1/actions` (count=11, sorted), `/v1/health/readiness`, `/v1/actions/graph.write_something/invoke` returning `mutation_fence`, `/v1/actions/graph.org_profile/invoke` without a token returning `auth_required` or `permission_missing`, and `/v1/auth/status` reporting `unconfigured` when setup is invalid. Combined regression `PYTHONPATH=src pytest tests/test_m365_runtime_p4_runtime_and_auth.py tests/test_m365_runtime_p5_graph_actions.py tests/test_m365_runtime_p5_launcher_app.py tests/test_ucp_m365_pack_contracts.py tests/test_ucp_m365_pack_client.py` returns `56 passed`.
- `P6` UCP Pack Contract And Local Lifecycle - **Complete** (2026-04-26). Updated `src/ucp_m365_pack/client.py` to add `M365_RUNTIME_URL` (and `SMARTHAUS_M365_RUNTIME_URL`) env support, `_configured_runtime_url()` and `_http_runtime_invoke()`, and a routing-snapshot that reports `selected_live_path = http_runtime` when the runtime URL is configured (preferred over `http_service`, then `stub`, then `unavailable`). `execute_m365_action()` now calls the standalone runtime first when `M365_RUNTIME_URL` is set, falls back to the legacy ops-adapter, then to stub mode, then fails closed with `m365_executor_unavailable`. Updated `src/ucp_m365_pack/setup_schema.json` to declare the Microsoft Graph auth fields (`M365_TENANT_ID`, `M365_CLIENT_ID`, `M365_AUTH_MODE`, `M365_REDIRECT_URI`, `M365_DEVICE_CODE_FALLBACK`, `M365_APP_ONLY_CLIENT_SECRET_REF`, `M365_APP_ONLY_CERTIFICATE_REF`, `M365_TOKEN_STORE`, `M365_KEYCHAIN_SERVICE`, `M365_ENCRYPTED_PACK_LOCAL_ALLOWED`, `M365_GRANTED_SCOPES`, `M365_RUNTIME_URL`) with `M365_TENANT_ID`/`M365_CLIENT_ID`/`M365_AUTH_MODE`/`M365_SERVICE_ACTOR_UPN` required and `M365_AUTH_MODE` constrained to the allowed enum (no `password`). Added the no-cross-repo verifier `scripts/ci/verify_standalone_graph_runtime_pack.py` running six checks (C1 runtime layout, C2 no forbidden tokens outside `_forbidden_tokens.py`, C3 no `ops_adapter`/`smarthaus_graph` imports, C4 setup schema fields, C5 client routes runtime-first and never claims direct import, C6 manifest description / capability claim) and emitted `configs/generated/standalone_graph_runtime_pack_verification.json` with `overall_ok=true`. Combined regression with `smarthaus_mcp_sdk` resolved on PYTHONPATH returns `56 passed` across runtime + legacy ucp_m365_pack tests.
- `P7` Packaging And Distribution - **Complete** (2026-04-26). Built the real standalone Graph runtime marketplace artifact `com.smarthaus.m365@1.1.0`. Added `scripts/ci/build_standalone_graph_runtime_pack.py` which (a) stages payload from `src/ucp_m365_pack/` and `src/m365_runtime/` into `dist/m365_pack/_payload_stage/` plus `setup_schema.json`, `registry/agents.yaml`, and a generated `registry/action_registry.yaml`; (b) emits `payload.tar.gz` (24 KB) and a manifest with `schema_version=0.2.0`, declared `runtime` block (module, entrypoint command, host/port, health/auth/actions/invoke paths, `read_only=true`, `mutation_fence=true`), expanded capabilities (`m365_runtime`, `m365_directory`, `m365_sites`, `m365_users`, `m365_groups`, `m365_teams`, `m365_drives`, `m365_email_health`, `m365_calendar_health`, `m365_servicehealth`), and a SHA256 content_digest tied to the payload bytes; (c) emits detached `signatures/manifest.sig` and `signatures/payload.sig`, full conformance evidence with 14 checks including a new `runtime_contract`, `read_only_contract`, and `no_source_repo_dependency_contract`; (d) builds the final `com.smarthaus.m365-1.1.0.ucp.tar.gz` (28 KB), emits `dist/m365_pack/SHA256SUMS` and `dist/m365_pack/provenance.json`; (e) installs to `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/1.1.0/` with bundle, `manifest.json`, `conformance.json`, regenerated `SHA256SUMS`, `provenance.json`, and a refreshed `README.md`. Provenance records `runtime_packaged=true` and `graph_runtime_in_payload=true`. Acceptance covered by `tests/test_m365_runtime_p7_packaging.py` (`8 passed`): dist layout exists, payload contains `m365_runtime/{__init__,launcher,auth/oauth,auth/app_only,auth/token_store,graph/{client,errors,registry,actions},health,audit,_forbidden_tokens}.py` plus the UCP-facing client+contracts, registry, and setup schema; manifest declares `runtime.module`, entrypoint command, read_only and mutation_fence; SHA256SUMS values match each file; install dir contains all required artifacts; the bundle extracts and the runtime imports + `plan_launch().outcome == "started"` from the extracted location with no `M365_REPO_ROOT` and no source-repo on PYTHONPATH; provenance records the runtime-packaged claims. Combined regression `PYTHONPATH=src:/Users/smarthaus/Projects/GitHub/UCP-codex-stable/src pytest tests/test_m365_runtime_p4_runtime_and_auth.py tests/test_m365_runtime_p5_graph_actions.py tests/test_m365_runtime_p5_launcher_app.py tests/test_m365_runtime_p7_packaging.py tests/test_ucp_m365_pack_contracts.py tests/test_ucp_m365_pack_client.py` returns `64 passed`.
- `P8` UCP Marketplace Activation Boundary - **Complete (M365-side handoff)** (2026-04-26). Published the M365-side handoff packet at `docs/commercialization/m365-standalone-graph-runtime-integration-pack-ucp-handoff-packet.md`. The packet locks pack identity (`com.smarthaus.m365@1.1.0`, bundle SHA `02dfccba...397cb5d`, manifest SHA `47497d93...a1ea993`, conformance SHA `5d0c5470...c60bcdf09`), payload inventory, the launch contract (`python -m m365_runtime` from the install root, default `127.0.0.1:9300`, fixed health/auth/action endpoint paths, `read_only=true`, `mutation_fence=true`), the setup contract with required Graph fields and explicit password rejection, the auth contract endpoints, the readiness/action/lifecycle contracts, the recommended UCP-side plan name `plan:ucp-m365-standalone-graph-runtime-pack-activation` and its bounded scope, the boundary lock recap (M365 owns Graph; UCP owns marketplace lifecycle; neither mutates the other), and the predecessor evidence chain. M365 does not mutate UCP source under this plan; live UCP install/launch/setup/auth/action acceptance must be opened in a separate UCP-owned plan. As a truthful boundary, no UCP-side `plan:ucp-m365-standalone-graph-runtime-pack-activation` exists in `/Users/smarthaus/Projects/GitHub/UCP/plans/` at the time of writing.
- `P9` Acceptance Evidence And Release - **Complete** (2026-04-26). Added the acceptance harness `scripts/ci/acceptance_standalone_graph_runtime_pack.py` which extracts the installed pack into a tmp dir and runs a fresh Python child whose `PYTHONPATH` excludes the M365 source repo. The child verifies SHA256SUMS integrity, imports `m365_runtime` from the extracted bundle, plans a launch with `outcome=started`, calls `invoke()` for `graph.org_profile` against an `httpx.MockTransport` that returns 200 (status_class=`success`), calls `invoke()` for `graph.users.create` (write action not in the read-only registry) and asserts `status_class=mutation_fence`, validates that an injected `client_secret` param is `[redacted]` in the audit envelope, and asserts pre-sign-in readiness `state=not_ready` with `label=auth`. The harness writes machine-readable evidence to `artifacts/diagnostics/m365_standalone_graph_runtime_pack_acceptance.json`. During P9 development the harness exposed a real fail-closed gap: the prior `invoke()` returned `internal_error` for unknown action IDs; the runtime now correctly fails closed with `mutation_fence`, the P5 unit tests are updated to match (`test_invoke_denies_unknown_action_with_mutation_fence`), and the pack was rebuilt to bundle SHA `9cef1985...95c8b7`. Final acceptance: 10/10 clauses pass and **release decision = GO** for `com.smarthaus.m365@1.1.0`. Evidence summary in `docs/commercialization/m365-standalone-graph-runtime-integration-pack-acceptance-evidence-and-release.md`. Live UCP through-the-installed-pack acceptance remains the explicit scope of the sibling UCP plan. Combined regression `PYTHONPATH=src:/Users/smarthaus/Projects/GitHub/UCP-codex-stable/src pytest tests/test_m365_runtime_p4_runtime_and_auth.py tests/test_m365_runtime_p5_graph_actions.py tests/test_m365_runtime_p5_launcher_app.py tests/test_m365_runtime_p7_packaging.py tests/test_ucp_m365_pack_contracts.py tests/test_ucp_m365_pack_client.py` returns `64 passed`.
- `P10` Operations, Rollback, And Maintenance - **Complete** (2026-04-26). Published the operations runbook at `docs/commercialization/m365-standalone-graph-runtime-integration-pack-operations-runbook.md` covering: P10A operator runbook (setup, sign-in, health/readiness, action invocation, logs, restart, support boundaries); P10B token recovery (`POST /v1/auth/clear`, `security delete-generic-password`, encrypted_pack_local file removal, app-only secret/certificate rotation, full local-state reset); P10C rollback (UCP-driven version replacement with fail-safe behavior if previous version cannot launch); P10D version migration (additive setup schema policy across `1.x`; version-tagged token-store policy; refresh-token invalidation handling); P10E support evidence policy (what to attach, the explicit forbidden list of token/secret/private-key materials, redaction-defect handling); P10F roadmap gate (write actions, webhooks, subscriptions, SaaS hosting, UCP-side UX, marketplace publication all require new governed plans). The M365-side standalone Graph runtime integration pack program is now complete end-to-end; the artifact is GO at `com.smarthaus.m365@1.1.0`. Live UCP through-the-installed-pack acceptance remains the explicit scope of the sibling UCP plan.

## Execution Outcome (Updated)

- **Decision:** `P0` complete; `P1` activated under explicit user-authorized continuation.
- **Approved by:** User authorized plan creation with "go build the plan" and full-plan execution with the 2026-04-25 standing instruction "continue through the whole plan unless there is a hard blocker" (treat governance errors as the next remediation task, do not bypass).
- **Phase 0 completion timestamp:** 2026-04-25 EDT.
