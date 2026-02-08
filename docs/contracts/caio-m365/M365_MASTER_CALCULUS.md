# M365 Master Calculus — System-Level Mathematical Guarantee

**Status:** Draft  
**Source of truth:** `docs/contracts/caio-m365/MATHEMATICS.md` (Eq. 1–5), this document.

---

## 1. Purpose

This document defines the **single, system-level guarantee** for the M365 instruction API: every response is produced by a pipeline that satisfies **postcondition** (Eq. 1–2), **idempotency** when a key is present (Eq. 3), **authentication** when required (Eq. 4), and **audit** (Eq. 5). All sub-equations are tied to invariants and lemmas; verification and CI enforce them.

---

## 2. Master Equation (Top-Level)

Let \(R\) be a valid request (action \(\in \mathcal{A}\), params per schema), \(H\) headers (optional `Idempotency-Key`, optional `X-CAIO-API-Key`). The system response is:

\[
\boxed{
  S = \mathrm{InstructionResponse}(R, H)
  = \mathrm{AuthGate}(H) \,\circ\,
  \mathrm{IdempotencyLookup}(H, R) \,\circ\,
  \mathrm{Execute}(R) \,\circ\,
  \mathrm{Audit}(R, S).
}
\]

- **AuthGate:** If API key is required and missing/invalid → return 401 (Eq. 4). Otherwise pass.
- **IdempotencyLookup:** If \(H\) has same `Idempotency-Key` and body as a prior success → return cached \(S_1\) (Eq. 3); else continue.
- **Execute:** Run action; produce \(S\) satisfying Eq. 1 (success) or Eq. 2 (error).
- **Audit:** For every execution path that produces \(S\), write exactly one audit record (Eq. 5) when audit is enabled.

So every \(S\) that reaches the client satisfies:

\[
\bigl( \mathtt{ok}(S) \Rightarrow \mathtt{result}(S) \neq \mathtt{null} \wedge \mathtt{shape}(\mathtt{result}(S)) \in \mathcal{S}_{\mathtt{action}} \bigr)
\;\wedge\;
\bigl( \neg\mathtt{ok}(S) \Rightarrow \mathtt{error}(S) \neq \mathtt{null} \bigr)
\;\wedge\;
\text{(when key + same body replayed)} \; S_2 = S_1
\;\wedge\;
\text{(when audit enabled)} \; \text{one record per request}.
\]

---

## 3. Sub-Equations and Invariant Mapping

| Equation | Constraint | Invariant | Lemma |
|----------|------------|-----------|--------|
| **Eq. 1** | Success ⇒ result non-null, shape ∈ \(\mathcal{S}_{\texttt{action}}\) | INV-CAIO-M365-001 | L1 |
| **Eq. 2** | Error ⇒ error non-null | INV-CAIO-M365-001 | L1 |
| **Eq. 3** | Same Idempotency-Key + same body + first success ⇒ second response = first (cached) | INV-CAIO-M365-002 | L2 |
| **Eq. 4** | Key required and missing/invalid ⇒ status 401 | INV-CAIO-M365-003 | L3 |
| **Eq. 5** | Every instruction execution (success or error) ⇒ exactly one audit record when audit enabled | INV-M365-AUDIT-001 | L4 |

---

## 4. Composition Rules

1. **Postcondition first:** Execute always produces \(S\) satisfying Eq. 1 or Eq. 2 before audit is written.
2. **Idempotency before execute:** If a cached response exists for (key, body), return it without re-executing; audit is still written for the replay (with idempotent_replay flag).
3. **Audit once per request:** Exactly one call to the audit writer per request, whether success, error, blocked, or idempotent replay.
4. **Auth before all:** If auth is required and fails, return 401 and do not execute or write audit for the instruction body (audit may still record the rejected attempt if implemented).

---

## 5. System-Level Guarantee

**Theorem (from composition):** For every valid request \(R\) and headers \(H\), the M365 instruction API either returns an HTTP 401 (auth failure) or a response \(S\) such that:

- \(S\) satisfies the response postcondition (Eq. 1–2).
- If Idempotency-Key was used and the same (key, body) previously succeeded, \(S\) equals the cached response (Eq. 3).
- When audit logging is enabled, exactly one audit record exists for this request (Eq. 5).

Verification: scripts and notebooks produce artifacts for each invariant; CI gates on all artifacts. See `invariants/INDEX.yaml`, `docs/contracts/caio-m365/LEMMAS.md`, and `scripts/ci/verify_*.py`, `notebooks/ma_m365_*.ipynb`.
