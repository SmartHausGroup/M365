# Personas, Agents, and the CAIO Edge Contract (Design Note)

**Status:** Design note — captured for when we implement. Not yet implemented.

---

## Intent

Personas/agents in this project (e.g. in `registry/agents.yaml`) should not exist for their own sake. They should be **physical manifestations of real people** — roles that would actually have **real backend actions** tied to them. Each persona should map to a **subset of the M365 capability set** \(\mathcal{O}\) (the 260 actions in `registry/capability_registry.yaml`). Subsets can **overlap** (e.g. multiple roles can list_users); the point is that every persona has a well-defined, real set of things they can do.

When we model the system as a **DAG**:

- **Node** = an agent (persona).
- **Edge** between that agent and **CAIO** = the place where the “person” interacts with the system.

The **contract for that edge** should be the **entire response** from the instruction API (ok, result/error, trace_id, etc.) — not a subset or a summary. That way the response can be **handed off to VFE** (voice/visual front-end) and the **person is, in effect, talking back to the person** (the user): the same response that came from the backend flows agent → CAIO → VFE → user, so the human sees what “that role” did.

---

## Implications

1. **Persona ↔ actions:** Each persona in `registry/agents.yaml` (or a derived view) should have its `allowed_actions` (or equivalent) defined as a **subset of \(\mathcal{O}\)** — i.e. concrete action names from our capability registry (e.g. `list_users`, `create_group`, `send_mail`), not abstract labels. So we can answer: “What can this role do?” with a list of real, implementable actions.

2. **No decorative personas:** If a persona has no real backend actions mapped, it shouldn’t exist as a first-class agent. Personas = real roles with real capabilities.

3. **Edge contract = full response:** The contract on the edge (agent ↔ CAIO) is the **full M365 instruction response** (e.g. `{ ok, result?, error?, trace_id? }` with result shape in \(\mathcal{S}_{\texttt{action}}\) when ok). That is what gets passed to VFE so the “person” can talk back to the user with the actual outcome.

4. **Overlap is fine:** Different personas can share actions (e.g. list_users, get_user). What matters is that each persona’s set is a subset of \(\mathcal{O}\) and is justified by the role.

---

## References

- **Capability universe:** `docs/contracts/M365_CAPABILITIES_UNIVERSE.md`, `registry/capability_registry.yaml`, `docs/contracts/M365_MASTER_CALCULUS_ACTIONS.md`.
- **Agents registry:** `registry/agents.yaml` (today uses abstract action names; future: map to \(\mathcal{O}\)).
- **CAIO ↔ M365 contract:** `docs/contracts/caio-m365/M365_MASTER_CALCULUS.md`, `docs/contracts/caio-m365/ACTION_SPECIFICATION.md` — response shape is the edge contract.
- **Capabilities and agents overview:** `docs/CAPABILITIES_AND_AGENTS.md`.

---

## When we implement

- Define each persona’s **allowed_actions** as a subset of \(\mathcal{O}\) (by action name).
- Ensure the **response** returned from the instruction API (per action) is the **entire** contract payload passed to VFE for that agent’s edge.
- Prune or justify any persona that has no real backend actions.
