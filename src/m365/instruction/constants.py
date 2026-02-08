"""
Phase 1 Section 1–2 constants: P, A_Admin, A_User, A_read, A_mut.

Extracted from notebooks/m365/INV-M365-A-instruction-structure.ipynb
Cell: Setup — deterministic configuration.

Also from INV-M365-D-read-mutation.ipynb, INV-M365-E-audit-semantics.ipynb
for A_read, A_mut.

Invariant: INV-M365-A-002, INV-M365-A-003 (persona and action sets)
Lemma: LEM-M365-A-002-01, LEM-M365-A-003-01
"""

# Phase 1 Section 1: P = {Admin, User}. Exactly two personas.
P: frozenset[str] = frozenset({"Admin", "User"})

# Phase 1 Section 2: A_Admin, A_User disjoint.
A_Admin: frozenset[str] = frozenset({"admin_mutate", "admin_read"})
A_User: frozenset[str] = frozenset({"user_read"})

# Phase 1 Section 3–4: A_read, A_mut partition; A_mut ⊆ A_Admin.
A_read: frozenset[str] = frozenset({"admin_read", "user_read"})
A_mut: frozenset[str] = frozenset({"admin_mutate"})
