# Plan: M365 Auth Persistence Reconnect Remediation

## Section 1: Plan Header

- **Plan ID:** `plan:m365-auth-persistence-reconnect-remediation`
- **Title:** `Repair standalone M365 runtime token hydration, refresh, and reconnect truth`
- **Version:** `1.0`
- **Status:** `Complete-GO`
- **Owner:** `SMARTHAUS`
- **Date Created:** `2026-05-01`
- **Date Updated:** `2026-05-01`
- **Branch:** `codex/m365-auth-persistence-reconnect-remediation`
- **North Star Ref:** `Operations/NORTHSTAR.md`
- **Execution Plan Ref:** `Operations/EXECUTION_PLAN.md § Initiative: M365 Auth Persistence Reconnect Remediation`
- **Domain:** `infrastructure`
- **Math/Algorithm Scope:** `false`

## Section 2: North Star Alignment

- **Source:** `Operations/NORTHSTAR.md`
- **Principles served:**
  - `M365-only tooling with truthful Microsoft Graph execution`
  - `Self-service runtime operation with minimal SMARTHAUS intervention`
  - `99.9% uptime and <2s endpoint posture by avoiding unnecessary re-auth loops`
  - `100% security compliance by keeping tokens in secure storage and never storing passwords`
- **Anti-alignment:**
  - `Does NOT store Microsoft passwords`
  - `Does NOT weaken device-code or PKCE consent requirements`
  - `Does NOT mask expired, revoked, or invalid Microsoft tokens as signed in`
  - `Does NOT mutate sibling UCP repo files`

## Section 3: Intent Capture

- **User's stated requirements:**
  - `Deep dive into the code and provide exact answer, not guesses`
  - `Determine why M365 is not starting properly`
  - `Clarify whether credentials are stored and whether they are reused`
  - `Create a governed plan and execute it start to finish`
- **Intent verification:** The current code proves tokens are stored in the configured token store, but runtime memory starts empty and no startup refresh path exists. This plan remediates that exact code defect.

## Section 4: Objective

Repair the standalone `m365_runtime` authentication lifecycle so delegated auth tokens persisted in the configured token store are deterministically rehydrated and refreshed after runtime restart, and so auth status/readiness/action invocation report `auth_required` truthfully when refresh fails rather than forcing ambiguous repeated user sign-in.

## Section 5: Scope

### In scope

- Runtime startup hydration from `TokenStore`
- Refresh-token based access-token renewal for delegated modes
- Fail-closed auth status reason when stored tokens cannot be refreshed
- Focused regression coverage using in-memory token-store test double and mocked OAuth/Graph transports
- Version/source alignment for a corrected `com.smarthaus.m365@0.1.3` artifact line
- Local deterministic validation and local artifact build/install cache only
- Governance tracker, action-log, and file-index synchronization

### Out of scope

- Publishing a GitHub Release
- Pushing branches or tags
- Mutating UCP repo files
- Tenant permission changes
- Microsoft credential rotation
- Storing username/password credentials
- Adding broad UI work; UCP UI reconnect affordance remains a sibling UCP follow-on after M365 artifact truth is green

### File allowlist

- `plans/m365-auth-persistence-reconnect-remediation/**`
- `docs/prompts/codex-m365-auth-persistence-reconnect-remediation.md`
- `docs/prompts/codex-m365-auth-persistence-reconnect-remediation-prompt.txt`
- `src/m365_runtime/__init__.py`
- `src/m365_runtime/launcher.py`
- `tests/test_m365_runtime_fix_auth_lifecycle.py`
- `tests/test_m365_runtime_0_1_2_readiness_fix.py`
- `tests/test_m365_runtime_p7_packaging.py`
- `scripts/ci/build_standalone_graph_runtime_pack.py`
- `notebooks/m365/INV-M365-DP-auth-persistence-reconnect-v1.ipynb`
- `configs/generated/auth_persistence_reconnect_v1_verification.json`
- `artifacts/diagnostics/m365_standalone_graph_runtime_pack_acceptance.json`
- `artifacts/diagnostics/m365_standalone_graph_runtime_pack_0_1_3_live_smoke.json`
- `dist/m365_pack/**`
- `Operations/EXECUTION_PLAN.md`
- `Operations/ACTION_LOG.md`
- `Operations/PROJECT_FILE_INDEX.md`

