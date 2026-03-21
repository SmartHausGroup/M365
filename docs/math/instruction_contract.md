# Formal Mathematical Specification: M365 Instruction Contract

**Phase 1 — Math Only**

**System:** M365 Instruction API
**Repo:** https://github.com/SmartHausGroup/M365
**MA Phase:** Phase 1 (Intent & Mathematical Foundation)

---

## Section 1: Sets and Domains

- **Personas**
  \[
  \mathcal{P} = \{\mathsf{Admin},\mathsf{User}\}.
  \]
  Exactly two personas; no other values.

- **Identities**
  \[
  \mathcal{I} \quad \text{(set of identity values)}.
  \]
  No internal structure assumed here; elements are opaque identifiers (e.g., validated elsewhere).

- **Actions**
  \[
  \mathcal{A} \quad \text{(set of action identifiers)}.
  \]
  Partitioned by persona (see Section 2). No enumeration or implementation detail.

- **Parameters**
  \[
  \mathcal{P}\!\mathit{ar} \quad \text{(set of parameter structures)}.
  \]
  Arbitrary structure; no internal syntax specified.

- **Tenant state**
  \[
  \mathcal{T} \quad \text{(set of tenant states)}.
  \]
  Represents the whole external state the system reads and may update. No internal representation.

- **Results (value domain)**
  \[
  \mathcal{R} \quad \text{(set of result values)}.
  \]
  Success values and failure/signal values; structure left abstract.

- **Audit events**
  \[
  \mathcal{E} \quad \text{(set of audit event structures)}.
  \]
  One element corresponds to "one audit record" for our guarantees.

- **Instruction tuple**
  \[
  \mathcal{X} = \mathcal{P} \times \mathcal{I} \times \mathcal{A} \times \mathcal{P}\!\mathit{ar}.
  \]
  An instruction is \(x = (p, i, a, \mathit{params}) \in \mathcal{X}\).

---

## Section 2: Instruction Structure

- **Instruction**
  \[
  x = (p, i, a, \mathit{params}), \qquad p \in \mathcal{P},\; i \in \mathcal{I},\; a \in \mathcal{A},\; \mathit{params} \in \mathcal{P}\!\mathit{ar}.
  \]

- **Action–persona compatibility**
  Define:
  \[
  \mathcal{A}_{\mathsf{Admin}} \subseteq \mathcal{A}, \qquad \mathcal{A}_{\mathsf{User}} \subseteq \mathcal{A}.
  \]
  Constraint: \(\mathcal{A}_{\mathsf{Admin}} \cap \mathcal{A}_{\mathsf{User}} = \varnothing\).
  An action is either Admin-only or User-only (no overlap).

- **Valid instruction (syntactic)**
  \(x = (p, i, a, \mathit{params})\) is **syntactically valid** if:
  \[
  (p = \mathsf{Admin} \wedge a \in \mathcal{A}_{\mathsf{Admin}}) \;\vee\; (p = \mathsf{User} \wedge a \in \mathcal{A}_{\mathsf{User}}).
  \]
  Denote the set of syntactically valid instructions by \(\mathcal{X}_{\mathrm{valid}} \subseteq \mathcal{X}\).

- **Semantic validity**
  Whether \((x, \tau)\) is allowed for tenant state \(\tau \in \mathcal{T}\) (e.g., permissions, preconditions) is not specified here; we only assume a predicate \(\mathrm{Valid}(x, \tau)\) is defined elsewhere. **Assumption:** M365 receives only instructions that have been validated (e.g., by CAIO); we specify behavior when that assumption holds and when it does not.

---

## Section 3: Core Evaluation Function(s)

