"""Localization of the forbidden source-repo / sibling-repo token list.

This module exists so that the rest of the runtime never names the forbidden
tokens directly. The L_STANDALONE / no-source-repo enforcement reads from this
list. Tests scan the runtime tree for these tokens with this single file
exempted, which keeps the proof tight.
"""

from __future__ import annotations

# WARNING: do not duplicate these strings anywhere else in src/m365_runtime/.
FORBIDDEN_TOKENS: tuple[str, ...] = (
    "M365_REPO_ROOT",
    "SMARTHAUS_M365_REPO_ROOT",
    "UCP_ROOT",
    "REPOS_ROOT",
    "UCP_REPOS_ROOT",
    "../M365",
    "from ops_adapter",
)
