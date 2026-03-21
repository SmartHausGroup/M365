"""Embeddable M365 connector module package."""

from m365.module.entrypoint import M365ConnectorModule
from m365.module.manifest import m365_connector_module_manifest

__all__ = ["M365ConnectorModule", "m365_connector_module_manifest"]
