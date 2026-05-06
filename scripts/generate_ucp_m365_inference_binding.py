from __future__ import annotations

import json
import sys
from hashlib import sha256
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from smarthaus_common.executor_routing import executor_route_for_action  # noqa: E402

SCHEMA_VERSION = "ucp-marketplace-inference-binding-v1"
TARGET_PACK_ID = "com.smarthaus.m365"
TARGET_PACK_VERSION = "0.1.4"

READ_PREFIXES = (
    "list",
    "get",
    "read",
    "search",
    "show",
)
READ_ACTION_PREFIXES = (
    "audit.",
    "directory.",
    "health.",
    "reports.",
    "security.alert",
    "security.incident",
    "security.secure_score",
    "service_principals.list",
    "apps.list",
    "apps.get",
    "ca.policies",
    "ca.policy_get",
    "ca.named_locations",
    "devices.list",
    "devices.get",
    "devices.compliance",
    "mail.list",
    "mail.read",
    "mail.folders",
    "mailbox.settings",
    "files.list",
    "files.get",
    "files.search",
    "sites.",
    "lists.",
    "drives.list",
)
MUTATION_TOKENS = (
    "add",
    "archive",
    "approve",
    "assign",
    "create",
    "delete",
    "deploy",
    "disable",
    "forward",
    "move",
    "offboard",
    "onboard",
    "prepare",
    "process",
    "provision",
    "publish",
    "purge",
    "remove",
    "renew",
    "reply",
    "respond",
    "restore",
    "schedule",
    "send",
    "share",
    "update",
    "upload",
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected YAML object: {path}")
    return payload


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _humanize_action(action: str) -> str:
    return action.replace("_", " ").replace("-", " ").replace(".", " ").strip()


def _aliases_for_action(action: str) -> list[str]:
    base = _humanize_action(action)
    aliases = [base]
    parts = base.split()
    if parts:
        aliases.append(" ".join(parts))
        if parts[0] in {"users", "groups", "teams", "files", "sites", "reports"} and len(parts) > 1:
            aliases.append(f"{parts[1]} {parts[0]}")
    if action.endswith(".list") or action.startswith("list_"):
        noun = parts[0] if parts else base
        aliases.extend([f"list {noun}", f"show {noun}"])
    if action.endswith(".get") or action.startswith("get_"):
        noun = parts[0] if parts else base
        aliases.append(f"get {noun}")
    return sorted({alias for alias in aliases if alias})


def _mutation_class(action: str) -> str:
    normalized = action.strip().lower()
    if normalized.startswith(READ_ACTION_PREFIXES):
        return "read"
    if normalized.split(".", 1)[0] in READ_PREFIXES or normalized.split("_", 1)[0] in READ_PREFIXES:
        return "read"
    if any(token in normalized.replace(".", "_").replace("-", "_").split("_") for token in MUTATION_TOKENS):
        return "confirmation_required"
    return "read"


def _required_params(action: str) -> list[str]:
    normalized = action.strip().lower()
    if normalized in {"users.read", "users.update", "users.disable"}:
        return ["userPrincipalName"]
    if normalized.startswith("groups.") and normalized not in {"groups.list", "groups.create"}:
        return ["groupId"]
    if normalized in {"groups.add_member", "groups.remove_member"}:
        return ["groupId", "userId"]
    if normalized.startswith("teams.") and normalized not in {"teams.list", "teams.create"}:
        return ["teamId"]
    if normalized.startswith("channels."):
        return ["teamId"]
    if normalized.startswith("calendar.") and normalized not in {"calendar.list", "calendar.availability"}:
        return ["userId"]
    if normalized.startswith("mail.") and normalized not in {"mail.list", "mail.folders"}:
        return ["userId"]
    if normalized.startswith("files.") and normalized not in {"files.list", "files.search"}:
        return ["driveId"]
    if normalized.startswith("lists.") and normalized not in {"lists.list"}:
        return ["siteId"]
    if normalized.startswith("security.alert_get"):
        return ["alertId"]
    if normalized.startswith("security.incident_get"):
        return ["incidentId"]
    if normalized.startswith("ca.policy_") and normalized not in {"ca.policy_create"}:
        return ["policyId"]
    if normalized.startswith("devices.get") or normalized.startswith("devices.actions"):
        return ["deviceId"]
    return []


def _tool_for_action(agent_id: str, action: str) -> str:
    # Use the generic MCP tool for execution because it accepts every agent/action
    # pair and preserves the selected persona in the final Graph request.
    executor_route_for_action(agent_id, action)
    return "m365_action"


def _job_function(persona: dict[str, Any]) -> str:
    responsibilities = [str(item) for item in persona.get("responsibilities", []) if item]
    if responsibilities:
        return "; ".join(responsibilities[:3]) + "."
    return str(persona.get("title") or persona.get("canonical_agent") or "M365 workflow support.")


def _persona_contract(persona: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract_id": f"m365-agent-contract:{persona['persona_id']}:v1",
        "identity": {
            "persona_id": persona["persona_id"],
            "person_name": persona["display_name"],
            "title": persona["title"],
            "department": persona["department"],
            "manager": persona["manager"],
            "escalation_owner": persona["escalation_owner"],
        },
        "access_boundary": {
            "allowed_domains": persona.get("allowed_domains", []),
            "allowed_actions": persona.get("allowed_actions", []),
            "denied_by_default": True,
            "external_presence_policy": persona.get("external_presence_policy"),
        },
        "approval_profile": {
            "risk_tier": persona.get("risk_tier"),
            "approval_owner": persona.get("approval_owner"),
            "approval_profile": persona.get("approval_profile"),
            "mutations_require": ["UCP Execute", "operator admission"],
        },
        "said_scope": {
            "allowed": "SAID may lock only one action listed in this persona contract.",
            "refuse": "SAID must refuse requests outside this persona contract.",
            "repair": "SAID must request exact missing parameters before action execution.",
        },
    }


def build_binding() -> dict[str, Any]:
    ai_team_path = REPO / "registry" / "ai_team.json"
    agents_path = REPO / "registry" / "agents.yaml"
    persona_registry_path = REPO / "registry" / "persona_registry_v2.yaml"
    persona_map_path = REPO / "registry" / "persona_capability_map.yaml"

    ai_team = _read_json(ai_team_path)
    agents = _read_yaml(agents_path).get("agents", {})
    persona_registry = _read_yaml(persona_registry_path)
    personas = persona_registry.get("personas", {})
    if not isinstance(personas, dict):
        raise ValueError("persona_registry_missing_personas")

    projected_personas: list[dict[str, Any]] = []
    for persona_id in sorted(personas):
        persona = personas[persona_id]
        allowed_actions = []
        for action in persona.get("allowed_actions", []):
            action_id = str(action)
            allowed_actions.append(
                {
                    "action_id": action_id,
                    "tool": _tool_for_action(persona_id, action_id),
                    "mutation_class": _mutation_class(action_id),
                    "required_params": _required_params(action_id),
                    "aliases": _aliases_for_action(action_id),
                }
            )
        allowed_tools = sorted({action["tool"] for action in allowed_actions})
        if persona.get("status") == "active" and not allowed_actions:
            raise ValueError(f"active_persona_has_no_actions:{persona_id}")
        projected_personas.append(
            {
                "agent_id": persona_id,
                "person_name": persona["display_name"],
                "display_name": persona["title"],
                "job_function": _job_function(persona),
                "department": persona["department"],
                "status": persona["status"],
                "coverage_status": persona["coverage_status"],
                "approval_profile": persona["approval_profile"],
                "approval_owner": persona["approval_owner"],
                "manager": persona["manager"],
                "escalation_owner": persona["escalation_owner"],
                "risk_tier": persona["risk_tier"],
                "allowed_domains": persona.get("allowed_domains", []),
                "allowed_tools": allowed_tools,
                "allowed_actions": allowed_actions,
                "examples": [
                    alias.capitalize()
                    for action in allowed_actions[:3]
                    for alias in action["aliases"][:1]
                ],
                "contract": _persona_contract(persona),
            }
        )

    summary = persona_registry["summary"]
    binding = {
        "schema_version": SCHEMA_VERSION,
        "binding_id": "com.smarthaus.m365.inference-binding.v1",
        "source": {
            "repo": "M365",
            "ai_team_sha256": _sha256(ai_team_path),
            "agents_sha256": _sha256(agents_path),
            "persona_registry_sha256": _sha256(persona_registry_path),
            "persona_capability_map_sha256": _sha256(persona_map_path),
        },
        "summary": {
            "persona_count": len(projected_personas),
            "active_personas": int(summary["active_personas"]),
            "planned_personas": int(summary["planned_personas"]),
            "registry_backed_personas": int(summary["registry_backed_personas"]),
            "persona_contract_only_personas": int(summary["persona_contract_only_personas"]),
            "action_count": sum(len(p["allowed_actions"]) for p in projected_personas),
            "source_total_agents": int(ai_team["total_agents"]),
            "source_registry_agents": len(agents),
        },
        "engine": {
            "id": "said.pack_intent_lock.v1",
            "runtime_contract": "said-pack-context-intent-lock-v1",
            "sealed_runtime_required": True,
        },
        "target_pack": {
            "pack_id": TARGET_PACK_ID,
            "version": TARGET_PACK_VERSION,
            "package_category": "capability_pack",
        },
        "personas": projected_personas,
        "fact_packets": [
            {
                "packet_id": "m365_persona_contracts",
                "source": "registry/persona_registry_v2.yaml",
                "description": "Authoritative M365 persona contract partition.",
            },
            {
                "packet_id": "m365_agent_actions",
                "source": "registry/agents.yaml",
                "description": "Allowed M365 action registry by persona.",
            },
        ],
        "mutation_policy": {
            "read_only_execution": "Read actions may execute after SAID locks a contract-valid intent.",
            "mutations_require": ["UCP Execute", "operator admission", "audit receipt"],
        },
        "refusal_boundaries": [
            "Unknown persona",
            "Persona status is planned",
            "Requested action is not listed in selected persona contract",
            "SAID result action/tool/mutation class does not match the binding",
            "Mutation requested without UCP admission",
        ],
    }
    expected = binding["summary"]
    if expected["persona_count"] != 59:
        raise ValueError(f"persona_count_mismatch:{expected['persona_count']}")
    if expected["active_personas"] != 54 or expected["planned_personas"] != 5:
        raise ValueError("persona_partition_mismatch")
    if expected["persona_count"] != expected["source_total_agents"]:
        raise ValueError("ai_team_persona_count_mismatch")
    return binding


def main() -> None:
    binding = build_binding()
    generated = REPO / "configs" / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    binding_path = generated / "m365_inference_binding.json"
    contracts_path = generated / "m365_agent_contracts.json"
    binding_path.write_text(json.dumps(binding, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    contracts_path.write_text(
        json.dumps(
            {
                "schema_version": "m365-agent-contracts-v1",
                "source_binding": binding["binding_id"],
                "summary": binding["summary"],
                "contracts": [
                    {
                        "agent_id": persona["agent_id"],
                        "person_name": persona["person_name"],
                        "display_name": persona["display_name"],
                        "status": persona["status"],
                        "contract": persona["contract"],
                    }
                    for persona in binding["personas"]
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
