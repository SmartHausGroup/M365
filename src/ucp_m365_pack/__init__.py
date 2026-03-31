"""Standalone UCP-facing M365 pack surface owned by the M365 repo."""

from ucp_m365_pack.contracts import M365PackAdapter, create_pack_adapter

__all__ = [
    "M365PackAdapter",
    "create_pack_adapter",
]
