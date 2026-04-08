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

import copy
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

_LOGICAL_EXECUTOR_ALIASES: dict[str, tuple[str, ...]] = {
    "approvals": ("sharepoint",),
    "messaging": ("collaboration",),
    "workmanagement": ("collaboration",),
    "knowledge": ("sharepoint",),
    "publishing": ("sharepoint",),
    "composite": ("sharepoint",),
    "reports": ("directory",),
    "access_reviews": ("directory",),
    "compliance": ("directory",),
    "security": ("directory",),
    "identity_security": ("directory",),
    "devices": ("directory",),
}

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
    scopes: list[str] = field(
        default_factory=lambda: [
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
        ]
    )
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
    approvals_site_url: str = ""
    approvals_site_id: str = ""
    approvals_list_id: str = ""
    approvals_list_name: str = "Approvals"


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
    groups: dict[str, str] = field(default_factory=dict)

    def resolve_tier_assignment(
        self, user_email: str, actor_groups: list[str] | None = None
    ) -> dict[str, Any]:
        """Resolve the effective tier for an actor from explicit user or group mappings."""
        if user_email:
            lower_email = user_email.lower()
            for email, tier in self.users.items():
                if email.lower() == lower_email:
                    return {
                        "tier_name": tier,
                        "assignment_source": "user",
                        "assignment_match": email,
                    }

        normalized_groups = {str(group).lower() for group in (actor_groups or []) if group}
        for group_id, tier in self.groups.items():
            if group_id.lower() in normalized_groups:
                return {
                    "tier_name": tier,
                    "assignment_source": "group",
                    "assignment_match": group_id,
                }

        return {
            "tier_name": self.default_tier,
            "assignment_source": "default",
            "assignment_match": self.default_tier,
        }

    def get_user_tier(self, user_email: str, actor_groups: list[str] | None = None) -> str:
        """Return the tier for a user, falling back to default_tier."""
        return self.resolve_tier_assignment(user_email, actor_groups)["tier_name"]


@dataclass
class ExecutorConfig:
    """Bounded executor configuration for one runtime domain."""

    name: str = ""
    display_name: str = ""
    domain: str = ""
    capabilities: list[str] = field(default_factory=list)
    azure: AzureConfig = field(default_factory=AzureConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)