- **Single-step evaluation (conceptual)**
  The core map is a partial function:
  \[
  \mathrm{Eval}: \mathcal{X} \times \mathcal{T} \rightharpoonup \mathcal{R} \times \mathcal{T} \times \mathcal{E}^*
  \]
  where \(\mathcal{E}^*\) denotes finite sequences (lists) of audit events.
  For \((x, \tau)\):
  - If \(\mathrm{Eval}(x, \tau)\) is defined:
    \[
    \mathrm{Eval}(x, \tau) = (r, \tau', \mathit{audit}),
    \]
    with \(r \in \mathcal{R}\), \(\tau' \in \mathcal{T}\), \(\mathit{audit} \in \mathcal{E}^*\).
  - If \(\mathrm{Eval}(x, \tau)\) is undefined: the instruction is rejected (failure; see Section 6).

- **Determinism (to be enforced by design)**
  For the same \(x \in \mathcal{X}\) and \(\tau \in \mathcal{T}\), \(\mathrm{Eval}(x, \tau)\) is either undefined for both, or defined with the same \((r, \tau', \mathit{audit})\). So:
  \[
  \mathrm{Eval}(x, \tau) = (r_1, \tau_1', \mathit{audit}_1) \wedge \mathrm{Eval}(x, \tau) = (r_2, \tau_2', \mathit{audit}_2)
  \;\Rightarrow\; r_1 = r_2 \wedge \tau_1' = \tau_2' \wedge \mathit{audit}_1 = \mathit{audit}_2.
  \]

- **Read-only vs mutating**
  We partition \(\mathcal{A}\) into:
  - \(\mathcal{A}_{\mathrm{read}}\) — read-only actions (no state change),
  - \(\mathcal{A}_{\mathrm{mut}}\) — mutating actions (state may change),
  with \(\mathcal{A}_{\mathrm{read}} \cap \mathcal{A}_{\mathrm{mut}} = \varnothing\).
  For **read-only** \(a \in \mathcal{A}_{\mathrm{read}}\) we require (Section 4):
  \[
  \mathrm{Eval}(x, \tau) = (r, \tau', \mathit{audit}) \;\Rightarrow\; \tau' = \tau \wedge \mathit{audit} = ().
  \]
  For **mutating** \(a \in \mathcal{A}_{\mathrm{mut}}\), we constrain \(\mathit{audit}\) in Section 5.

---

## Section 4: Mutation vs Read Semantics

- **Read-only**
  Let \(x = (p, i, a, \mathit{params})\) with \(a \in \mathcal{A}_{\mathrm{read}}\). For any \(\tau \in \mathcal{T}\) where \(\mathrm{Eval}(x, \tau)\) is defined:
  \[
  \mathrm{Eval}(x, \tau) = (r, \tau', \mathit{audit}) \;\Rightarrow\; \tau' = \tau \;\wedge\; \mathit{audit} = ().
  \]
  So: no state change, no audit events.

- **Mutating**
  Let \(x = (p, i, a, \mathit{params})\) with \(a \in \mathcal{A}_{\mathrm{mut}}\). For any \(\tau \in \mathcal{T}\) where \(\mathrm{Eval}(x, \tau)\) is defined:
  \[
  \mathrm{Eval}(x, \tau) = (r, \tau', \mathit{audit}).
  \]
  We allow \(\tau' \neq \tau\) and \(\mathit{audit}\) non-empty; exact cardinality of \(\mathit{audit}\) is given in Section 5.

- **Persona and mutation**
  Only Admin may perform mutating actions:
  \[
  \mathcal{A}_{\mathrm{mut}} \subseteq \mathcal{A}_{\mathsf{Admin}}.
  \]
  So User persona has no access to \(\mathcal{A}_{\mathrm{mut}}\) (persona isolation).

---

## Section 5: Audit Event Semantics

- **Successful Admin mutation**
  If \(x = (\mathsf{Admin}, i, a, \mathit{params})\), \(a \in \mathcal{A}_{\mathrm{mut}}\), and \(\mathrm{Eval}(x, \tau) = (r, \tau', \mathit{audit})\) with \(r\) indicating success, then:
  \[
  |\mathit{audit}| = 1.
  \]
  So exactly one audit record per successful Admin mutation.

- **No audit on failure or rejection**
  If \(\mathrm{Eval}(x, \tau)\) is undefined (rejected/invalid), or if it is defined with \(r\) indicating failure:
  \[
  \mathit{audit} = ().
  \]
  So failed or rejected instructions produce zero audit records.

- **Read-only and User**
  For \(a \in \mathcal{A}_{\mathrm{read}}\), or for User persona, we already required \(\mathit{audit} = ()\) when \(\mathrm{Eval}\) is defined (Section 4). So audit events are only for successful Admin mutations.

---

## Section 6: Determinism and Failure Constraints

- **Determinism**
  Same instruction and same tenant state imply unique outcome (including "undefined"):
  \[
  \forall x \in \mathcal{X},\, \forall \tau \in \mathcal{T}: \quad \text{at most one } (r, \tau', \mathit{audit}) \text{ such that } \mathrm{Eval}(x, \tau) = (r, \tau', \mathit{audit}).
  \]
  So: given \((x, \tau)\), the resulting system behavior is deterministic.

- **Failure closed / no side effects on invalid**
  If \(x \notin \mathcal{X}_{\mathrm{valid}}\), or if \(\mathrm{Valid}(x, \tau)\) does not hold (when that predicate is defined), then \(\mathrm{Eval}(x, \tau)\) is **undefined**. In that case we require:
  - No state change: tenant state remains \(\tau\) (from the perspective of this system).
  - No audit: no audit records are produced.
  So invalid instructions "fail closed" with no side effects.

- **Explicit ambiguity**
  The exact definition of "invalid" (beyond \(x \notin \mathcal{X}_{\mathrm{valid}}\)) and the precise semantics of "failure" vs "rejection" are left to the invariant phase; here we only require that whenever the system does not produce a normal success outcome, it produces no state change and no audit.

---

## Section 7: Explicit Non-Goals (What M365 Does NOT Do)

- **No intent or routing**
  M365 does not infer intent, choose persona, or route instructions. It only evaluates the given instruction tuple. So: no function from "user intent" or "request" to \((p, i, a, \mathit{params})\); that is outside the system.

- **No identity resolution**
  Identity \(i \in \mathcal{I}\) is taken as given. M365 does not authenticate, resolve, or validate identity; that is assumed done by the caller (e.g., CAIO).

- **No hidden context**
  Every executed instruction is fully described by \(x = (p, i, a, \mathit{params})\). There are no additional hidden inputs, side channels, or implicit context that affect \(\mathrm{Eval}\). So: instruction completeness.

- **No operator or algorithm specification**
  This document does not define how to compute \(\mathrm{Eval}\), which APIs to call, or any concrete operators or algorithms. It only specifies domains, the type of \(\mathrm{Eval}\), and the constraints on its values.

- **No protocol or API detail**
  No HTTP, no Graph API, no serialization. Only the abstract map \((x, \tau) \mapsto (r, \tau', \mathit{audit})\) and the above constraints.

---

**End of Phase 1 specification.**
