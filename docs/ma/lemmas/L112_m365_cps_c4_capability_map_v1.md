# L112 - M365 Capability Pack C4 Operator Capability Map v1

**Lemma id:** `L112_m365_cps_c4_capability_map_v1`
**Plan reference:** `plan:m365-cps-trkC-p4-operator-capability-map:T2`
**Predecessor:** `L111_m365_cps_c3_docstring_audit_v1`

## Mission

Auto-generate `docs/m365_capability_map.md` from the live runtime
registry, alias table, and `registry/agents.yaml`. The doc is the
operator-facing reference for "what can my M365 capability pack
actually do right now". Regenerated deterministically from source-of-
truth files so it cannot drift.

## Predicate

```
CapabilityMapValid =
    L_GENERATOR_PRESENT
  ∧ L_OUTPUT_DETERMINISTIC
  ∧ L_DOC_HAS_THREE_SECTIONS
  ∧ L_DOC_REFERENCES_LIVE_DATA
```

## Lemmas

### L_GENERATOR_PRESENT

`scripts/generate_m365_capability_map.py` exists and produces output
to stdout (or the `--out` path).

### L_OUTPUT_DETERMINISTIC

Two consecutive runs against the same registry/alias/agents.yaml
produce byte-identical output.

### L_DOC_HAS_THREE_SECTIONS

The generated doc contains:
1. **Implemented actions** — every entry in `READ_ONLY_REGISTRY` with
   workload, endpoint, scopes, auth_modes, min_tier.
2. **Legacy aliases** — every entry in `LEGACY_ACTION_TO_RUNTIME_ACTION`
   showing the legacy → runtime mapping.
3. **Coverage status by agent** — for each agent in `agents.yaml`, the
   per-action breakdown (implemented / aliased / planned).

### L_DOC_REFERENCES_LIVE_DATA

The doc's totals match `len(READ_ONLY_REGISTRY)`,
`len(LEGACY_ACTION_TO_RUNTIME_ACTION)`, and the agents.yaml advertised
totals exactly.