@dataclass
class ExecutorRegistryConfig:
    """Registry metadata for bounded executors and future routing."""

    default_executor: str = ""
    routes: dict[str, str] = field(default_factory=dict)


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
    executors: dict[str, ExecutorConfig] = field(default_factory=dict)
    executor_registry: ExecutorRegistryConfig = field(default_factory=ExecutorRegistryConfig)

    @property
    def is_delegated(self) -> bool:
        return self.auth.mode in ("delegated", "hybrid")

    @property
    def is_app_only(self) -> bool:
        return self.auth.mode == "app_only"

    @property
    def is_hybrid(self) -> bool:
        return self.auth.mode == "hybrid"

    @property
    def default_executor_name(self) -> str:
        return self.executor_registry.default_executor

    @property
    def default_executor(self) -> ExecutorConfig | None:
        return self.executors.get(self.default_executor_name)

    def resolve_executor_name(
        self,
        route_key: str,
        *,
        action_name: str | None = None,
        fallback_keys: list[str] | None = None,
    ) -> str:
        candidates: list[str] = []
        if action_name:
            candidates.append(action_name)
        if route_key:
            candidates.append(route_key)
        candidates.extend([str(key) for key in (fallback_keys or []) if str(key).strip()])

        registry_routes = {
            str(key).strip().lower(): str(value).strip()
            for key, value in (self.executor_registry.routes or {}).items()
            if str(key).strip() and str(value).strip()
        }
        executor_capabilities = {
            executor_name: {
                executor_name.lower(),
                str(executor.domain or "").strip().lower(),
                *{
                    str(capability).strip().lower()
                    for capability in (executor.capabilities or [])
                    if str(capability).strip()
                },
            }
            for executor_name, executor in (self.executors or {}).items()
        }

        for candidate in candidates:
            normalized_candidate = str(candidate).strip().lower()
            if not normalized_candidate:
                continue

            target = registry_routes.get(normalized_candidate)
            if target:
                if target not in self.executors:
                    raise ValueError(
                        f"executor_route_target_missing:{normalized_candidate}:{target}"
                    )
                return target
            if normalized_candidate in self.executors:
                return normalized_candidate
            for alias_target in _LOGICAL_EXECUTOR_ALIASES.get(normalized_candidate, ()):
                if alias_target in self.executors:
                    return alias_target
            for executor_name, capabilities in executor_capabilities.items():
                if normalized_candidate in capabilities:
                    return executor_name

        if len(self.executors) == 1:
            return self.default_executor_name

        raise ValueError(f"executor_route_unmapped:{route_key}")

    def project_executor(self, executor_name: str) -> TenantConfig:
        if executor_name not in self.executors:
            raise ValueError(f"executor_not_defined:{executor_name}")

        projected = copy.deepcopy(self)
        executor = projected.executors[executor_name]
        projected.azure = _clone_azure_config(executor.azure)
        projected.auth = _clone_auth_config(executor.auth)
        projected.executor_registry.default_executor = executor_name
        return projected

    def project_powerplatform_executor(self) -> TenantConfig:
        """Project Power Platform onto an explicit runtime identity.

        The logical `powerplatform` route must never silently drift onto the
        SharePoint executor. If no explicit Power Platform executor exists in
        the tenant contract, this falls back only to the dedicated or legacy
        bootstrap env contract.
        """

        explicit = self.executors.get("powerplatform")
        if explicit is not None:
            return self.project_executor("powerplatform")

        for executor_name, executor in (self.executors or {}).items():
            if str(executor.domain or "").strip().lower() == "powerplatform":
                return self.project_executor(executor_name)

        env_azure = _build_powerplatform_env_azure_config()
        if not env_azure.tenant_id or not env_azure.client_id:
            raise ValueError("powerplatform_executor_unconfigured")

        projected = copy.deepcopy(self)
        projected.azure = env_azure
        projected.executor_registry.default_executor = "powerplatform"
        projected.executors["powerplatform"] = ExecutorConfig(
            name="powerplatform",
            display_name="Power Platform Runtime Projection",
            domain="powerplatform",
            capabilities=["powerplatform", "powerapps", "powerautomate", "powerbi"],
            azure=_clone_azure_config(env_azure),
            auth=_clone_auth_config(projected.auth),
        )
        return projected


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

_ENV_FALLBACKS = {
    "azure.tenant_id": [
        "AZURE_TENANT_ID",
        "GRAPH_TENANT_ID",
        "MICROSOFT_TENANT_ID",
    ],
    "azure.client_id": [
        "AZURE_CLIENT_ID",
        "AZURE_APP_CLIENT_ID_TAI",
        "GRAPH_CLIENT_ID",
        "MICROSOFT_CLIENT_ID",
    ],
    "azure.client_secret": [
        "AZURE_CLIENT_SECRET",
        "AZURE_APP_CLIENT_SECRET_TAI",
        "GRAPH_CLIENT_SECRET",
        "MICROSOFT_CLIENT_SECRET",
    ],
    "azure.client_certificate_path": [
        "AZURE_CLIENT_CERTIFICATE_PATH",
    ],
}

