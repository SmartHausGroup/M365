"""Action registry + permission matrix for the standalone Graph runtime.

Read-only Graph actions only. Mutation/write actions are explicitly fenced
(`mutation_fence`) until a separate mutation-governance plan approves them.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .. import ALLOWED_AUTH_MODES


class ActionRegistryError(KeyError):
    pass


@dataclass(frozen=True)
class ActionSpec:
    action_id: str
    workload: str
    endpoint: str
    auth_modes: frozenset[str]
    scopes: frozenset[str]
    risk: str
    rw: str

    def __post_init__(self) -> None:
        for mode in self.auth_modes:
            if mode not in ALLOWED_AUTH_MODES:
                raise ActionRegistryError(f"invalid_auth_mode:{mode}")


READ_ONLY_REGISTRY: dict[str, ActionSpec] = {
    spec.action_id: spec
    for spec in (
        ActionSpec("graph.org_profile",     "directory",  "/organization",                    frozenset({"app_only_secret","app_only_certificate"}),                                          frozenset({"Organization.Read.All"}),  "low", "read"),
        ActionSpec("graph.me",              "me",         "/me",                              frozenset({"auth_code_pkce","device_code"}),                                                    frozenset({"User.Read"}),              "low", "read"),
        ActionSpec("graph.users.list",      "users",      "/users",                           frozenset({"auth_code_pkce","device_code","app_only_secret","app_only_certificate"}),         frozenset({"User.Read.All"}),          "low", "read"),
        ActionSpec("graph.groups.list",     "groups",     "/groups",                          frozenset({"auth_code_pkce","device_code","app_only_secret","app_only_certificate"}),         frozenset({"Group.Read.All"}),         "low", "read"),
        ActionSpec("graph.sites.root",      "sharepoint", "/sites/root",                      frozenset({"auth_code_pkce","app_only_secret","app_only_certificate"}),                         frozenset({"Sites.Read.All"}),         "low", "read"),
        ActionSpec("graph.sites.search",    "sharepoint", "/sites?search=",                   frozenset({"auth_code_pkce","app_only_secret","app_only_certificate"}),                         frozenset({"Sites.Read.All"}),         "low", "read"),
        ActionSpec("graph.teams.list",      "teams",      "/teams",                           frozenset({"auth_code_pkce","app_only_secret","app_only_certificate"}),                         frozenset({"Team.ReadBasic.All"}),     "low", "read"),
        ActionSpec("graph.drives.list",     "sharepoint", "/drives",                          frozenset({"auth_code_pkce","app_only_secret","app_only_certificate"}),                         frozenset({"Files.Read.All"}),         "low", "read"),
        ActionSpec("graph.mail.health",     "exchange",   "/me/mailFolders",                  frozenset({"auth_code_pkce","device_code"}),                                                    frozenset({"Mail.Read"}),              "low", "read"),
        ActionSpec("graph.calendar.health", "exchange",   "/me/calendars",                    frozenset({"auth_code_pkce","device_code"}),                                                    frozenset({"Calendars.Read"}),         "low", "read"),
        ActionSpec("graph.servicehealth",   "admin",      "/admin/serviceHealth/issues",      frozenset({"app_only_secret","app_only_certificate"}),                                          frozenset({"ServiceHealth.Read.All"}), "low", "read"),
    )
}


def get_action(action_id: str) -> ActionSpec:
    spec = READ_ONLY_REGISTRY.get(action_id)
    if spec is None:
        raise ActionRegistryError(action_id)
    return spec


def admit(action_id: str, granted_scopes: frozenset[str], current_auth_mode: str) -> tuple[str, str]:
    try:
        spec = get_action(action_id)
    except ActionRegistryError:
        return ("denied", "unknown_action")
    if current_auth_mode not in spec.auth_modes:
        return ("denied", "auth_mode_mismatch")
    if not spec.scopes.issubset(granted_scopes):
        return ("denied", "permission_missing")
    if spec.rw != "read":
        return ("denied", "mutation_fence")
    return ("admit", "ok")
