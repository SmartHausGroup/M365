"""
M365 Instruction Contract — instruction structure and constants.

Extracted from notebooks/m365/INV-M365-A-instruction-structure.ipynb
and notebooks referenced by eval notebooks (B, C, D, E, F, G).

Invariants: INV-M365-A-001, INV-M365-A-002, INV-M365-A-003
Lemmas: LEM-M365-A-001-01, LEM-M365-A-002-01, LEM-M365-A-003-01
"""

from m365.instruction.constants import A_Admin, A_User, P
from m365.instruction.structure import (
    instruction_4tuple,
    lemma_A001_holds,
    lemma_A002_holds,
    lemma_A003_holds,
    verify_A001,
    verify_A002,
    verify_A003,
)

__all__ = [
    "P",
    "A_Admin",
    "A_User",
    "instruction_4tuple",
    "lemma_A001_holds",
    "lemma_A002_holds",
    "lemma_A003_holds",
    "verify_A001",
    "verify_A002",
    "verify_A003",
]
