# Phase 1 Formula — M365 Contract System

Plan refs: `plan:m365-ma-scorecard-alignment:R2`, `plan:m365-ma-scorecard-alignment:R5`

## Governing Formula

Let:

- `A` be the declared M365 instruction action set
- `P` be request parameters
- `S` be tenant and runtime state
- `G` be the active governance gates
- `R` be the instruction response
- `Q` be the audit trace side effect

Define the governing instruction evaluation function:

`Eval : A x P x S x G -> (R, Q)`

Subject to the existing contract constraints:

1. `a ∈ A_impl` implies the action is supported by the runtime contract.
2. `auth_invalid => status(R) = 401`
3. `mutating(a) and mutations_disabled(G) => ok(R) = false and error(R) = "m365_mutations_disabled"`
4. `same(idempotency_key, a, P) and first_success => R_replay = R_first`
5. `execution_completed => exactly_one_audit_record(Q)`
6. `same(a, P, S, G) => same(R, Q)` for the current deterministic contract boundary

## Source Mapping

- Intent source: `docs/contracts/caio-m365/INTENT.md`
- Mathematics source: `docs/contracts/caio-m365/MATHEMATICS.md`
- Master calculus source: `docs/contracts/caio-m365/M365_MASTER_CALCULUS.md`
- Capability universe source: `docs/contracts/M365_MASTER_CALCULUS_ACTIONS.md`

## Current Verified Action Surface

The currently implemented and verified runtime action surface is the 9-action set already locked by commercialization `P0A`:

- `list_users`
- `get_user`
- `reset_user_password`
- `list_teams`
- `list_sites`
- `create_site`
- `create_team`
- `add_channel`
- `provision_service`

The broader capability universe remains a contract-universe or roadmap surface, not the current runtime-commercial launch surface.
