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
REGISTRY_PATH = REPO_ROOT / "registry" / "forms_approvals_connectors_expansion_v2.yaml"
CAPABILITY_REGISTRY_PATH = REPO_ROOT / "registry" / "capability_registry.yaml"
ARTIFACT_PATH = (
    REPO_ROOT / "configs" / "generated" / "forms_approvals_connectors_expansion_verification.json"
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
                if not isinstance(node.value, ast.Set | ast.List | ast.Tuple):
                    continue
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
    expansion = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8")) or {}
    capability_registry = yaml.safe_load(CAPABILITY_REGISTRY_PATH.read_text(encoding="utf-8")) or {}
    supported_actions = expansion.get("supported_actions") or {}
    router_supported_actions, instruction_schema_actions = _load_router_literals()
    capability_actions = {
        item["action"]: item
        for item in (capability_registry.get("actions") or [])
        if isinstance(item, dict) and item.get("action")
    }

    missing_in_supported_set: list[str] = []
    missing_in_schema: list[str] = []
    capability_mismatches: list[str] = []
    route_mismatches: list[str] = []
    auth_mismatches: list[str] = []
    approval_mismatches: list[str] = []

    for action, definition in supported_actions.items():
        if action not in router_supported_actions:
            missing_in_supported_set.append(action)
        if action not in instruction_schema_actions:
            missing_in_schema.append(action)

        capability_alias = str(definition.get("capability_registry_alias") or "")
        capability_entry = capability_actions.get(capability_alias)
        if not capability_entry or capability_entry.get("status") != "implemented":
            capability_mismatches.append(action)

        expected_route = "powerplatform" if action.startswith(("get_approval", "list_approval", "create_approval", "respond_to_approval")) else "knowledge"
        if executor_route_for_action(None, action) != expected_route:
            route_mismatches.append(action)

        auth = resolve_action_auth("m365-administrator", action, {})
        expected_auth = "delegated" if expected_route == "powerplatform" else "app_only"
        if auth.auth_class != expected_auth or auth.executor_domain != expected_route:
            auth_mismatches.append(action)

        approval = resolve_action_approval_risk("m365-administrator", action, {})
        expected_profile = str(definition.get("approval_profile") or "")
        if approval.approval_profile != expected_profile:
            approval_mismatches.append(action)

    passed = not any(
        (
            missing_in_supported_set,
            missing_in_schema,
            capability_mismatches,
            route_mismatches,
            auth_mismatches,
            approval_mismatches,
        )
    )
    artifact = {
        "passed": passed,
        "supported_actions_count": len(supported_actions),
        "missing_in_supported_set": missing_in_supported_set,
        "missing_in_instruction_schema": missing_in_schema,
        "capability_registry_mismatches": capability_mismatches,
        "route_mismatches": route_mismatches,
        "auth_mismatches": auth_mismatches,
        "approval_profile_mismatches": approval_mismatches,
    }
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(
        "verify_forms_approvals_connectors_expansion:",
        "PASSED" if passed else "FAILED",
        f"({len(supported_actions)} actions)",
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
