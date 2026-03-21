#!/usr/bin/env bash
set -euo pipefail

# Usage: ./employee-lifecycle.sh test.user@smarthaus.ai "Test User" [LICENSES]
# LICENSES: comma-separated license aliases or skuPartNumbers (e.g., E3 or E3,E5)

ADAPTER_URL=${OPS_ADAPTER_URL:-http://localhost:8080}
UPN=${1:?"Provide userPrincipalName"}
DISPLAY_NAME=${2:-"Test User"}
LICENSES_CSV=${3:-"E3"}

echo "=== Employee Lifecycle for $UPN ==="

echo "-- Create user"
curl -s -X POST "$ADAPTER_URL/actions/m365-administrator/users.create" \
  -H 'Content-Type: application/json' \
  -d "{\"params\":{\"userPrincipalName\":\"$UPN\",\"displayName\":\"$DISPLAY_NAME\"}}" | jq

echo "-- Read user"
curl -s -X POST "$ADAPTER_URL/actions/m365-administrator/users.read" \
  -H 'Content-Type: application/json' \
  -d "{\"params\":{\"userPrincipalName\":\"$UPN\"}}" | jq

echo "-- Update user (jobTitle, department)"
curl -s -X POST "$ADAPTER_URL/actions/m365-administrator/users.update" \
  -H 'Content-Type: application/json' \
  -d "{\"params\":{\"userPrincipalName\":\"$UPN\",\"jobTitle\":\"Engineer\",\"department\":\"Engineering\"}}" | jq

echo "-- Disable user"
curl -s -X POST "$ADAPTER_URL/actions/m365-administrator/users.disable" \
  -H 'Content-Type: application/json' \
  -d "{\"params\":{\"userPrincipalName\":\"$UPN\"}}" | jq

echo "✅ Lifecycle completed for $UPN"
echo "-- Assign licenses ($LICENSES_CSV)"
curl -s -X POST "$ADAPTER_URL/actions/m365-administrator/licenses.assign" \
  -H 'Content-Type: application/json' \
  -d "{\"params\":{\"userPrincipalName\":\"$UPN\",\"licenses\":[\"${LICENSES_CSV//,/\",\"}\"]}}" | jq

echo "-- Read user (post-licenses)"
curl -s -X POST "$ADAPTER_URL/actions/m365-administrator/users.read" \
  -H 'Content-Type: application/json' \
  -d "{\"params\":{\"userPrincipalName\":\"$UPN\"}}" | jq
