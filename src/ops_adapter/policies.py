from __future__ import annotations

import os
import httpx
from typing import Any, Dict


class OPAClient:
    def __init__(self, base_url: str | None = None, fail_open: bool | None = None):
        self.base_url = base_url or os.getenv("OPA_URL", "http://localhost:8181")
        # Resolve fail_open precedence:
        # 1) Explicit env OPA_FAIL_OPEN if provided
        # 2) Production defaults to fail closed; others fail open
        if os.getenv("OPA_FAIL_OPEN") is not None:
            try:
                self.fail_open = bool(int(os.getenv("OPA_FAIL_OPEN", "0")))
            except Exception:
                self.fail_open = os.getenv("OPA_FAIL_OPEN", "false").lower() in ("1", "true", "yes")
        else:
            env = (os.getenv("ENVIRONMENT") or os.getenv("OPS_ADAPTER_ENV") or "").lower()
            self.fail_open = not (env in ("prod", "production"))
        self.dev_mode = (os.getenv("OPS_ADAPTER_ENV", "").lower() in ("dev", "sandbox", "local"))

    async def check(self, agent: str, action: str, data: Dict[str, Any], rate_allowed: bool, correlation_id: str) -> Dict[str, Any]:
        payload = {
            "input": {
                "agent": agent,
                "action": action,
                "data": data,
                "rate_allowed": rate_allowed,
                "correlation_id": correlation_id,
                "dev_mode": self.dev_mode,
            }
        }

        url = f"{self.base_url}/v1/data/ops/decision"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                result = resp.json().get("result", {})
                # Normalize
                return {
                    "allowed": bool(result.get("allow", False)),
                    "approval_required": bool(result.get("approval_required", False)),
                    "reason": result.get("reason", "") or "",
                }
        except Exception as e:
            if self.fail_open:
                return {"allowed": True, "approval_required": False, "reason": f"opa_unreachable_fallback: {e}"}
            return {"allowed": False, "approval_required": False, "reason": f"opa_error: {e}"}
