#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/deploy-production.sh [--validate-all] [--enable-monitoring] [--go-live]

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[deploy] Preflight checks"
command -v docker >/dev/null || { echo "docker not installed"; exit 1; }
docker compose version >/dev/null || { echo "docker compose missing"; exit 1; }

if [[ "${1:-}" == "--help" ]]; then
  echo "Usage: $0 [--validate-all] [--enable-monitoring] [--go-live]"
  exit 0
fi

ENABLE_MONITORING=false
VALIDATE_ALL=false
GO_LIVE=false

for arg in "$@"; do
  case "$arg" in
    --enable-monitoring) ENABLE_MONITORING=true ;;
    --validate-all) VALIDATE_ALL=true ;;
    --go-live) GO_LIVE=true ;;
  esac
done

export OPS_DRY_RUN=${OPS_DRY_RUN:-false}
export OPA_FAIL_OPEN=${OPA_FAIL_OPEN:-false}
export ENVIRONMENT=${ENVIRONMENT:-production}

echo "[deploy] Bringing up OPA + Ops Adapter (prod overlay)"
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d opa ops-adapter

echo "[deploy] Waiting for services..."
set +e
for i in {1..30}; do
  curl -sf http://127.0.0.1:8080/health >/dev/null && break
  sleep 1
done
for i in {1..30}; do
  curl -sf http://127.0.0.1:8181/health >/dev/null && break
  sleep 1
done
set -e

echo "[deploy] Health checks"
curl -sf http://127.0.0.1:8080/health | jq .

if $ENABLE_MONITORING; then
  echo "[deploy] Monitoring scaffolding enabled (ensure az is logged in)"
  if command -v az >/dev/null; then
    echo "- You can import KQL saved searches from monitoring/kql/*"
  else
    echo "- az not found; skipping monitoring setup"
  fi
fi

if $VALIDATE_ALL; then
  echo "[deploy] Running validation suite"
  ./scripts/validate-production.sh --quick || { echo "Validation failed"; exit 1; }
fi

if $GO_LIVE; then
  echo "[deploy] Go-live flag set. Ensure OPA policies are current and approvals wired."
fi

echo "[deploy] Done."
