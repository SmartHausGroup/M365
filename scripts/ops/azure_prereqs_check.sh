#!/usr/bin/env bash
set -euo pipefail
echo "[azure] Checking az login and subscription"
command -v az >/dev/null || { echo "az not installed"; exit 1; }
az account show >/dev/null 2>&1 || { echo "Run 'az login' first"; exit 1; }
if [[ -n "${SUBSCRIPTION_ID:-}" ]]; then
  az account set --subscription "$SUBSCRIPTION_ID"
fi
echo "[azure] OK"

