# Lemma L15 — Tenant Contract and Executor Registry Extension

## Claim

The tenant-selected configuration authority can be extended from a single implicit executor to an explicit executor registry without breaking the current runtime contract if:

1. bounded executor identities are represented in the tenant contract;
2. one deterministic default executor is projected back into the legacy root auth fields; and
3. the migration path from single-executor to bounded-executor posture is explicit.

## Why This Matters

`B7A` is the first runtime act after the `B6` certification rebase. The repo cannot honestly resume certification until the tenant contract can represent the rebased multi-executor target.

## Inputs

- tenant YAML with legacy root `azure` and `auth`
- optional executor registry metadata
- optional bounded executor definitions

## Outputs

- deterministic multi-executor tenant schema
- default-executor projection for backward compatibility
- explicit migration semantics from single executor to bounded executors

## Proof Sketch

If the loader parses bounded executors first, chooses exactly one default executor, and mirrors that executor into the existing root runtime fields, then:

- old runtime readers remain stable;
- new runtime readers can consume the registry directly; and
- the config authority can evolve without split sources of truth.

## Runtime Bindings

- `src/smarthaus_common/tenant_config.py`
- `src/smarthaus_common/config.py`
- `tests/test_env_loading.py`
- `tests/test_approvals.py`

## Failure Boundary

`B7A` fails closed if:

- multiple executors exist but no deterministic default is resolved;
- executor metadata is parsed but not exposed through the tenant config;
- the loader still assumes one executor only.
