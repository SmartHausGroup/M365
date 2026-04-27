# Lemma L98: M365 Standalone Graph Runtime Pack Lemmas v1

**Plan reference:** `plan:m365-standalone-graph-runtime-integration-pack:R3`
**Phase:** `P2` Lemmas And Machine Invariants
**Date:** 2026-04-26
**Notebook reference:** `notebooks/m365/INV-M365-DM-standalone-graph-runtime-pack-p2-lemmas-v1.ipynb`
**Lemma proof reference:** `notebooks/lemma_proofs/L98_m365_standalone_graph_runtime_pack_lemmas_v1.ipynb`
**Scorecard reference:** `artifacts/scorecards/scorecard_l98.json`
**Generated verification reference:** `configs/generated/standalone_graph_runtime_integration_pack_p2_lemmas_v1_verification.json`

This lemma bundles the seven binding obligations the standalone M365 Graph runtime integration pack must satisfy. They are derived from the P1 formal calculus and decompose `Ready` into machine-checkable parts.

## L-STANDALONE - Installed artifact requires no source repo

### Statement
The runtime behavior of an installed pack at root `r` does not require the M365 source repository. For every runtime read path `path` produced at `r`, `path ⊆ r`. The runtime does not consult `M365_REPO_ROOT`, `SMARTHAUS_M365_REPO_ROOT`, `../M365`, or any sibling-repo path. Renaming, hiding, or removing the M365 source repo on the host does not change runtime behavior at `r`.

### Boundary
- Test/build tooling outside the runtime is permitted to read the source repo.
- The packaged registry must be inside `r`, not loaded from the source.

### Failure modes (rejected)
- Pack imports load the source `src/` tree.
- Pack uses `M365_REPO_ROOT` or walks parent directories searching for `registry/agents.yaml` or `src/ops_adapter`.
- Pack reads tenants from `UCP_ROOT`, `REPOS_ROOT`, or any `<sibling>/tenants` path that escapes `r`.

## L-LAUNCH - Installed artifact deterministically launches or reports a launch error

### Statement
Launching the runtime entrypoint at `r` produces exactly one outcome from the launch lattice `{started, port_conflict, config_invalid, dependency_missing, launch_unknown}` within `≤ 5 s`. There is no silent state.

### Boundary
- `started` requires a healthy local listener and a passing readiness probe attempt.
- `launch_unknown` is reserved and must be unreachable in tests; observing it in production is itself a defect signal.

### Failure modes (rejected)
- Launch hangs without a deadline.
- Launcher crashes without producing a launch lattice node.
- Launch claims success while the listener is not bound.

## L-AUTH - Auth setup never stores passwords and never exposes tokens

### Statement
For every accepted setup config `c`, `c.auth_mode ∈ {auth_code_pkce, device_code, app_only_secret, app_only_certificate}`. No code path produces or persists a username/password Microsoft credential. No token, secret, refresh token, authorization code, client secret, or certificate private key appears in logs, audit, evidence, or notebook artifacts.

### Boundary
- Operator/admin credential handling for Azure portal flows is outside this lemma.
- Tokens may exist in encrypted Keychain or in the explicitly approved encrypted pack-local store.

### Failure modes (rejected)
- `auth_mode = password` admitted at validation.
- Plain token text appears in any artifact under `r`.
- Token stored in plain file or in an encrypted store that the lemma did not approve.

## L-PERMISSIONS - Each action declares required Graph scopes/roles and fails closed when absent

### Statement
For every action `a ∈ A`, the action registry binds `required_scopes(a)` (delegated mode) or `required_roles(a)` (app-only mode). For every invocation, when the bound scopes/roles are not present in the current auth state, `Execute` returns `Denial(permission_missing, audit)` and never performs a Graph call.

### Boundary
- Per-tenant Graph policy that revokes scopes after grant is reported as `permission_missing` to the operator and is not interpreted as a runtime defect.

