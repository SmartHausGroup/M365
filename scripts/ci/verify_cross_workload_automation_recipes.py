#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from pathlib import Path

import yaml
from smarthaus_common.approval_risk import resolve_action_approval_risk
from smarthaus_common.auth_model import resolve_action_auth
from smarthaus_common.executor_routing import executor_route_for_action

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "registry" / "cross_workload_automation_recipes_v2.yaml"
CAPABILITY_REGISTRY_PATH = REPO_ROOT / "registry" / "capability_registry.yaml"
ARTIFACT_PATH = (
    REPO_ROOT / "configs" / "generated" / "cross_workload_automation_recipes_verification.json"
)
ROUTER_PATH = REPO_ROOT / "src" / "provisioning_api" / "routers" / "m365.py"


def _load_router_literals() -> tuple[set[str], set[str]]:
    tree = ast.parse(ROUTER_PATH.read_text(encoding="utf-8"))
    supported_actions: set[str] = set()
    schema_actions: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "_SUPPORTED_ACTIONS":
                if isinstance(node.value, ast.Set | ast.List | ast.Tuple):
                    supported_actions = {
                        elt.value
                        for elt in node.value.elts
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                    }
            if isinstance(target, ast.Name) and target.id == "INSTRUCTION_ACTIONS_SCHEMA":
                if not isinstance(node.value, ast.List | ast.Tuple):
                    continue
                for item in node.value.elts:
                    if not isinstance(item, ast.Dict):
                        continue
                    for key_node, value_node in zip(item.keys, item.values, strict=False):
                        if (
                            isinstance(key_node, ast.Constant)
                            and key_node.value == "action"
                            and isinstance(value_node, ast.Constant)
                            and isinstance(value_node.value, str)
                        ):
                            schema_actions.add(value_node.value)
    return supported_actions, schema_actions


def main() -> int:
    registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8")) or {}
    capability_registry = yaml.safe_load(CAPABILITY_REGISTRY_PATH.read_text(encoding="utf-8")) or {}
    catalog_actions = registry.get("catalog_actions") or {}
    recipes = registry.get("recipes") or []
    router_supported, router_schema = _load_router_literals()
    capability_actions = {
        item["action"]: item
        for item in (capability_registry.get("actions") or [])
        if isinstance(item, dict) and item.get("action")
    }

    missing_catalog_supported: list[str] = []
    missing_catalog_schema: list[str] = []
    capability_mismatches: list[str] = []
    route_mismatches: list[str] = []
    auth_mismatches: list[str] = []
    approval_mismatches: list[str] = []
    invalid_recipe_ids: list[str] = []
    non_cross_workload_recipes: list[str] = []
    step_action_mismatches: list[str] = []

    for action, definition in catalog_actions.items():
        if action not in router_supported:
            missing_catalog_supported.append(action)
        if action not in router_schema:
            missing_catalog_schema.append(action)
        capability_alias = str(definition.get("capability_registry_alias") or "")
        capability_entry = capability_actions.get(capability_alias)
        if not capability_entry or capability_entry.get("status") != "implemented":
            capability_mismatches.append(action)
        if executor_route_for_action(None, action) != "composite":
            route_mismatches.append(action)
        auth = resolve_action_auth("m365-administrator", action, {})
        if auth.auth_class != "app_only" or auth.executor_domain != "composite":
            auth_mismatches.append(action)
        approval = resolve_action_approval_risk("m365-administrator", action, {})
        if approval.approval_profile != str(definition.get("approval_profile") or ""):
            approval_mismatches.append(action)

    for recipe in recipes:
        recipe_id = str(recipe.get("recipeId") or "")
        if not recipe_id:
            invalid_recipe_ids.append("<missing>")
            continue
        workloads = recipe.get("workloads") or []
        if len(set(workloads)) < 2:
            non_cross_workload_recipes.append(recipe_id)
        for step in recipe.get("steps") or []:
            action = step.get("action")
            if not action:
                step_action_mismatches.append(f"{recipe_id}:<missing>")
                continue
            capability_entry = capability_actions.get(action)
            if not capability_entry or capability_entry.get("status") != "implemented":
                step_action_mismatches.append(f"{recipe_id}:{action}")

    passed = not any(
        (
            missing_catalog_supported,
            missing_catalog_schema,
            capability_mismatches,
            route_mismatches,
            auth_mismatches,
            approval_mismatches,
            invalid_recipe_ids,
            non_cross_workload_recipes,
            step_action_mismatches,
        )
    )
    artifact = {
        "passed": passed,
        "catalog_action_count": len(catalog_actions),
        "recipe_count": len(recipes),
        "missing_catalog_supported": missing_catalog_supported,
        "missing_catalog_schema": missing_catalog_schema,
        "capability_mismatches": capability_mismatches,
        "route_mismatches": route_mismatches,
        "auth_mismatches": auth_mismatches,
        "approval_mismatches": approval_mismatches,
        "invalid_recipe_ids": invalid_recipe_ids,
        "non_cross_workload_recipes": non_cross_workload_recipes,
        "step_action_mismatches": step_action_mismatches,
    }
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(
        "verify_cross_workload_automation_recipes:",
        "PASSED" if passed else "FAILED",
        f"({len(catalog_actions)} catalog actions, {len(recipes)} recipes)",
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
