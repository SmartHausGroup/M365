"""
M365 Instruction Contract — evaluation partial function and invariant verification.

Extracted from notebooks/m365/INV-M365-B-persona-isolation.ipynb through
INV-M365-G-mediation.ipynb.

Invariants: INV-M365-B-001, B-002, C-001, D-001, D-002, E-001, E-002, E-003, F-001, G-001, G-002
"""

from m365.eval.partial import eval_partial
from m365.eval.validity import is_valid
from m365.eval.verify_b import verify_B001, verify_B002
from m365.eval.verify_c import verify_C001
from m365.eval.verify_d import verify_D001, verify_D002
from m365.eval.verify_e import verify_E001, verify_E002, verify_E003
from m365.eval.verify_f import verify_F001
from m365.eval.verify_g import verify_G001, verify_G002

__all__ = [
    "eval_partial",
    "is_valid",
    "verify_B001",
    "verify_B002",
    "verify_C001",
    "verify_D001",
    "verify_D002",
    "verify_E001",
    "verify_E002",
    "verify_E003",
    "verify_F001",
    "verify_G001",
    "verify_G002",
]
