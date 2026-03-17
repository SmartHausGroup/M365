"""
INV-M365-C-001: Determinism verification (keystone).

Extracted from notebooks/m365/INV-M365-C-001-determinism.ipynb
Cell: Invariant Verification — verify_C001.

Invariant: INV-M365-C-001
Lemma: LEM-M365-C-001-01
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


def verify_C001(
    eval_fn: Callable[[Any, Any], tuple[Any, Any, Any] | None],
    instruction: Any,
    tenant_state: Any,
    n_calls: int = 5,
) -> None:
    """
    INV-M365-C-001: For any (instruction, tenant_state), n_calls evaluations produce
    identical (result, new_tenant_state, audit_events) when all succeed, or all undefined.

    Extracted from notebooks/m365/INV-M365-C-001-determinism.ipynb
    Cell: Invariant Verification.
    Fail closed: raises AssertionError on violation.
    """
    results = [eval_fn(instruction, tenant_state) for _ in range(n_calls)]
    if results[0] is None:
        assert all(r is None for r in results), "All undefined"
    else:
        assert all(r == results[0] for r in results), "All same triple"
