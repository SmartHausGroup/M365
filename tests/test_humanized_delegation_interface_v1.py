from __future__ import annotations

import yaml
from fastapi.testclient import TestClient
from ops_adapter.app import create_app
from ops_adapter.personas import load_persona_registry, resolve_humanized_delegation_request


def _load_personas() -> tuple[dict, dict[str, dict]]:
    with open("registry/agents.yaml", encoding="utf-8") as handle:
        registry = yaml.safe_load(handle)
    return registry, load_persona_registry(registry)


def test_e5b_resolves_talk_to_phrase() -> None:
    _, personas = _load_personas()
    resolution = resolve_humanized_delegation_request("Talk to Elena Rodriguez", personas)

    assert resolution["canonical_agent"] == "website-manager"
    assert resolution["matched_pattern"] == "talk_to"
    assert resolution["task_hint"] is None


def test_e5b_resolves_department_hint() -> None:
    _, personas = _load_personas()
    resolution = resolve_humanized_delegation_request(
        "Route this to Marcus in Operations",
        personas,
    )

    assert resolution["canonical_agent"] == "m365-administrator"
    assert resolution["matched_pattern"] == "route_to"


def test_e5b_fails_closed_on_ambiguous_short_name() -> None:
    _, personas = _load_personas()
    try:
        resolve_humanized_delegation_request("Ask Taylor to review this", personas)
    except ValueError as exc:
        assert str(exc) == "persona_ambiguous:Taylor"
    else:
        raise AssertionError("Expected ambiguous short-name targeting to fail closed")


def test_e5b_app_route_exposes_humanized_resolution() -> None:
    client = TestClient(create_app())

    response = client.get("/personas/resolve", params={"query": "Have Elena Rodriguez handle this"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["canonical_agent"] == "website-manager"
    assert payload["matched_pattern"] == "have_handle"
