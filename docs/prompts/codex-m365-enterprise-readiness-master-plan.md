# Codex Detailed Prompt: M365 Enterprise Readiness Master Plan

**Plan reference:** `plan:m365-enterprise-readiness-master-plan:R1`
**Detailed plan:** `plans/m365-enterprise-readiness-master-plan/m365-enterprise-readiness-master-plan.md`
**Approval status:** Planning artifact created. Execute open phases only after explicit approval for the relevant phase.

---

## Executive summary

This is the one active enterprise-readiness program for standalone M365 v1. It absorbs the commercialization-definition work already completed and makes the real critical path explicit: runtime hardening first, live-tenant certification second, launch collateral and handoff last.

## Current state

- Historical foundation `A1` through `A4` is complete.
- The old commercialization plan is now historical input, not the active execution path.
- The next real blocker is `B1` runtime config authority remediation.
- `D1` and `D2` are downstream launch phases and must not be used to imply readiness before `B` and `C` are green.

## Required execution order

Execute in this order:

1. `B1` Runtime Config Authority Remediation
2. `B2` Fail-Closed Governance and Approval Remediation
3. `B3` Admin Audit and Evidence-Surface Remediation
4. `C1` Live-Tenant Certification Execution
5. `C2` Release Certification Packet and Decision
6. `D1` Enterprise Collateral Pack
7. `D2` Pilot Acceptance and Customer Handoff

## Execution rules

- Treat `docs/commercialization/` as completed foundation, not as proof of enterprise readiness by itself.
- Do not claim enterprise readiness until `B`, `C`, and `D` are complete.
- Any tenant-impacting work in `C1` requires explicit approval before execution.
- Keep `Operations/EXECUTION_PLAN.md` and `Operations/ACTION_LOG.md` synchronized after every phase.
- If a phase changes product definition, operator model, or success criteria, update `Operations/NORTHSTAR.md`.

## References

- `plans/m365-enterprise-readiness-master-plan/m365-enterprise-readiness-master-plan.md`
- `plans/m365-enterprise-commercialization-readiness/m365-enterprise-commercialization-readiness.md`
- `Operations/NORTHSTAR.md`
- `Operations/EXECUTION_PLAN.md`
- `docs/commercialization/`
