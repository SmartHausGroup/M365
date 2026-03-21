# Lemma L44 — M365 Humanized Delegation Interface v1

## Statement

If the runtime resolves natural-language delegation requests through the authoritative persona
registry and a bounded pattern set, then named digital employees become addressable through human
phrases without allowing ambiguous or non-authoritative persona resolution.

## Inputs

- `registry/persona_registry_v2.yaml`
- `registry/humanized_delegation_interface_v1.yaml`
- `src/ops_adapter/personas.py`
- `src/ops_adapter/main.py`
- `src/ops_adapter/app.py`

## Proof Sketch

1. The delegation interface limits supported utterances to a finite pattern registry.
2. Each matched utterance reduces to one target phrase plus an optional task hint.
3. Persona resolution is bounded to the authoritative registry and respects department hints.
4. Ambiguous short-name matches raise a fail-closed error instead of silently choosing.
5. Therefore natural delegation is deterministic, bounded, and auditable.

## Machine Bindings

- `scripts/ci/verify_humanized_delegation_interface_v1.py`
- `tests/test_humanized_delegation_interface_v1.py`
