# Master Calculus — All Actions (Full O)

**Purpose:** The master calculus applies to **every** capability in the universe. This document defines \(\mathcal{O}\), \(\mathcal{O}_m\), and \(\mathcal{S}_{\texttt{action}}\) for all actions.

**Sources:** `registry/capability_registry.yaml`, `docs/contracts/M365_CAPABILITIES_UNIVERSE.md`, `caio-m365/ACTION_SPECIFICATION.md`, `caio-m365/MATHEMATICS.md`.

---

## 1. The set \(\mathcal{O}\)

\[
\mathcal{O} = \{\,\texttt{action name}\,\mid \texttt{entry in } \texttt{registry/capability\_registry.yaml}\,\}.
\]

**Canonical enumeration:** The registry lists every action with `action`, `resource`, `domain`, `required_permissions`, `mutating`, `status` (implemented | planned). The human-readable list is `M365_CAPABILITIES_UNIVERSE.md`. **Count:** 260 actions (9 implemented, 251 planned).

**No action outside \(\mathcal{O}\) is executable.** The pipeline \(\mathcal{P}\) (AuthGate ∘ IdempotencyLookup ∘ Execute ∘ Audit) and the master equation apply to every \(a \in \mathcal{O}\).

---

## 2. Mutating subset \(\mathcal{O}_m\)

\[
\mathcal{O}_m = \{\,a \in \mathcal{O} \mid \texttt{mutating}(a) = \texttt{true}\,\}.
\]

**Definition:** For each action in the registry, the field `mutating` is set from the operation type (create, update, delete, add, remove, send, assign, etc.). Idempotency (Eq. 3) and audit (Eq. 5) apply to all executions; mutating actions may require mutations enabled in the environment (see MATHEMATICS.md).

---

## 3. Result shape \(\mathcal{S}_{\texttt{action}}\) for every action

For each \(a \in \mathcal{O}\):

- **If \(a\) is implemented:** \(\mathcal{S}_a\) is defined in `caio-m365/ACTION_SPECIFICATION.md` and in the registry field `result_shape_keys`. The verification script asserts that successful responses have result shape in \(\mathcal{S}_a\).
- **If \(a\) is planned:** \(\mathcal{S}_a\) is **TBD** until the action is specified. When we implement \(a\), we add its result shape to ACTION_SPECIFICATION and to the registry.

**Master equation (per action):** For every request \(R\) with \(\texttt{action}(R) = a \in \mathcal{O}\):

\[
S = \mathcal{P}(R), \quad \mathtt{ok}(S) \Rightarrow \mathtt{shape}(\mathtt{result}(S)) \in \mathcal{S}_a, \quad \text{Eq. 1--5 hold as in MATHEMATICS.md}.
\]

So the **master calculus is defined for all 260 actions**: each has a place in \(\mathcal{O}\), a mutating flag, and a result-shape definition (either specified or TBD). Implementing a planned action means: (1) implement handler and (2) define \(\mathcal{S}_a\) in ACTION_SPECIFICATION and registry, then set status to implemented.

---

## 4. Summary

| Item | Value |
|------|--------|
| **\(\mathcal{O}\)** | 260 actions (registry + universe list) |
| **\(\mathcal{O}_m\)** | Subset with mutating = true (from registry) |
| **Implemented \(\mathcal{A}\)** | 9 (list_users, get_user, reset_user_password, list_teams, list_sites, create_site, create_team, add_channel, provision_service) |
| **Planned** | 251 |
| **\(\mathcal{S}_a\)** | Defined for implemented; TBD for planned until specified |
| **Master equation** | Applies to every \(a \in \mathcal{O}\) |

The full universe is under the same calculus. Close the gap by implementing planned actions and defining their \(\mathcal{S}_a\).
