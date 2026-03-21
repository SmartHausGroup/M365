"""Embeddable M365 instruction connector for TAI module runtime."""

from __future__ import annotations

import os
import uuid
from typing import Any

from provisioning_api.routers.m365 import execute_instruction_contract

from m365.module.manifest import m365_connector_module_manifest


class M365ConnectorModule:
    """TAI-loadable connector exposing `m365.instruction.execute`."""

    capability_id = "m365.instruction.execute"

    def __init__(self, require_user_context: bool | None = None) -> None:
        self.require_user_context = (
            require_user_context
            if require_user_context is not None
            else _flag_enabled("M365_MODULE_REQUIRE_AUTH", default=True)
        )

    @classmethod
    def manifest(cls) -> dict[str, Any]:
        return m365_connector_module_manifest()

    def capabilities(self) -> list[str]:
        return [self.capability_id]

    def health(self) -> dict[str, Any]:
        return {
            "ok": True,
            "module_id": "m365-connector",
            "capabilities": self.capabilities(),
            "require_user_context": self.require_user_context,
            "allow_mutations": _flag_enabled("ALLOW_M365_MUTATIONS", default=False),
        }

    def invoke(self, capability: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        if capability != self.capability_id:
            return {
                "ok": False,
                "error": f"Unsupported capability '{capability}'",
                "trace_id": self._trace_id(payload),
            }
        return self.execute(payload or {})

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        trace_id = self._trace_id(payload)
        action = payload.get("action")
        if not isinstance(action, str) or not action.strip():
            return {
                "ok": False,
                "error": "action is required",
                "trace_id": trace_id,
            }

        params = payload.get("params", {})
        if not isinstance(params, dict):
            return {
                "ok": False,
                "error": "params must be an object",
                "trace_id": trace_id,
            }

        user_info = self._resolve_user_info(payload)
        return execute_instruction_contract(
            action=action,
            params_payload=params,
            trace_id=trace_id,
            user_info=user_info,
            idempotency_key=self._resolve_idempotency_key(payload),
            require_user_context=self.require_user_context,
        )

    @staticmethod
    def _resolve_user_info(payload: dict[str, Any]) -> dict[str, Any] | None:
        direct = payload.get("user_info")
        if isinstance(direct, dict):
            return direct

        context = payload.get("context")
        if not isinstance(context, dict):
            context = {}

        scoped = context.get("user_info")
        if isinstance(scoped, dict):
            return scoped

        auth = payload.get("auth")
        if not isinstance(auth, dict):
            auth = context.get("auth")
        if isinstance(auth, dict):
            auth_user = auth.get("user_info")
            if isinstance(auth_user, dict):
                return auth_user
            actor = auth.get("actor")
            if isinstance(actor, str) and actor.strip():
                return {"actor": actor.strip()}

        actor = payload.get("actor")
        if isinstance(actor, str) and actor.strip():
            return {"actor": actor.strip()}

        return None

    @staticmethod
    def _resolve_idempotency_key(payload: dict[str, Any]) -> str | None:
        candidates = [
            payload.get("idempotency_key"),
            payload.get("idem_key"),
        ]
        context = payload.get("context")
        if isinstance(context, dict):
            candidates.extend([context.get("idempotency_key"), context.get("idem_key")])
        for candidate in candidates:
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
        return None

    @staticmethod
    def _trace_id(payload: dict[str, Any] | None) -> str:
        if isinstance(payload, dict):
            for key in ("trace_id", "request_id"):
                value = payload.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        return str(uuid.uuid4())


def _flag_enabled(name: str, *, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in ("1", "true", "yes")
