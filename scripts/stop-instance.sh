#!/usr/bin/env bash
set -euo pipefail

NAME=${NAME:-${1:-m365-dashboard}}

docker compose -p "$NAME" down || true
echo "Stopped instance '$NAME'"