### Failure modes (rejected)
- Action invokes Graph without checking declared scopes/roles.
- Action returns `success` while the Graph response indicates a scope problem.
- Action declares no required scope/role.

## L-READINESS - Readiness is true only when all predicates hold

### Statement
The runtime returns `Ready=true` if and only if every clause of the P1 readiness predicate evaluates to `true` from observed local state. Unknown, missing, partially observed, or stale predicates resolve to `false`.

### Boundary
- Cached readiness values must carry an expiry; stale cache forces re-probe before reporting `true`.

### Failure modes (rejected)
- Returning `Ready=true` when any clause is `unknown`.
- Returning `Ready=true` based solely on absence of error.
- Returning `Ready=true` from an external opinion (e.g., UCP cache) without a fresh local probe.

## L-AUDIT - Every transition produces a bounded audit record

### Statement
Every observed transition in the union of `setup ∪ auth ∪ health ∪ action ∪ lifecycle` produces exactly one audit envelope `(actor, action, before_after_redacted, status_class, correlation_id, time)`. The redaction regex from P1E is applied before any record is written, logged, or exported.

### Boundary
- Performance counters and connection-pool internals are not part of the audit envelope unless explicitly attached.
- The audit envelope size has a fixed upper bound (8 KB before encoding) to prevent log-channel abuse.

### Failure modes (rejected)
- A state transition produces no audit record.
- An audit record is written before redaction.
- Two records cover the same transition (duplicate audit).

## L-PACKAGING - Artifact checksums, signatures, evidence, and payload inventory match the manifest

### Statement
For every released artifact `(manifest, payload, signatures, evidence, sha256sums)`:

- `sha256sums` matches the bytes of `manifest.json`, the bundle file, and the conformance evidence file.
- `signatures/manifest.sig` and `signatures/payload.sig` digest-align with the manifest and payload, respectively.
- `manifest.content_digest.value` equals the SHA256 of the canonicalized payload contents.
- `evidence/conformance.json` includes a `payload_sources_contract` check that lists every payload member declared in the manifest.

If any of these properties is false, the bundle is non-conformant and must be rebuilt.

### Boundary
- Reproducible-build determinism requires lockfiles and stable `tar` ordering, which the build script must enforce.
- This lemma does not address marketplace publication, only the local artifact and its installed copy.

### Failure modes (rejected)
- Drift between the bundled `payload.tar.gz` digest and `content_digest.value`.
- Missing or stale `signatures/*.sig`.
- `SHA256SUMS` includes files not present in the artifact, or omits files present in the artifact.

## Bundled Statement (combined predicate)

```
StandaloneRuntimeTruth(p, c, r, u, A, h)
  := L_STANDALONE(p, r)
   ∧ L_LAUNCH(p, r)
   ∧ L_AUTH(c, r)
   ∧ L_PERMISSIONS(A, c, h)
   ∧ L_READINESS(p, c, r, u, A, h)
   ∧ L_AUDIT(A, h)
   ∧ L_PACKAGING(p)
```

`StandaloneRuntimeTruth = true` is the precondition for asserting that the standalone Graph runtime integration pack is shippable at any version.

## Determinism

- Each lemma is statable as a deterministic predicate over locally observable inputs.
- Each lemma's failure mode list is exhaustive and disjoint within the lemma.
- Each lemma's tests in P3 will return only `pass`/`fail`, never `unknown`.

## Proof Sketch

The seven lemmas correspond exactly to the seven obligations the integration must keep simultaneously: self-containment of the artifact, deterministic launch behavior, auth-mode safety, permission sufficiency, readiness honesty, audit completeness, and packaging integrity. Each lemma reduces a specific clause of the P1 readiness predicate to a checkable obligation, and each clause's failure mode is a known root cause from the current artifact (P0) or from prior governed remediation work in this repo (e.g., ops-adapter source-tree dependency, missing scope checks). Their conjunction is necessary for `Ready=true` and sufficient for the composition theorem from P1F.
