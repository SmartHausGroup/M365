"""Standalone UCP-facing M365 pack surface owned by the M365 repo.

The pack adapter (``M365PackAdapter``) lives in :mod:`ucp_m365_pack.contracts`
and depends on the UCP MCP SDK (``smarthaus_mcp_sdk``). The pack client
(``execute_m365_action``) lives in :mod:`ucp_m365_pack.client` and does not
require the MCP SDK. To avoid forcing the SDK import on consumers that only
need the client, the adapter symbols are imported lazily via ``__getattr__``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

__all__ = [
    "M365PackAdapter",
    "create_pack_adapter",
]


def __getattr__(name: str) -> Any:
    if name in ("M365PackAdapter", "create_pack_adapter"):
        from ucp_m365_pack.contracts import M365PackAdapter, create_pack_adapter  # noqa: F401

        return {
            "M365PackAdapter": M365PackAdapter,
            "create_pack_adapter": create_pack_adapter,
        }[name]
    raise AttributeError(f"module 'ucp_m365_pack' has no attribute {name!r}")


if TYPE_CHECKING:  # pragma: no cover
    from ucp_m365_pack.contracts import M365PackAdapter, create_pack_adapter  # noqa: F401
