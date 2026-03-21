# L21 — M365 Persona-to-Capability and Risk Mapping

## Claim

For the SMARTHAUS workforce-expansion program to remain deterministic after `E0C`, the workforce map is admissible iff:

1. the authoritative persona roster remains the `39`-persona census in `registry/ai_team.json`
2. each authoritative persona is bound to explicit workload families and capability families
3. each authoritative persona is bound to a deterministic approval posture
4. personas without runtime actions are treated as contract-only rather than silently implied to be implemented
5. non-authoritative registry agents are recorded as overflow inventory rather than folded into the workforce by accident

If any of those conditions fails, `E0D` remains incomplete and the expansion program cannot honestly claim that persona coverage is locked.

## Existing Proof Sources

- `Operations/NORTHSTAR.md`
- `plans/m365-ai-workforce-expansion-master-plan/m365-ai-workforce-expansion-master-plan.md`
- `registry/ai_team.json`
- `registry/agents.yaml`
- `registry/persona_capability_map.yaml`
- `docs/commercialization/m365-department-persona-census.md`
- `docs/commercialization/m365-capability-taxonomy-and-feasibility-map.md`
- `docs/commercialization/m365-persona-capability-and-risk-map.md`
- `notebooks/m365/INV-M365-W-persona-capability-risk-mapping.ipynb`
- `notebooks/lemma_proofs/L21_m365_persona_capability_risk_mapping.ipynb`

## Acceptance Evidence

- `registry/persona_capability_map.yaml` covers exactly `39` authoritative personas across `10` departments
- every mapped persona has workload families, capability families, risk tier, approval profile, and coverage status
- the commercialization doc explains the same approval profiles, coverage split, and department/persona bindings
- the plan and tracker state advance from `E0D` to `E0E` without widening scope beyond the locked roster

## Deterministic Surface

`PersonaCoverageLocked = AuthoritativeRoster × CapabilityBindings × ApprovalProfiles × CoverageClassification`

`AuthoritativeRoster = Census39 ∧ DepartmentSet10`

`CoverageClassification = RegistryBacked ∨ PersonaContractOnly`

`OverflowRegistry = RegistryAgents - AuthoritativeRoster`

`E0D_GO = PersonaCoverageLocked ∧ OverflowRegistryDocumented`
