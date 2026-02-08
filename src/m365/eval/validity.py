"""
Syntactic validity: instruction is 4-tuple and (p,a) compatible with A_Admin, A_User.

Extracted from notebooks/m365/INV-M365-B-persona-isolation.ipynb
Cell: Setup — is_valid(instruction).

Also same logic in INV-M365-C-001-determinism.ipynb, INV-M365-D-read-mutation.ipynb,
INV-M365-E-audit-semantics.ipynb, INV-M365-F-failure-closed.ipynb.

Invariant: INV-M365-A-003 (syntactic validity)
Lemma: LEM-M365-A-003-01
"""

from __future__ import annotations

from typing import Any

from m365.instruction.constants import A_Admin, A_User


def is_valid(instruction: Any) -> bool:
    """
    True iff instruction is 4-tuple and (p=Admin and a in A_Admin) or (p=User and a in A_User).

    Extracted from notebooks/m365/INV-M365-B-persona-isolation.ipynb
    Cell: Setup.
    Invariant: INV-M365-A-003
    Lemma: LEM-M365-A-003-01
    """
    if not isinstance(instruction, (tuple, list)) or len(instruction) != 4:
        return False
    p, a = instruction[0], instruction[2]
    return (p == "Admin" and a in A_Admin) or (p == "User" and a in A_User)
