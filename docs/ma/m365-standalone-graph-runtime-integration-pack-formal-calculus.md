# M365 Standalone Graph Runtime Integration Pack - P1 Formal Calculus

**Plan:** `plan:m365-standalone-graph-runtime-integration-pack:R2`
**Phase:** `P1` Governing Formula And Formal Calculus
**Date:** 2026-04-25
**Owner:** SMARTHAUS
**Predecessors:** P0A autopsy + P0B/C/D/E intent and boundary lock.
**Notebook evidence:** `notebooks/m365/INV-M365-DL-standalone-graph-runtime-pack-p1-formal-calculus-v1.ipynb`
**Generated verification:** `configs/generated/standalone_graph_runtime_integration_pack_p1_formal_calculus_v1_verification.json`

This document formalizes the readiness, action-execution, and failure-class predicates that govern the standalone M365 Graph runtime integration pack. P1 produces calculus only, no implementation code.

## P1A - Domains

We fix the following finite domains.

| Symbol | Domain | Description |
| --- | --- | --- |
| `p` | `Pack` | A packaged marketplace artifact `(manifest, payload, signatures, evidence, sha256sums)`. |
| `r` | `InstalledRoot` | The filesystem path the artifact has been extracted to (e.g. `/Users/smarthaus/Projects/GitHub/IntegrationPacks/M365/<version>`). |
| `c` | `SetupConfig` | Operator-supplied tenant ID, client ID, auth mode, redirect/device-code policy, app-only credential references, actor UPN, scope manifest. Username/password is not a member of `SetupConfig`. |
| `u` | `UcpHost` | The marketplace host that resolves the pack's contracts. |
| `A` | `ActionSet` | Finite set of declared action IDs. Each `a ∈ A` carries `(workload, endpoint_family, auth_mode, scopes, risk, rw_class)`. |
| `h` | `HealthVector` | Tuple `(svc, auth, tok, graph, perm, ctr)` of last observed health probes for service, auth, token, Graph, permission matrix, and contract resolution. |
| `s` | `AuthState` | One of `unconfigured`, `consent_pending`, `signed_in`, `expired`, `revoked`, `error`. |
| `t` | `Token` | An opaque, securely stored credential. Tokens are values; they are never persisted as plain text and never logged. |
| `g` | `GraphResponse` | A normalized response `(status_class, retry_after, correlation_id, body_class)`. |
| `e` | `Event` | An audit envelope `(actor, action, before_after_redacted, status_class, correlation_id, time)`. |

`SetupConfig` is constrained: `auth_mode ∈ {auth_code_pkce, device_code, app_only_secret, app_only_certificate}`. `auth_mode = password` is rejected at validation (and therefore not a member). `scopes` is a finite subset of Microsoft Graph permission names declared at packaging time.

## P1B - Readiness Formula

`Ready : Pack × SetupConfig × InstalledRoot × UcpHost × ActionSet × HealthVector → {true, false}`

```
Ready(p, c, r, u, A, h) =
    ArtifactSelfContained(p, r)
  ∧ RuntimeLaunchable(p, r)
  ∧ AuthConfigured(c)
  ∧ TokenStoreSafe(c, r)
  ∧ GraphReachable(c, h)
  ∧ PermissionsSufficient(A, c, h)
  ∧ UcpContractsResolvable(p, u)
  ∧ AuditComplete(A, h)
  ∧ NoSourceRepoDependency(p, r)
```

Each conjunct is itself a deterministic predicate over locally observable inputs.

### Readiness predicate clauses

- **`ArtifactSelfContained(p, r)`** ≡ for every member `m` of `p.payload`, `m` exists at `r/m`, and the runtime modules under `r` resolve their imports without traversing outside `r`. Mathematically:
  `∀ m ∈ payload(p): exists(r/m) ∧ ∀ runtime_import x: resolved_path(x, r) ⊆ r`.