### File denylist

- `../UCP/**`
- `registry/**`
- `docs/commercialization/m365-standalone-graph-runtime-integration-pack-0-1-2-*`
- Microsoft tenant configuration or secret material
- Any path outside the allowlist without a separate governed scope correction

## Section 6: Requirements

- **R0 — Governed plan package**
  - Create the plan triplet, prompt pair, execution-plan entry, file-index entries, and action-log entry.
- **R1 — Root-cause lock**
  - Preserve the exact diagnosis: token-store writes exist, startup hydration/refresh does not.
- **R2 — Startup token hydration and refresh**
  - On runtime app construction, load stored token metadata and refresh delegated tokens before reporting signed-in readiness.
- **R3 — Lazy refresh before status/readiness/actions**
  - Before `/v1/auth/status`, `/v1/health/readiness`, and action invocation, refresh an expired or near-expired delegated token when a refresh token exists.
- **R4 — Fail-closed auth state**
  - Never treat an unexpired-proofless stored access token as signed in. If refresh fails, clear in-memory access and return `auth_required` with a truthful reason.
- **R5 — Regression proof**
  - Add focused tests for startup refresh, refresh failure, refresh-token preservation, persisted expiry metadata, and no-token-leak audit behavior.
- **R6 — Corrected artifact line**
  - Move the active local pack build line to `0.1.3` without rewriting the already-published `0.1.2` release authority.
- **R7 — Validation and local build proof**
  - Run targeted tests, package verifier/acceptance where feasible, `git diff --check`, and local `0.1.3` artifact build/cache install.
- **R8 — Governance closeout**
  - Update this plan, execution plan, file index, and action log with the final result.

## Section 7: Execution Sequence

`R0 -> R1 -> R2 -> R3 -> R4 -> R5 -> R6 -> R7 -> R8`

Stop on first hard blocker. If a UCP `validate_action` rule blocks a scoped step because metadata shape is insufficient, repair the metadata shape and retry. If the rule denies the action for a substantive policy reason, stop and report.

## Section 8: Current Root Cause

The active runtime code in `src/m365_runtime/launcher.py` initializes:

- `state["access_token"] = None`
- `state["refresh_token"] = None`
- `state["token_expires_at"] = None`

The runtime stores tokens with `_store_access_token()` after device-code, PKCE, or app-only auth. The configured token store reads and writes through macOS Keychain by default. However, `build_app()` never reads `access_token` or `refresh_token` from that store on startup, and it never calls `refresh_access_token()` before readiness or action invocation. Therefore a restarted runtime has no valid in-memory bearer token even when secure stored credentials exist.

## Section 9: Gates

- **CHECK:C0 — Governance package exists**
  - Plan triplet, prompt pair, execution-plan entry, file-index entry, and action-log entry exist.
- **CHECK:C1 — Root cause remains bounded**
  - The change targets M365 runtime token hydration/refresh only.
- **CHECK:C2 — Secure storage preserved**
  - No password storage, plaintext token files, token logging, or token evidence leakage is introduced.
- **CHECK:C3 — Reconnect behavior proven**
  - A runtime with stored refresh token reaches `signed_in` and invokes Graph with the refreshed bearer token without re-running device-code sign-in.
- **CHECK:C4 — Failure behavior proven**
  - Failed refresh produces `auth_required` and never invokes Graph with stale access tokens.
- **CHECK:C5 — Version/artifact truth preserved**
  - Source/runtime/build metadata agree on corrected local pack line `0.1.3`; historical `0.1.2` release docs remain historical.
- **CHECK:C6 — Validation green**
  - Focused pytest, packaging tests, verifier/acceptance, build, and diff hygiene pass or produce a truthful blocker.

## Section 10: Determinism Requirements

This is not math/algorithm work. Determinism is defined as follows: for fixed token-store contents, fixed mocked OAuth transport responses, fixed mocked Graph responses, and fixed wall-clock token-expiry boundary, the runtime must return the same auth state, readiness state, action status class, and token-store mutations on replay.

## Section 11: Artifacts

