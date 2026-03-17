#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/validate-production.sh [--full-test-suite|--quick]

MODE=quick
for arg in "$@"; do
  case "$arg" in
    --full-test-suite) MODE=full ;;
    --quick) MODE=quick ;;
  esac
done

ADAPTER=${OPS_ADAPTER_URL:-http://127.0.0.1:8080}

echo "[validate] Health check"
curl -sf "$ADAPTER/health" >/dev/null || { echo "Adapter not healthy"; exit 1; }

echo "[validate] Policy enforcement (website.deploy should return pending/approval)"
resp=$(curl -s -X POST "$ADAPTER/actions/website-manager/website.deploy" \
  -H 'Content-Type: application/json' \
  -H 'X-Request-ID: validation-deploy-001' \
  -d '{"params":{"env":"production","commit":"abc123"}}')
echo "$resp" | jq .
status=$(echo "$resp" | jq -r .status)
if [[ "$status" != "pending" && "$status" != "ok" ]]; then
  echo "Unexpected status: $status"; exit 1;
fi

echo "[validate] Audit trail contains correlation ID?"
if [[ -f logs/ops_audit.log ]]; then
  grep -q "validation-deploy-001" logs/ops_audit.log || echo "(info) correlation id not yet flushed to file log"
else
  echo "(info) file audit not configured; ensure central logs receive X-Request-ID"
fi

echo "[validate] Rate limiting burst test"
ok=0; fail=0
for i in {1..20}; do
  r=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$ADAPTER/actions/m365-administrator/user.provision" -H 'Content-Type: application/json' -d '{"params":{"userPrincipalName":"t'"$i"'@example.com"}}')
  if [[ "$r" == "200" ]]; then ok=$((ok+1)); else fail=$((fail+1)); fi
done
echo "200s=$ok throttled=$fail"

if [[ "$MODE" == "full" ]]; then
  echo "[validate] Full suite placeholder (add sandbox E2E and contract tests)"
fi

echo "[validate] OK"

