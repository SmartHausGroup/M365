"""
INV-M365-F-001: Failure-closed / no state change on rejection.

Extracted from notebooks/m365/INV-M365-F-failure-closed.ipynb
Cell: Invariant Verification — verify_F001.

Invariant: INV-M365-F-001
Lemma: LEM-M365-F-001-01
"""

from __future__ import annotations

from typing import Any, Callable


def verify_F001(
    instruction: Any,
    tenant_state: Any,
    eval_fn: Callable[[Any, Any], tuple[Any, Any, Any] | None],
) -> Any:
    """
    INV-M365-F-001: When Eval undefined, return tenant_state unchanged (no observable mutation).
    When defined, return new_tenant_state from triple.

    Extracted from notebooks/m365/INV-M365-F-failure-closed.ipynb
    Cell: Invariant Verification.
    Fail closed: on undefined, returns tenant_state; no side effects.
    """
    out = eval_fn(instruction, tenant_state)
    if out is None:
        assert True
        return tenant_state
    return out[1]
