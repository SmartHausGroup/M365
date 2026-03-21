# M365 Packaging, Install, and Bootstrap

**Status:** `P4A` complete
**Date:** 2026-03-17
**Plan refs:** `plan:m365-enterprise-commercialization-readiness:R5`, `plan:m365-enterprise-commercialization-readiness:P4A`

This document defines the packaging and bootstrap model for standalone M365 v1. It chooses one canonical install path for the current repository state and classifies all other paths as compatibility or development surfaces.

Deterministic packaging rule for this repository state:

`CanonicalStandalonePath = PythonPackageInstall -> m365-server launcher -> app root bootstrap -> tenant-scoped runtime configuration`

If more than one install path is presented as equally canonical, packaging remains commercially ambiguous.

## Package Variants

The current repo supports three relevant packaging shapes, but only one is canonical for standalone commercialization.

### 1. Standalone server application

Classification: **canonical standalone variant**

Characteristics:

1. installed as the `smarthaus-m365` Python package from the M365 distribution root
2. exposes the `m365-server` launcher via `pyproject.toml`
3. runs the ops-adapter as a formal application
4. supports operator bootstrap through app-root inputs and external runtime configuration

Evidence:

1. `pyproject.toml`
2. `src/m365_server/__main__.py`
3. `docs/M365_SERVER_APP.md`

### 2. Embedded TAI licensed module

Classification: **compatible platform variant, not the canonical standalone path**

Characteristics:

1. used when M365 is hosted as a licensed module inside TAI
2. preserves entitlement-driven module behavior and centralized governance
3. is commercially important, but it is not the default standalone install story

Evidence:

1. `docs/TAI_LICENSED_MODULE_MODEL.md`
2. `docs/LOCAL_TEST_LICENSED_RUNTIME.md`
3. `src/m365/module/entrypoint.py`

### 3. Source-tree local development path

Classification: **development-only variant**

Characteristics:

1. repo checkout
2. editable install or direct Python execution
3. suitable for engineering and local validation
4. not the enterprise-facing packaging story

Evidence:

1. `docs/LOCAL_TEST_LICENSED_RUNTIME.md`
2. `docs/enterprise_setup.md`

## Install Path

The one canonical standalone install path for the current repo state is:

1. obtain the M365 distribution root
2. create a dedicated Python 3.14+ virtual environment
3. install the package
4. run `m365-server`
5. point the server at an app root that contains `registry/agents.yaml` and operator bootstrap inputs

### Canonical install sequence

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -e .
m365-server
```

Commercial interpretation:

1. The launcher command is the product entrypoint.
2. `python -m m365_server` is an alternate compatibility invocation, not the primary install story.
3. The TAI-hosted module route is a separate packaging variant, not the canonical standalone onboarding path.

## Bootstrap Flow

The canonical bootstrap flow for the standalone variant is:

1. operator prepares app root
2. app root provides `registry/agents.yaml`
3. runtime resolves `M365_APP_ROOT` or current working directory
4. launcher loads bootstrap `.env` only for local/operator convenience
5. runtime initializes logs and registry path
6. tenant-scoped runtime configuration is then resolved through the commercialization-defined canonical contract

### Bootstrap sequence details

1. Set or select `M365_APP_ROOT`.
2. Ensure app root contains:
   - `registry/agents.yaml`
   - optional bootstrap `.env`
3. Start `m365-server`.
4. Launcher creates `logs/` and sets runtime env for registry/log path.
5. Runtime uses bootstrap inputs to start, while production authority remains tenant-scoped config and secret injection outside committed repo files.

### Canonical bootstrap boundary

Bootstrap `.env` is allowed only as:

1. launcher convenience
2. local operator input
3. local test input

Bootstrap `.env` is not:

1. the authoritative production tenant contract
2. the long-term secret-management model
3. the release-certification evidence source

## Environment Setup

The standalone operator environment should be described in two layers.

### Layer 1 — bootstrap environment

Used to get the server running:

1. `M365_APP_ROOT`
2. `M365_SERVER_HOST`
3. `M365_SERVER_PORT`
4. `LOG_DIR` if overriding the default
5. optional launcher/bootstrap `.env`

### Layer 2 — canonical runtime configuration

Used for the supported production posture:

1. `UCP_TENANT`
2. tenant YAML contract
3. externally injected secret material
4. supported auth mode and governance settings defined in prior commercialization phases

Current commercial rule:

The install process may mention both layers, but production authority belongs to layer 2.

## Prerequisites

The current repo-state standalone packaging path requires:

1. Python 3.14 or newer
2. package installation from the M365 distribution root
3. app root containing `registry/agents.yaml`
4. supported runtime dependencies from `pyproject.toml`
5. operator access to tenant-scoped configuration inputs
6. external secret injection path for production use
7. OPA availability when policy enforcement is part of the target deployment
8. non-production tenant for any write-capable validation

Operational prerequisite notes:

1. The current standalone packaging story assumes operator familiarity with Python package installation.
2. Wheel-only or container-only distribution is not yet the canonical story in the repo today.
3. Packaging implementation remains behind the commercialization docs; this phase only defines the supported path.

## Decision Summary

`P4A` chooses one canonical standalone packaging path for the current repo state:

1. install the Python package
2. launch with `m365-server`
3. bootstrap from app root
4. resolve production identity and governance through tenant-scoped configuration

Residual packaging gaps intentionally deferred:

1. formal release artifact packaging beyond the current Python package surface
2. installer simplification beyond Python-operator workflows
3. operator onboarding and runbooks, which belong to `P4B`
