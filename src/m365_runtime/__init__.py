"""Standalone Microsoft Graph runtime for the SMARTHAUS M365 Integration Pack.

Plan reference: plan:m365-standalone-graph-runtime-integration-pack:R5
Notebook evidence: notebooks/m365/INV-M365-DN-standalone-graph-runtime-pack-p3-prototypes-v1.ipynb
Scorecard: artifacts/scorecards/scorecard_standalone_graph_runtime_pack_p3.json

This package is the runtime service that ships INSIDE the marketplace artifact.
It must not import from `ops_adapter`, `smarthaus_graph`, or any sibling-repo
path. It must read only from its own installed root.
"""

from __future__ import annotations

__all__ = [
    "FAILURE_LATTICE",
    "ALLOWED_AUTH_MODES",
    "RUNTIME_VERSION",
]

RUNTIME_VERSION = "1.2.0"

FAILURE_LATTICE = (
    "success",
    "not_configured",
    "auth_required",
    "consent_required",
    "permission_missing",
    "throttled",
    "graph_unreachable",
    "policy_denied",
    "mutation_fence",
    "internal_error",
)

ALLOWED_AUTH_MODES = frozenset(
    {"auth_code_pkce", "device_code", "app_only_secret", "app_only_certificate"}
)
