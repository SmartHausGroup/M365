"""
Instruction 4-tuple structure and invariant verification (INV-M365-A-001, A-002, A-003).

Extracted from notebooks/m365/INV-M365-A-instruction-structure.ipynb
Cells: Setup (instruction_4tuple), Lemma Execution (lemma_A*_holds), Invariant Verification (verify_A*).

Invariant: INV-M365-A-001, INV-M365-A-002, INV-M365-A-003
Lemma: LEM-M365-A-001-01, LEM-M365-A-002-01, LEM-M365-A-003-01
"""

from __future__ import annotations

from typing import Any

from m365.instruction.constants import A_Admin, A_User, P


def instruction_4tuple(p: str, i: Any, a: str, params: Any) -> tuple[Any, Any, Any, Any]:
    """
    Build instruction as 4-tuple (persona, identity, action, parameters).

    Extracted from notebooks/m365/INV-M365-A-instruction-structure.ipynb
    Cell: Setup.
    Invariant: INV-M365-A-001
    """
    return (p, i, a, params)


def lemma_A001_holds(instruction: Any) -> bool:
    """
    Lemma A-001: instruction has exactly four components; sole source per tuple.

    Extracted from notebooks/m365/INV-M365-A-instruction-structure.ipynb
    Cell: Lemma Execution (LEM-M365-A-001-01).
    Invariant: INV-M365-A-001
    """
    if not isinstance(instruction, tuple | list) or len(instruction) != 4:
        return False
    return True


def lemma_A002_holds(instruction: Any) -> bool:
    """
    Lemma A-002: persona in P = {Admin, User}.

    Extracted from notebooks/m365/INV-M365-A-instruction-structure.ipynb
    Cell: Lemma Execution (LEM-M365-A-002-01).
    Invariant: INV-M365-A-002
    """
    p = instruction[0]
    return p in P


def lemma_A003_holds(instruction: Any) -> bool:
    """
    Lemma A-003: (p=Admin and a in A_Admin) or (p=User and a in A_User).

    Extracted from notebooks/m365/INV-M365-A-instruction-structure.ipynb
    Cell: Lemma Execution (LEM-M365-A-003-01).
    Invariant: INV-M365-A-003
    """
    p, a = instruction[0], instruction[2]
    return (p == "Admin" and a in A_Admin) or (p == "User" and a in A_User)


def verify_A001(instruction: Any) -> None:
    """
    INV-M365-A-001: exactly four components; each present; sole source.

    Extracted from notebooks/m365/INV-M365-A-instruction-structure.ipynb
    Cell: Invariant Verification.
    Fail closed: raises AssertionError on violation.
    """
    assert isinstance(instruction, tuple | list), "instruction must be tuple/list"
    assert len(instruction) == 4, "exactly four components"
    assert all(c is not None for c in instruction), "no component missing"


def verify_A002(instruction: Any) -> None:
    """
    INV-M365-A-002: instruction.persona in {Admin, User}.

    Extracted from notebooks/m365/INV-M365-A-instruction-structure.ipynb
    Cell: Invariant Verification.
    Fail closed: raises AssertionError on violation.
    """
    assert instruction[0] in P, "persona in {Admin, User}"


def verify_A003(instruction: Any) -> None:
    """
    INV-M365-A-003: syntactically valid; A_Admin and A_User disjoint.

    Extracted from notebooks/m365/INV-M365-A-instruction-structure.ipynb
    Cell: Invariant Verification.
    Fail closed: raises AssertionError on violation.
    """
    p, a = instruction[0], instruction[2]
    assert (p == "Admin" and a in A_Admin) or (p == "User" and a in A_User), "syntactically valid"
    assert A_Admin & A_User == set(), "disjoint"