- `plans/m365-auth-persistence-reconnect-remediation/m365-auth-persistence-reconnect-remediation.md`
- `plans/m365-auth-persistence-reconnect-remediation/m365-auth-persistence-reconnect-remediation.yaml`
- `plans/m365-auth-persistence-reconnect-remediation/m365-auth-persistence-reconnect-remediation.json`
- `docs/prompts/codex-m365-auth-persistence-reconnect-remediation.md`
- `docs/prompts/codex-m365-auth-persistence-reconnect-remediation-prompt.txt`
- `src/m365_runtime/__init__.py`
- `src/m365_runtime/launcher.py`
- `tests/test_m365_runtime_fix_auth_lifecycle.py`
- `tests/test_m365_runtime_0_1_2_readiness_fix.py`
- `tests/test_m365_runtime_p7_packaging.py`
- `scripts/ci/build_standalone_graph_runtime_pack.py`
- `notebooks/m365/INV-M365-DP-auth-persistence-reconnect-v1.ipynb`
- `configs/generated/auth_persistence_reconnect_v1_verification.json`
- `artifacts/diagnostics/m365_standalone_graph_runtime_pack_acceptance.json`
- `artifacts/diagnostics/m365_standalone_graph_runtime_pack_0_1_3_live_smoke.json`
- `dist/m365_pack/manifest.json`
- `dist/m365_pack/payload.tar.gz`
- `dist/m365_pack/evidence/conformance.json`
- `dist/m365_pack/signatures/manifest.sig`
- `dist/m365_pack/signatures/payload.sig`

## Section 12: Environment

- **Python:** `.venv/bin/python`
- **Test runner:** `.venv/bin/pytest`
- **Runtime dependencies:** existing M365 runtime dependency set
- **External systems:** Microsoft Graph is mocked for focused regressions; local artifact build does not call Microsoft Graph.
- **Secrets:** No secret or token material may be committed, logged, or written into evidence.

## Section 13: Implementation Approach

- **Option A:** Hydrate stored access tokens directly and report signed in.
  - **Pros:** minimal code
  - **Cons:** unsafe because existing stored access tokens may be expired and expiry metadata may be missing
- **Option B:** Always force user sign-in on every restart.
  - **Pros:** simplest security posture
  - **Cons:** fails self-service reliability and ignores existing secure refresh-token storage
- **Option C:** Use stored refresh tokens to mint a fresh access token on startup and before expiry; fail closed on refresh failure.
  - **Pros:** matches Microsoft delegated OAuth lifecycle, uses secure token store, avoids repeated device-code login, and remains fail-closed
  - **Cons:** requires careful tests around token expiry and refresh failure
- **Chosen:** `Option C`
- **Rationale:** It is the only option that both reuses stored credentials and avoids trusting stale bearer tokens.

## Section 14: Risks and Mitigations

- **Risk:** Refresh failure could be caused by transient network behavior.
  - **Mitigation:** classify as `auth_required` without logging tokens; do not claim signed in.
- **Risk:** Existing users may have only `access_token` and `refresh_token` without stored expiry metadata.
  - **Mitigation:** prefer refresh token and mint fresh access on startup instead of trusting stale access.
- **Risk:** Version bump touches tests and build metadata.
  - **Mitigation:** keep published `0.1.2` docs historical; update active build constants/tests only for `0.1.3`.
- **Risk:** UCP still needs consumer-side UI/admission follow-up.
  - **Mitigation:** declare UCP follow-up as out of M365 scope and hand off after this plan is green.

## Section 15: Rollback

Revert only the allowlisted files changed by this plan. If local `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/0.1.3/` is produced and later rejected, delete only that local cache directory after explicit approval; never delete the existing published `0.1.2` cache.

## Section 16: Prompt References

- **Prompt doc:** `docs/prompts/codex-m365-auth-persistence-reconnect-remediation.md`
- **Prompt kickoff:** `docs/prompts/codex-m365-auth-persistence-reconnect-remediation-prompt.txt`

## Section 17: Traceability

