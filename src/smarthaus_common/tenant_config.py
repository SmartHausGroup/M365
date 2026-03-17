"""Tenant configuration loader for the Universal Control Plane (UCP).

Loads per-customer configuration from YAML files in the tenants/ directory.
The active tenant is selected via the UCP_TENANT environment variable.

Credential resolution order (per field):
  1. Tenant YAML value (if non-empty)
  2. Environment variable fallback

This ensures tenant configs can reference env vars for secrets while keeping
the YAML file safe for version control when secrets are omitted.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class AzureConfig:
    tenant_id: str = ""
    client_id: str = ""
    client_secret: str = ""
    client_certificate_path: str = ""


@dataclass
class DelegatedAuthConfig:
    scopes: list[str] = field(default_factory=lambda: [
        "User.Read",
        "Mail.ReadWrite",
        "Mail.Send",
        "Calendars.ReadWrite",
        "Files.ReadWrite.All",
        "Sites.ReadWrite.All",
        "Team.ReadBasic.All",
        "Channel.ReadBasic.All",
        "Group.Read.All",
        "ChannelMessage.Send",
        "Chat.ReadWrite",
    ])
    token_cache_path: str = ""
    auto_prompt: bool = True


@dataclass
class AppOnlyAuthConfig:
    scope: str = "https://graph.microsoft.com/.default"


@dataclass
class AuthConfig:
    mode: str = "delegated"  # "app_only" | "delegated" | "hybrid"
    delegated: DelegatedAuthConfig = field(default_factory=DelegatedAuthConfig)
    app_only: AppOnlyAuthConfig = field(default_factory=AppOnlyAuthConfig)


@dataclass
class GraphSettings:
    base_url: str = "https://graph.microsoft.com/v1.0"
    timeout_seconds: int = 30
    max_retries: int = 5
    backoff_multiplier: float = 1.0
    backoff_max_seconds: float = 20.0


@dataclass
class GovernanceOverrides:
    confirmation_ttl_seconds: int = 900
    require_confirmation_for: list[str] = field(default_factory=list)
    financial_threshold_auto: float = 5000.0
    financial_threshold_manager: float = 50000.0


@dataclass
class DataResidency:
    enabled: bool = False
    default_region: str = ""
    rules: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class OrgMappings:
    sharepoint_hostname: str = ""
    primary_site_id: str = ""
    default_user_id: str = ""


@dataclass
class TenantIdentity:
    id: str = ""
    display_name: str = ""
    domain: str = ""


@dataclass
class PermissionTiersConfig:
    """Per-tenant permission tier assignments."""

    default_tier: str = "standard_user"
    users: dict[str, str] = field(default_factory=dict)

    def get_user_tier(self, user_email: str) -> str:
        """Return the tier for a user, falling back to default_tier."""
        if not user_email:
            return self.default_tier
        # Case-insensitive lookup
        lower_email = user_email.lower()
        for email, tier in self.users.items():
            if email.lower() == lower_email:
                return tier
        return self.default_tier


@dataclass
class TenantConfig:
    """Complete tenant configuration."""

    tenant: TenantIdentity = field(default_factory=TenantIdentity)
    azure: AzureConfig = field(default_factory=AzureConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    graph: GraphSettings = field(default_factory=GraphSettings)
    governance: GovernanceOverrides = field(default_factory=GovernanceOverrides)
    data_residency: DataResidency = field(default_factory=DataResidency)
    org: OrgMappings = field(default_factory=OrgMappings)
    permission_tiers: PermissionTiersConfig = field(default_factory=PermissionTiersConfig)

    @property
    def is_delegated(self) -> bool:
        return self.auth.mode in ("delegated", "hybrid")

    @property
    def is_app_only(self) -> bool:
        return self.auth.mode == "app_only"

    @property
    def is_hybrid(self) -> bool:
        return self.auth.mode == "hybrid"


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

_ENV_FALLBACKS = {
    "azure.tenant_id": [
        "AZURE_TENANT_ID", "GRAPH_TENANT_ID", "MICROSOFT_TENANT_ID",
    ],
    "azure.client_id": [
        "AZURE_CLIENT_ID", "AZURE_APP_CLIENT_ID_TAI",
        "GRAPH_CLIENT_ID", "MICROSOFT_CLIENT_ID",
    ],
    "azure.client_secret": [
        "AZURE_CLIENT_SECRET", "AZURE_APP_CLIENT_SECRET_TAI",
        "GRAPH_CLIENT_SECRET", "MICROSOFT_CLIENT_SECRET",
    ],
    "azure.client_certificate_path": [
        "AZURE_CLIENT_CERTIFICATE_PATH",
    ],
}


def _resolve_env_fallback(yaml_value: str, env_keys: list[str]) -> str:
    """Return yaml_value if non-empty, else try each env var in order."""
    if yaml_value:
        return yaml_value
    for key in env_keys:
        val = os.getenv(key, "")
        if val:
            return val
    return ""


def _parse_section(raw: dict[str, Any] | None, cls: type, defaults: Any | None = None):
    """Instantiate a dataclass from a dict, ignoring unknown keys."""
    if raw is None:
        return defaults or cls()
    # Filter to only keys the dataclass accepts
    import dataclasses
    valid_keys = {f.name for f in dataclasses.fields(cls)}
    filtered = {}
    for k, v in raw.items():
        if k in valid_keys:
            filtered[k] = v
    return cls(**filtered)


def load_tenant_config(
    tenant_slug: str | None = None,
    tenants_dir: str | None = None,
) -> TenantConfig:
    """Load a tenant configuration from YAML.

    Args:
        tenant_slug: Tenant identifier (e.g., "smarthaus"). If None, reads
                     from UCP_TENANT env var.
        tenants_dir: Directory containing tenant YAML files. If None, searches
                     standard locations.

    Returns:
        Fully resolved TenantConfig with env var fallbacks applied.
    """
    slug = tenant_slug or os.getenv("UCP_TENANT", "")

    if not slug:
        # No tenant configured — return defaults with env var fallbacks
        cfg = TenantConfig()
        cfg.azure.tenant_id = _resolve_env_fallback("", _ENV_FALLBACKS["azure.tenant_id"])
        cfg.azure.client_id = _resolve_env_fallback("", _ENV_FALLBACKS["azure.client_id"])
        cfg.azure.client_secret = _resolve_env_fallback("", _ENV_FALLBACKS["azure.client_secret"])
        cfg.azure.client_certificate_path = _resolve_env_fallback("", _ENV_FALLBACKS["azure.client_certificate_path"])
        return cfg

    # Search for the tenant file
    search_dirs: list[Path] = []

    if tenants_dir:
        search_dirs.append(Path(tenants_dir))

    # Standard locations relative to known paths
    mcp_root = os.getenv("UCP_ROOT", "")
    repos_root = os.getenv("REPOS_ROOT", os.getenv("UCP_REPOS_ROOT", ""))

    if mcp_root:
        search_dirs.append(Path(mcp_root) / "tenants")
    if repos_root:
        search_dirs.append(Path(repos_root) / "SMARTHAUS_MCPSERVER_core" / "tenants")

    # Relative from this file: src/smarthaus_common/ -> src/ -> M365/ -> ../UCP/tenants
    this_dir = Path(__file__).parent
    search_dirs.append(this_dir / ".." / ".." / ".." / "UCP" / "tenants")

    # Relative from this file: src/smarthaus_common/ -> src/ -> M365/ -> ../SMARTHAUS_MCPSERVER_core/tenants
    search_dirs.append(this_dir / ".." / ".." / ".." / "SMARTHAUS_MCPSERVER_core" / "tenants")

    yaml_path: Path | None = None
    for d in search_dirs:
        candidate = d / f"{slug}.yaml"
        resolved = candidate.resolve()
        if resolved.is_file():
            yaml_path = resolved
            break

    if yaml_path is None:
        raise FileNotFoundError(
            f"Tenant config '{slug}.yaml' not found. "
            f"Searched: {[str(d.resolve()) for d in search_dirs]}"
        )

    # Parse YAML
    with open(yaml_path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    # Build config
    cfg = TenantConfig()

    # Tenant identity
    cfg.tenant = _parse_section(raw.get("tenant"), TenantIdentity)

    # Azure — with env fallbacks for secrets
    azure_raw = raw.get("azure") or {}
    cfg.azure = AzureConfig(
        tenant_id=_resolve_env_fallback(azure_raw.get("tenant_id", ""), _ENV_FALLBACKS["azure.tenant_id"]),
        client_id=_resolve_env_fallback(azure_raw.get("client_id", ""), _ENV_FALLBACKS["azure.client_id"]),
        client_secret=_resolve_env_fallback(azure_raw.get("client_secret", ""), _ENV_FALLBACKS["azure.client_secret"]),
        client_certificate_path=_resolve_env_fallback(
            azure_raw.get("client_certificate_path", ""), _ENV_FALLBACKS["azure.client_certificate_path"]
        ),
    )

    # Auth
    auth_raw = raw.get("auth") or {}
    delegated_raw = auth_raw.get("delegated") or {}
    app_only_raw = auth_raw.get("app_only") or {}
    cfg.auth = AuthConfig(
        mode=auth_raw.get("mode", "delegated"),
        delegated=_parse_section(delegated_raw, DelegatedAuthConfig),
        app_only=_parse_section(app_only_raw, AppOnlyAuthConfig),
    )

    # Token cache path default
    if not cfg.auth.delegated.token_cache_path:
        cache_dir = Path.home() / ".ucp" / "tokens"
        cfg.auth.delegated.token_cache_path = str(cache_dir / f"{cfg.azure.tenant_id}.cache")

    # Graph settings
    cfg.graph = _parse_section(raw.get("graph"), GraphSettings)

    # Governance
    cfg.governance = _parse_section(raw.get("governance"), GovernanceOverrides)

    # Data residency
    cfg.data_residency = _parse_section(raw.get("data_residency"), DataResidency)

    # Org mappings
    cfg.org = _parse_section(raw.get("org"), OrgMappings)

    # Permission tiers
    pt_raw = raw.get("permission_tiers") or {}
    cfg.permission_tiers = PermissionTiersConfig(
        default_tier=pt_raw.get("default_tier", "standard_user"),
        users=pt_raw.get("users") or {},
    )

    return cfg


# ---------------------------------------------------------------------------
# Module-level cache
# ---------------------------------------------------------------------------

_cached_config: TenantConfig | None = None
_cached_slug: str | None = None


def get_tenant_config(tenant_slug: str | None = None) -> TenantConfig:
    """Get the tenant config, with caching.

    Call with no args to use the UCP_TENANT env var.
    Call with a slug to load a specific tenant (resets cache if different).
    """
    global _cached_config, _cached_slug

    slug = tenant_slug or os.getenv("UCP_TENANT", "")

    if _cached_config is not None and _cached_slug == slug:
        return _cached_config

    _cached_config = load_tenant_config(slug)
    _cached_slug = slug
    return _cached_config


def reload_tenant_config() -> TenantConfig:
    """Force reload the current tenant config from disk."""
    global _cached_config, _cached_slug
    _cached_config = None
    _cached_slug = None
    return get_tenant_config()
