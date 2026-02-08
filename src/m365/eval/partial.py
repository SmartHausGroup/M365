"""
Eval as partial function: (instruction, tenant_state) -> (r, tau', audit) or None.

Extracted from notebooks/m365/INV-M365-C-001-determinism.ipynb
Cell: Setup — eval_partial.

Invariant: INV-M365-C-001 (Determinism keystone)
Lemma: LEM-M365-C-001-01
"""

from __future__ import annotations

from typing import Any

from m365.eval.validity import is_valid

# Result tag (Phase 1 Section 1: R)
SUCCESS = "Success"


def eval_partial(
    instruction: Any, tenant_state: Any
) -> tuple[str, Any, list[Any]] | None:
    """
    Partial function: same (instruction, tenant_state) -> same result or both undefined.

    Extracted from notebooks/m365/INV-M365-C-001-determinism.ipynb
    Cell: Setup.
    Invariant: INV-M365-C-001
    Lemma: LEM-M365-C-001-01
    """
    if not is_valid(instruction):
        return None
    p, a = instruction[0], instruction[2]
    if a in {"admin_read", "user_read"}:
        return (SUCCESS, tenant_state, [])
    if a == "admin_mutate" and p == "Admin":
        return (SUCCESS, tenant_state + 1, [{}])
    return None
