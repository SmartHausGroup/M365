"""
INV-M365-E-001, E-002, E-003: Audit semantics verification.

Extracted from notebooks/m365/INV-M365-E-audit-semantics.ipynb
Cell: Invariant Verification — verify_E001, verify_E002, verify_E003.

Invariant: INV-M365-E-001, INV-M365-E-002, INV-M365-E-003
Lemma: LEM-M365-E-001-01, LEM-M365-E-002-01, LEM-M365-E-003-01
"""

from __future__ import annotations

from typing import Any, Callable

from m365.instruction.constants import A_mut, A_read


def verify_E001(
    instruction: Any,
    tenant_state: Any,
    eval_fn: Callable[[Any, Any], tuple[Any, Any, Any] | None],
) -> None:
    """
    INV-M365-E-001: persona=Admin, action in A_mut, result success -> |audit_events| = 1.

    Extracted from notebooks/m365/INV-M365-E-audit-semantics.ipynb
    Cell: Invariant Verification.
    Fail closed: raises AssertionError on violation.
    """
    out = eval_fn(instruction, tenant_state)
    if out is None:
        return
    r, _, audit = out
    if (
        instruction[0] == "Admin"
        and instruction[2] in A_mut
        and r == "Success"
    ):
        assert len(audit) == 1, "E-001: exactly one audit"


def verify_E002(
    instruction: Any,
    tenant_state: Any,
    eval_fn: Callable[[Any, Any], tuple[Any, Any, Any] | None],
) -> None:
    """
    INV-M365-E-002: evaluation undefined or result failure -> |audit_events| = 0.

    Extracted from notebooks/m365/INV-M365-E-audit-semantics.ipynb
    Cell: Invariant Verification.
    Fail closed: raises AssertionError on violation.
    """
    out = eval_fn(instruction, tenant_state)
    if out is None:
        return
    r, _, audit = out
    if r != "Success":
        assert len(audit) == 0


def verify_E003(
    instruction: Any,
    tenant_state: Any,
    eval_fn: Callable[[Any, Any], tuple[Any, Any, Any] | None],
) -> None:
    """
    INV-M365-E-003: persona=User or action in A_read -> |audit_events| = 0.

    Extracted from notebooks/m365/INV-M365-E-audit-semantics.ipynb
    Cell: Invariant Verification.
    Fail closed: raises AssertionError on violation.
    """
    out = eval_fn(instruction, tenant_state)
    if out is None:
        return
    _, _, audit = out
    if instruction[0] == "User" or instruction[2] in A_read:
        assert len(audit) == 0, "E-003: User/read -> no audit"