- **`RuntimeLaunchable(p, r)`** ≡ launching `p.entrypoint` from `r` produces a deterministic state in `{started, port_conflict, config_invalid, dependency_missing, launch_unknown}`. The function is total: there is no silent state.
- **`AuthConfigured(c)`** ≡ `c.tenant_id ≠ ∅ ∧ c.client_id ≠ ∅ ∧ c.auth_mode ∈ AllowedAuthModes ∧ required_credential_refs(c.auth_mode) ⊆ c`. `password` is not in `AllowedAuthModes`.
- **`TokenStoreSafe(c, r)`** ≡ `token_store(c, r) ∈ {keychain, encrypted_pack_local}` and no token, secret, refresh token, authorization code, client secret, or certificate private key appears in `logs(r)`, `audit(r)`, or `evidence(r)`.
- **`GraphReachable(c, h)`** ≡ `h.graph ∈ {ok, throttled_recoverable}` and the most recent matched-filter probe of Microsoft Graph `/me` (delegated) or `/organization` (app-only) returned `2xx` within the bounded retry budget.
- **`PermissionsSufficient(A, c, h)`** ≡ `∀ a ∈ A_bound: required_scopes(a) ⊆ granted_scopes(c, h)`. `A_bound` is the subset of declared actions activated by setup.
- **`UcpContractsResolvable(p, u)`** ≡ `u` resolves the pack's `setup`, `auth`, `health`, `readiness`, `action`, and `lifecycle` contracts entirely from `p` at `r`. UCP imports neither Microsoft Graph code nor `M365_REPO_ROOT`.
- **`AuditComplete(A, h)`** ≡ every observed transition in `setup ∪ auth ∪ action ∪ lifecycle` produced a record in `audit(r)` with redaction.
- **`NoSourceRepoDependency(p, r)`** ≡ for every runtime read `read(path)` performed by `p` at `r`, `path ⊆ r`. There is no read of `M365_REPO_ROOT`, `../M365`, or `<sibling>/registry/agents.yaml`.

If any clause is `false` or `unknown`, `Ready = false`. There is no partial credit.

## P1C - Action Execution Function

`Execute : Action × Actor × AuthState × Policy × GraphState → Result`

```
Result = Success(payload, audit)
       | Denial(reason, audit)
       | Pending(reason, audit)

Execute(a, actor, s, P, G):
    if s ∉ {signed_in}                                  ⇒ Denial(auth_required, audit)
    if a ∉ ActionSet                                    ⇒ Denial(unknown_action, audit)
    if required_scopes(a) ⊄ granted_scopes(s)           ⇒ Denial(permission_missing, audit)
    if rw_class(a) ≠ read ∧ ¬mutation_governance(a)     ⇒ Denial(mutation_fence, audit)
    if ¬policy_admit(a, actor, P)                       ⇒ Denial(policy_denied, audit)
    if ¬reachable(G)                                    ⇒ Denial(graph_unreachable, audit)
    g = graph_call(a, actor, G)
    case g of
        2xx                                              ⇒ Success(normalize(g), audit)
        throttled within budget                          ⇒ retry; recurse with same arguments
        throttled exhausted                              ⇒ Denial(throttled, audit)
        4xx without scope reason                         ⇒ Denial(forbidden, audit)
        4xx with scope reason                            ⇒ Denial(permission_missing, audit)
        5xx                                              ⇒ Denial(graph_unreachable, audit)
        anything else                                    ⇒ Denial(internal_error, audit)
```

`audit` is built from the bounded audit envelope `(actor, action, before_after_redacted, status_class, correlation_id, time)`. The function is total: every `Graph` outcome maps to exactly one branch above. `Pending` is reserved for actions that require human approval (currently empty for read-only acceptance).

The mutation fence is enforced inside `Execute`: until a separate mutation-governance plan supplies `mutation_governance(a) = true` for a given write action, write actions resolve to `Denial(mutation_fence, audit)`.

## P1D - Failure Lattice

The failure lattice fixes the named outcomes and their partial order. Every action, readiness, and health response resolves to exactly one node.

```
                              success
                                 │
              ┌──────────────────┼─────────────────────┐
              │                  │                     │
         not_configured     auth_required        consent_required
              │                  │                     │
              └──────┬───────────┘                     │
                     │                                 │
              permission_missing ◄─────────────────────┘
                     │
                throttled
                     │
              graph_unreachable
                     │
                policy_denied
                     │
                mutation_fence
                     │
               internal_error
```

**Reading rule.** A higher-up node is "less bad" (closer to success). When two predicates fail simultaneously, the runtime reports the *highest* node that is still not satisfied, so operators get the fix-first signal. For example, if both `auth_required` and `permission_missing` are unsatisfied, the response carries `auth_required`.

