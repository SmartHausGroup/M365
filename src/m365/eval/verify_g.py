"""
INV-M365-G-001, G-002: Instruction mediation / no hidden context verification.

Extracted from notebooks/m365/INV-M365-G-mediation.ipynb
Cell: Invariant Verification — verify_G001, verify_G002.

Invariant: INV-M365-G-001, INV-M365-G-002
Lemma: LEM-M365-G-001-01, LEM-M365-G-002-01
"""

from __future__ import annotations

from typing import Any, Callable

from m365.instruction.constants import A_Admin, A_User, P


def verify_G001(instruction: Any) -> None:
    """
    INV-M365-G-001: instruction has 4 components; persona in P; action in A_Admin or A_User.

    Extracted from notebooks/m365/INV-M365-G-mediation.ipynb
    Cell: Invariant Verification.
    Fail closed: raises AssertionError on violation.
    """
    assert len(instruction) == 4
    assert instruction[0] in P
    assert instruction[2] in A_Admin or instruction[2] in A_User


def verify_G002(
    eval_fn: Callable[[Any, Any], tuple[Any, Any, Any] | None],
    instruction: Any,
    tenant_state: Any,
) -> None:
    """
    INV-M365-G-002: Output depends only on (instruction, tenant_state); same input -> same output.

    Extracted from notebooks/m365/INV-M365-G-mediation.ipynb
    Cell: Invariant Verification.
    Fail closed: raises AssertionError on violation.
    """
    o1 = eval_fn(instruction, tenant_state)
    o2 = eval_fn(instruction, tenant_state)
    assert o1 == o2, "Output depends only on (instruction, tenant_state)"
