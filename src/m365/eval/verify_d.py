"""
INV-M365-D-001, D-002: Read vs mutation semantics verification.

Extracted from notebooks/m365/INV-M365-D-read-mutation.ipynb
Cell: Invariant Verification — verify_D001, verify_D002.

Invariant: INV-M365-D-001, INV-M365-D-002
Lemma: LEM-M365-D-001-01, LEM-M365-D-002-01
"""

from __future__ import annotations

from typing import Any, Callable

from m365.instruction.constants import A_mut, A_read


def verify_D001(
    instruction: Any,
    tenant_state: Any,
    eval_fn: Callable[[Any, Any], tuple[Any, Any, Any] | None],
) -> None:
    """
    INV-M365-D-001: For action in A_read and Eval defined, new_state=tenant_state, |audit|=0.

    Extracted from notebooks/m365/INV-M365-D-read-mutation.ipynb
    Cell: Invariant Verification.
    Fail closed: raises AssertionError on violation.
    """
    a = instruction[2]
    if a not in A_read:
        return
    out = eval_fn(instruction, tenant_state)
    if out is None:
        return
    r, new_state, audit = out
    assert new_state == tenant_state, "D-001: read preserves state"
    assert len(audit) == 0, "D-001: read produces no audit"


def verify_D002(instruction: Any) -> None:
    """
    INV-M365-D-002: For action in A_mut, persona = Admin.

    Extracted from notebooks/m365/INV-M365-D-read-mutation.ipynb
    Cell: Invariant Verification.
    Fail closed: raises AssertionError on violation.
    """
    a = instruction[2]
    if a in A_mut:
        assert instruction[0] == "Admin", "D-002: mutating requires Admin"