_POWERPLATFORM_ENV_FALLBACKS = {
    "azure.tenant_id": [
        "SMARTHAUS_PP_TENANT_ID",
        "SMARTHAUS_POWERPLATFORM_TENANT_ID",
        "AZURE_TENANT_ID",
        "GRAPH_TENANT_ID",
        "MICROSOFT_TENANT_ID",
    ],
    "azure.client_id": [
        "SMARTHAUS_PP_CLIENT_ID",
        "SMARTHAUS_POWERPLATFORM_CLIENT_ID",
        "AZURE_APP_CLIENT_ID_TAI",
        "GRAPH_CLIENT_ID",
        "AZURE_CLIENT_ID",
        "MICROSOFT_CLIENT_ID",
    ],
    "azure.client_secret": [
        "SMARTHAUS_PP_CLIENT_SECRET",
        "SMARTHAUS_POWERPLATFORM_CLIENT_SECRET",
        "AZURE_APP_CLIENT_SECRET_TAI",
        "GRAPH_CLIENT_SECRET",
        "AZURE_CLIENT_SECRET",
        "MICROSOFT_CLIENT_SECRET",
    ],
    "azure.client_certificate_path": [
        "SMARTHAUS_PP_CLIENT_CERTIFICATE_PATH",
        "SMARTHAUS_POWERPLATFORM_CLIENT_CERTIFICATE_PATH",
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


def _parse_section(raw: dict[str, Any] | None, cls: type[Any], defaults: Any | None = None) -> Any:
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


def _parse_string_list(raw: Any, default: list[str] | None = None) -> list[str]:
    if not isinstance(raw, list):
        return list(default or [])
    return [str(item) for item in raw if str(item).strip()]


def _clone_azure_config(source: AzureConfig) -> AzureConfig:
    return AzureConfig(
        tenant_id=source.tenant_id,
        client_id=source.client_id,
        client_secret=source.client_secret,
        client_certificate_path=source.client_certificate_path,
    )


def _build_powerplatform_env_azure_config() -> AzureConfig:
    return AzureConfig(
        tenant_id=_resolve_env_fallback("", _POWERPLATFORM_ENV_FALLBACKS["azure.tenant_id"]),
        client_id=_resolve_env_fallback("", _POWERPLATFORM_ENV_FALLBACKS["azure.client_id"]),
        client_secret=_resolve_env_fallback(
            "", _POWERPLATFORM_ENV_FALLBACKS["azure.client_secret"]
        ),
        client_certificate_path=_resolve_env_fallback(
            "", _POWERPLATFORM_ENV_FALLBACKS["azure.client_certificate_path"]
        ),
    )


def _clone_auth_config(source: AuthConfig) -> AuthConfig:
    return AuthConfig(
        mode=source.mode,
        delegated=DelegatedAuthConfig(
            scopes=list(source.delegated.scopes),
            token_cache_path=source.delegated.token_cache_path,
            auto_prompt=source.delegated.auto_prompt,
        ),
        app_only=AppOnlyAuthConfig(scope=source.app_only.scope),
    )


def _build_azure_config(
    raw: dict[str, Any] | None, fallback: AzureConfig | None = None
) -> AzureConfig:
    base = fallback or AzureConfig()
    data = raw or {}
    return AzureConfig(
        tenant_id=_resolve_env_fallback(
            str(data.get("tenant_id", base.tenant_id) or ""),
            _ENV_FALLBACKS["azure.tenant_id"],
        ),
        client_id=_resolve_env_fallback(
            str(data.get("client_id", base.client_id) or ""),
            _ENV_FALLBACKS["azure.client_id"],
        ),
        client_secret=_resolve_env_fallback(
            str(data.get("client_secret", base.client_secret) or ""),
            _ENV_FALLBACKS["azure.client_secret"],
        ),
        client_certificate_path=_resolve_env_fallback(
            str(data.get("client_certificate_path", base.client_certificate_path) or ""),
            _ENV_FALLBACKS["azure.client_certificate_path"],
        ),
    )


def _build_auth_config(
    raw: dict[str, Any] | None, fallback: AuthConfig | None = None
) -> AuthConfig:
    base = fallback or AuthConfig()
    data = raw or {}
    delegated_raw = data.get("delegated") or {}
    app_only_raw = data.get("app_only") or {}
    delegated = DelegatedAuthConfig(
        scopes=_parse_string_list(delegated_raw.get("scopes"), base.delegated.scopes),
        token_cache_path=str(
            delegated_raw.get("token_cache_path", base.delegated.token_cache_path) or ""
        ),
        auto_prompt=bool(delegated_raw.get("auto_prompt", base.delegated.auto_prompt)),
    )
    app_only = AppOnlyAuthConfig(
        scope=str(app_only_raw.get("scope", base.app_only.scope) or base.app_only.scope)
    )
    return AuthConfig(
        mode=str(data.get("mode", base.mode) or base.mode),
        delegated=delegated,
        app_only=app_only,
    )


def _apply_auth_defaults(auth_cfg: AuthConfig, tenant_id: str) -> None:
    if not auth_cfg.delegated.token_cache_path:
        cache_dir = Path.home() / ".ucp" / "tokens"
        auth_cfg.delegated.token_cache_path = str(cache_dir / f"{tenant_id}.cache")


def _build_executor_configs(
    raw: Any,
    *,
    fallback_azure: AzureConfig,
    fallback_auth: AuthConfig,
) -> dict[str, ExecutorConfig]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError("executors must be a mapping of executor names to configuration")

    executors: dict[str, ExecutorConfig] = {}
    for name in sorted(raw):
        executor_raw = raw.get(name) or {}
        if not isinstance(executor_raw, dict):
            raise ValueError(f"Executor '{name}' must be a mapping")

        azure_cfg = _build_azure_config(executor_raw.get("azure"), fallback=fallback_azure)
        auth_cfg = _build_auth_config(executor_raw.get("auth"), fallback=fallback_auth)
        _apply_auth_defaults(auth_cfg, azure_cfg.tenant_id)

        executors[name] = ExecutorConfig(
            name=name,
            display_name=str(executor_raw.get("display_name", name) or name),
            domain=str(executor_raw.get("domain", name) or name),
            capabilities=_parse_string_list(executor_raw.get("capabilities")),
            azure=azure_cfg,
            auth=auth_cfg,
        )

    return executors


def _build_executor_registry(
    raw: Any,
    *,
    executors: dict[str, ExecutorConfig],
) -> ExecutorRegistryConfig:
    if not executors:
        return ExecutorRegistryConfig()

    if raw is None:
        registry_raw: dict[str, Any] = {}
    elif isinstance(raw, dict):
        registry_raw = raw
    else:
        raise ValueError("executor_registry must be a mapping")

    default_executor = str(registry_raw.get("default_executor", "") or "")
    routes_raw = registry_raw.get("routes")
    if routes_raw is None:
        routes_raw = registry_raw.get("routing") or {}
    if not isinstance(routes_raw, dict):
        raise ValueError("executor_registry.routes must be a mapping")

    if not default_executor:
        if len(executors) == 1:
            default_executor = next(iter(executors))
        else:
            raise ValueError("Multiple executors require executor_registry.default_executor")

    if default_executor not in executors:
        raise ValueError(f"executor_registry.default_executor '{default_executor}' is not defined")

    routes = {str(route): str(target) for route, target in routes_raw.items()}
    for route, target in routes.items():
        if target not in executors:
            raise ValueError(
                f"executor_registry route '{route}' targets unknown executor '{target}'"
            )

    return ExecutorRegistryConfig(default_executor=default_executor, routes=routes)


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
        cfg.azure.client_certificate_path = _resolve_env_fallback(
            "", _ENV_FALLBACKS["azure.client_certificate_path"]
        )
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

    # Root executor values remain the backward-compatible runtime contract.
    azure_raw = raw.get("azure") or {}
    auth_raw = raw.get("auth") or {}
    cfg.azure = _build_azure_config(azure_raw)
    cfg.auth = _build_auth_config(auth_raw)
    _apply_auth_defaults(cfg.auth, cfg.azure.tenant_id)

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
        groups=pt_raw.get("groups") or {},
    )

    # Executors and registry metadata. Legacy single-executor tenants get a
    # synthesized "default" executor so downstream runtime code can migrate
    # without splitting configuration authority.
    cfg.executors = _build_executor_configs(
        raw.get("executors"),
        fallback_azure=cfg.azure,
        fallback_auth=cfg.auth,
    )
    if cfg.executors:
        cfg.executor_registry = _build_executor_registry(
            raw.get("executor_registry"),
            executors=cfg.executors,
        )
    else:
        cfg.executors = {
            "default": ExecutorConfig(
                name="default",
                display_name="Default Executor",
                domain="default",
                capabilities=["legacy"],
                azure=_clone_azure_config(cfg.azure),
                auth=_clone_auth_config(cfg.auth),
            )
        }
        cfg.executor_registry = ExecutorRegistryConfig(default_executor="default")

    default_executor = cfg.default_executor
    if default_executor is None:
        raise ValueError("No deterministic default executor is available")

    cfg.azure = _clone_azure_config(default_executor.azure)
    cfg.auth = _clone_auth_config(default_executor.auth)

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