**Disjointness.** No state is silently ambiguous. Implementations must implement a total function from internal state to one lattice node and never emit an unspecified response.

**Boundary node `success`.** `success` is reached only when no other node is true. `Ready=true` is `success` of the readiness predicate; `Execute` reaches `Success(...)` only when no denial node fires.

## P1E - Deterministic Boundaries For OAuth/Graph Nondeterminism

The runtime is deterministic where it can be, and explicitly bounds nondeterministic surfaces.

### Time bounds

- Service launch: `≤ 5 s` to `started` or to a non-`launch_unknown` lattice node.
- Health probe round-trip: `≤ 10 s` per band (service / auth / token / graph / permission / contract).
- Graph call default timeout: `≤ 30 s`. Per-action override permitted up to `≤ 60 s`.
- Token refresh: `≤ 15 s`.

### Retry budgets

- Graph 5xx: at most 2 retries, exponential backoff `1s, 4s`. Throttled `Retry-After` honored up to 30 s with at most 2 retries. Beyond budget, fail closed to `throttled` or `graph_unreachable`.
- Token refresh: at most 1 retry. Beyond budget, fail closed to `auth_required`.

### Cryptographic randomness

- PKCE code verifier: 32 bytes from `os.urandom`. Tests are forbidden from seeding production randomness.
- OAuth state and nonce: 16 bytes from `os.urandom`. Same prohibition.
- Tests use mocked auth providers and redacted fixtures. Test-only deterministic `Token` values are tagged and rejected by production validators.

### Replay and fixtures

- All deterministic tests use replay fixtures with stable `correlation_id`, fixed wall clock, and recorded Graph responses.
- Live acceptance is gated behind explicit user approval; results are audited but not used to seed deterministic tests.

### Audit redaction policy

- `Authorization` headers, `client_secret`, `refresh_token`, `code`, `id_token`, `assertion`, `access_token`, certificate `private_key`, and any field whose name matches `(?i)token|secret|password|assertion|certificate.*key|private.*key|authorization` MUST be redacted to a fixed sentinel `[redacted]` before any audit, log, evidence, or notebook artifact is emitted.

## P1F - Composition Theorem (Statement, Proof Sketch)

**Theorem (Standalone Readiness Composition).** Let `R(p,c,r,u,A,h) = Ready(...)` from P1B. Then `R = true` implies that an arbitrary read-only action `a ∈ A_bound` either succeeds via Microsoft Graph or terminates in a node strictly weaker than `success` from the failure lattice (no implicit success).

**Proof sketch.** From `Ready=true`, all nine conjuncts hold. Pick any `a ∈ A_bound`. By `AuthConfigured`, `s = signed_in`. By `PermissionsSufficient`, `required_scopes(a) ⊆ granted_scopes(s)`. By `GraphReachable`, the most recent probe is in `{ok, throttled_recoverable}`. `Execute(a, actor, s, P, G)` therefore cannot return `Denial(auth_required)`, `Denial(permission_missing)` (modulo Graph-side scope drift, which is reported as `permission_missing` and is the operator's signal), or `Denial(graph_unreachable)` purely from local state. The remaining branches of `Execute` are exhaustive over `Graph` outcomes and produce a `Success` or a strictly weaker lattice node, hence the conclusion. ∎

This theorem is what the readiness contract is allowed to claim. It does **not** claim Microsoft Graph itself is healthy globally; it claims that a successful read of `Ready` plus a successful per-action call resolves to one of the declared outcomes deterministically.

## Interaction With Existing Repo Math

The repo already has phase 1/2 calculus documents `docs/ma/phase1_formula.md` and `docs/ma/phase2_calculus.md` for earlier programs. Those documents address the M365 governance/persona action surface and remain authoritative for that work. This P1 calculus is scoped narrowly to the standalone Graph runtime integration pack and does not modify or contradict the prior calculus.

## Closure

- `P1A` Domains - locked.
- `P1B` Readiness formula - locked with nine conjunctive clauses.
- `P1C` Action execution function - total function over the failure lattice.
- `P1D` Failure lattice - exhaustive named outcomes with disjointness rule.
- `P1E` Deterministic boundaries - timeouts, retry budgets, cryptographic randomness rules, replay policy, redaction policy.
- `P1F` Composition theorem - stated and proof-sketched.
- This document closes phase `P1`. Phase `P2` (Lemmas And Machine Invariants) is the next bounded act.
