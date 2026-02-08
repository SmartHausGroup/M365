"""
INV-M365-B-001, B-002: Persona isolation verification.

Extracted from notebooks/m365/INV-M365-B-persona-isolation.ipynb
Cells: Lemma Execution (lemma_B001, lemma_B002), Invariant Verification (verify_B001, verify_B002).

Invariant: INV-M365-B-001, INV-M365-B-002
Lemma: LEM-M365-B-001-01, LEM-M365-B-002-01
"""

from __future__ import annotations

from typing import Any

from m365.instruction.constants import A_Admin, A_mut, A_User


def verify_B001(instruction: Any) -> None:
    """
    INV-M365-B-001: For persona=User, action in A_User only (not A_Admin or A_mut).

    Extracted from notebooks/m365/INV-M365-B-persona-isolation.ipynb
    Cell: Invariant Verification.
    Fail closed: raises AssertionError on violation.
    """
    p, a = instruction[0], instruction[2]
    if p == "User":
        assert a in A_User, "B-001 fail: User must use A_User"
        assert a not in A_Admin and a not in A_mut


def verify_B002(instruction: Any) -> None:
    """
    INV-M365-B-002: For persona=User, action not in A_mut.

    Extracted from notebooks/m365/INV-M365-B-persona-isolation.ipynb
    Cell: Invariant Verification.
    Fail closed: raises AssertionError on violation.
    """
    p, a = instruction[0], instruction[2]
    if p == "User":
        assert a not in A_mut, "B-002 fail: User cannot mutate"
