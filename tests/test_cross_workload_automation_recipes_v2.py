from __future__ import annotations

from collections.abc import Generator

import pytest
from provisioning_api.routers import m365 as m365_router
from smarthaus_common.approval_risk import (
    reload_approval_risk_registry,
    resolve_action_approval_risk,
)
from smarthaus_common.auth_model import reload_auth_model_registry, resolve_action_auth
from smarthaus_common.automation_recipe_client import AutomationRecipeClient
from smarthaus_common.executor_routing import (
    executor_route_for_action,
    reload_executor_routing_registry,
)


def _reload() -> None:
    reload_executor_routing_registry()
    reload_auth_model_registry()
    reload_approval_risk_registry()


def _catalog_actions() -> set[str]:
    return {"list_automation_recipes", "get_automation_recipe"}


def _supported_schema_actions() -> set[str]:
    return {str(item["action"]) for item in m365_router.INSTRUCTION_ACTIONS_SCHEMA}


@pytest.fixture(autouse=True)
def _reload_registries() -> Generator[None, None, None]:
    _reload()
    yield
    _reload()


def test_e3e_instruction_schema_includes_catalog_actions() -> None:
    assert _catalog_actions().issubset(_supported_schema_actions())


def test_e3e_actions_route_auth_and_approval_to_composite() -> None:
    for action in _catalog_actions():
        assert executor_route_for_action(None, action) == "composite"
        auth = resolve_action_auth("m365-administrator", action, {})
        assert auth.executor_domain == "composite"
        assert auth.auth_class == "app_only"
        approval = resolve_action_approval_risk("m365-administrator", action, {})
        assert approval.approval_profile == "low-observe-create"
        assert approval.approval_required is False


def test_e3e_recipe_catalog_is_cross_workload() -> None:
    recipes = AutomationRecipeClient().list_recipes(top=100)
    assert len(recipes) >= 5
    assert all(len(set(recipe["workloads"])) >= 2 for recipe in recipes)


def test_e3e_recipe_catalog_filters_and_get() -> None:
    client = AutomationRecipeClient()

    operations_recipes = client.list_recipes(department="operations", top=10)
    assert operations_recipes
    assert all("operations" in recipe["departments"] for recipe in operations_recipes)

    recipe = client.get_recipe("knowledge_connector_launch")
    assert recipe["recipeId"] == "knowledge_connector_launch"
    assert recipe["title"] == "Knowledge connector launch"
    assert len(recipe["steps"]) >= 5


def test_e3e_instruction_contract_executes_catalog_actions() -> None:
    list_payload = m365_router.execute_instruction_contract(
        action="list_automation_recipes",
        params_payload={"department": "operations", "top": 3},
        trace_id="trace-list-automation-recipes",
    )
    get_payload = m365_router.execute_instruction_contract(
        action="get_automation_recipe",
        params_payload={"recipeId": "incident_response_war_room"},
        trace_id="trace-get-automation-recipe",
    )

    assert list_payload["ok"] is True
    assert list_payload["result"]["count"] <= 3
    assert all(
        "operations" in recipe["departments"] for recipe in list_payload["result"]["recipes"]
    )
    assert get_payload["ok"] is True
    assert get_payload["result"]["recipe"]["recipeId"] == "incident_response_war_room"
