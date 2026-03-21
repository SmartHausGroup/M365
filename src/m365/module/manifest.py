"""Manifest metadata for the embeddable M365 connector module."""

from __future__ import annotations

from typing import Any


def m365_connector_module_manifest() -> dict[str, Any]:
    """Return M365 connector module manifest for TAI runtime hosts."""
    return {
        "module_id": "m365-connector",
        "version": "1.0.0",
        "entrypoint": "m365.module.entrypoint:M365ConnectorModule",
        "capabilities": ["m365.instruction.execute"],
        "entitlements": ["m365_actions"],
        "compatibility": {"min_tai_version": "0.1.0"},
        "permissions": ["graph:m365", "audit:write", "mutations:gated"],
        "metadata": {
            "request_contract": ["action", "params"],
            "response_contract": ["ok", "result", "error", "trace_id"],
            "requires_host_auth": True,
            "external_mode_supported": True,
        },
    }