- `plan:m365-auth-persistence-reconnect-remediation:R0` -> governed package creation
- `plan:m365-auth-persistence-reconnect-remediation:R1` -> root cause lock
- `plan:m365-auth-persistence-reconnect-remediation:R2` -> startup hydration/refresh
- `plan:m365-auth-persistence-reconnect-remediation:R3` -> lazy refresh before status/readiness/actions
- `plan:m365-auth-persistence-reconnect-remediation:R4` -> fail-closed auth state
- `plan:m365-auth-persistence-reconnect-remediation:R5` -> regression proof
- `plan:m365-auth-persistence-reconnect-remediation:R6` -> corrected artifact line
- `plan:m365-auth-persistence-reconnect-remediation:R7` -> validation and local build proof
- `plan:m365-auth-persistence-reconnect-remediation:R8` -> governance closeout

## Section 18: Governance Closure

- [x] `Operations/ACTION_LOG.md` updated
- [x] `Operations/EXECUTION_PLAN.md` updated
- [x] `Operations/PROJECT_FILE_INDEX.md` updated
- [x] Plan artifacts synchronized (`.md/.yaml/.json`)
- [x] Prompt pair exists
- [x] Validation result recorded

## Section 19: Execution Outcome

- **R0:** complete — governed package and notebook-backing scope correction created
- **R1:** complete — root cause locked to missing startup hydration/refresh from `TokenStore`
- **R2:** complete — startup hydration refreshes delegated stored refresh tokens and hydrates unexpired access tokens only when expiry metadata is fresh
- **R3:** complete — `/v1/auth/status`, `/v1/health/readiness`, and action invocation run the lazy refresh gate before reporting or invoking Graph
- **R4:** complete — stale or proofless access tokens fail closed as `auth_required`; refresh failure clears in-memory bearer use and does not call Graph with stale tokens
- **R5:** complete — focused regression coverage added for startup refresh, refresh failure, persisted expiry, refresh-token preservation, and delegated stored-token hydration
- **R6:** complete — active local runtime/build/test line moved to `com.smarthaus.m365@0.1.3` without rewriting published `0.1.2` release authority
- **R7:** complete — validation green:
  - `PYTHONPATH=src .venv/bin/pytest -q tests/test_m365_runtime_fix_auth_lifecycle.py tests/test_m365_runtime_0_1_2_readiness_fix.py tests/test_m365_runtime_p5_launcher_app.py tests/test_m365_runtime_p7_packaging.py` -> `44 passed`
  - `.venv/bin/pre-commit run --files src/m365_runtime/__init__.py src/m365_runtime/launcher.py scripts/ci/build_standalone_graph_runtime_pack.py tests/test_m365_runtime_fix_auth_lifecycle.py tests/test_m365_runtime_0_1_2_readiness_fix.py tests/test_m365_runtime_p7_packaging.py` -> passed
  - `.venv/bin/python scripts/ci/build_standalone_graph_runtime_pack.py` -> built and installed `com.smarthaus.m365@0.1.3`, bundle SHA `d26278c6c47a650a8750ff0dc6b914fde418b778395661ebd5bba2f440981c4e`
  - `PYTHONPATH=src .venv/bin/python scripts/ci/verify_standalone_graph_runtime_pack.py` -> `PASSED (9 checks)`
  - `PYTHONPATH=src .venv/bin/python scripts/ci/acceptance_standalone_graph_runtime_pack.py` -> `GO; clauses passed: 21/21`
  - `git diff --check` -> clean
  - Live installed-pack Microsoft smoke -> `GO`: `0.1.3` completed device-code sign-in, live `graph.me`, readiness `ready/success`, restart without reauth, and forced-stale-expiry restart using stored refresh token. Evidence: `artifacts/diagnostics/m365_standalone_graph_runtime_pack_0_1_3_live_smoke.json`
- **R8:** complete — governance closeout synchronized

## Section 20: Live Smoke Finding

- The runtime remediation works live when the configured delegated scope set includes `offline_access`.
- A baseline live run with only `User.Read,Directory.Read.All` completed sign-in, `graph.me`, readiness, and restart while the stored access token was still fresh, but forced-expiry restart failed closed as `auth_required` with reason `lazy_refresh:refresh_token_missing`.
- Therefore the UCP-side setup/admission path must include `offline_access` for true long-lived refresh-token reconnect behavior.
