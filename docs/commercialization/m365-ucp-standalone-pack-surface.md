# M365 UCP Standalone Pack Surface

This repository now owns the standalone UCP-facing `m365_pack` surface.

## Boundary

- The M365 repo owns:
  - `src/ucp_m365_pack/contracts.py`
  - `src/ucp_m365_pack/client.py`
  - the focused tests proving that package
- UCP owns:
  - host/runtime registration
  - pack loading from the `M365` owner repo
  - desktop/operator visibility
- The dedicated M365 service still owns:
  - live Microsoft 365 auth-bearing execution
  - JWT-backed caller identity enforcement
  - Graph API interaction

## Live posture

The standalone client is service-mode only for live execution:

- `http_service` when `M365_OPS_ADAPTER_URL` is configured
- `stub` only when `GRAPH_STUB_MODE=1`
- fail closed otherwise

Direct import fallback is intentionally removed from the live path. If the
service is unavailable, the package returns a deterministic failure instead of
silently falling back to embedded execution.
