# Phase 2 Calculus — M365 Contract Variables and Boundary Conditions

Plan refs: `plan:m365-ma-scorecard-alignment:R2`, `plan:m365-ma-scorecard-alignment:R5`

## Variables

- `a` — requested instruction action
- `p` — normalized parameter object
- `h` — request headers and auth context
- `i` — idempotency key
- `sigma` — tenant and runtime state
- `g` — governance flags such as mutation gate and audit enablement
- `kappa` — runtime configuration authority state
- `r` — instruction response
- `q` — emitted audit record set

## Operators

- `normalize(a, p)` — request normalization as implemented by the instruction router
- `allow_mutation(g, a)` — mutating action gate
- `auth_ok(h)` — CAIO API key and session gate
- `hash(a, p)` — idempotency request hash
- `shape(r)` — response-shape check against the contract
- `audit(q)` — one-record-per-request audit emission
- `resolve_cfg(kappa)` — runtime config resolution under tenant selection and bootstrap inputs
- `parse_ok(v)` — parser and YAML-loader acceptance for the narrow blocker-recovery surface
- `ruff_ok(tau)` — Ruff acceptance over the scoped tooling surface `tau`
- `format_ok(phi)` — formatter acceptance over the scoped runtime or notebook surface `phi`
- `stub_env_ok(psi)` — typing-stub availability over governed third-party imports `psi`
- `module_unique(mu)` — unique module-name resolution for governed Python sources `mu`
- `mypy_actionable(theta)` — Mypy output over the governed path without environment or duplicate-module blockers
- `approval_cfg(alpha)` — approval target resolution from the selected tenant contract with env compatibility fallback
- `approval_auth(epsilon)` — approval Graph token acquisition through the tenant-selected app-only executor path
- `app_roles(omega)` — separation between operator-identity and executor app registrations
- `exec_cred(lambda)` — credential mode of the executor app registration under the selected tenant contract

## Boundary Conditions

1. Unknown action is rejected fail-closed.
2. Missing required auth is rejected fail-closed.
3. Mutating actions remain blocked when mutation gating is disabled.
4. Idempotency replay returns the cached successful result for the same logical request.
5. Successful and unsuccessful executions both produce audit evidence under the audit invariant.
6. When `UCP_TENANT` is selected, production credential and org-mapping authority resolve from tenant config plus injected secret env fallback, not bootstrap dotenv values.
7. Repo-wide validation cannot advance while the known parse-blocker surface is not loadable by Python and YAML tooling.
8. Repo-wide validation cannot advance to runtime/notebook or full-closure acts while the pinned scripts and CI Ruff surface remains non-green.
9. Repo-wide validation cannot advance to Mypy or final closure while the pinned runtime, CLI, governed-test, and notebook formatter surface remains non-green.
10. Repo-wide validation cannot advance to targeted or full closure while the governed Mypy path still fails on missing stubs or duplicate module discovery.
11. Standalone `C1A` approval readiness cannot advance while approval target resolution depends solely on ad hoc shell inputs instead of the selected tenant contract or explicit compatibility fallback.
12. Standalone `C1A` approval readiness cannot advance while the approval backend authenticates through a parallel env-only credential path instead of the tenant-selected app-only executor contract.
13. Standalone `C1A` certification cannot advance while the SMARTHAUS operator-identity app and executor app remain role-ambiguous or while the executor app lacks an explicit certificate-cutover contract.

## Stability and Determinism

Within fixed repository state and fixed normalized inputs:

1. The supported action set is stable.
2. Contract verification artifacts are stable.
3. The response and audit contract is deterministic for the currently proven instruction surface.

The determinism bridge for governance alignment is rooted in:

- `notebooks/m365/INV-M365-C-001-determinism.ipynb`
- the stable intersection of contract, registry, and router action surfaces

## Lemma Mapping

- `L1` — response postcondition and result-shape compliance
- `L2` — idempotency replay stability
- `L3` — authentication fail-closed behavior
- `L4` — audit one-record-per-request behavior
- `L5` — deterministic action-surface and contract replay stability
- `L6` — tenant-selected runtime config authority precedence
- `L7` — validation-blocker syntax recovery for the repo-wide quality gate
- `L8` — scripts and CI Ruff cleanup remains scope-bounded while removing the pinned tooling debt
- `L9` — runtime, CLI, governed-test, and notebook validation cleanup remains scope-bounded while removing the pinned execution-surface debt
- `L10` — Mypy remediation remains scope-bounded while eliminating missing-stub and duplicate-module blockers on the governed path
- `L13` — SMARTHAUS enterprise certification remains blocked until the Entra app registrations are role-separated and the executor certificate-cutover contract is explicit
