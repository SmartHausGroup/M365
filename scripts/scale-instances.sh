#!/usr/bin/env bash
set -euo pipefail

BASE_NAME=${NAME:-${1:-m365-scale}}
COUNT=${COUNT:-${2:-3}}
BASE_PORT=${PORT:-${3:-9000}}

for i in $(seq 1 "$COUNT"); do
  name="${BASE_NAME}-${i}"
  port=$(./scripts/port-finder.sh "$BASE_PORT")
  echo "Starting $name on port $port"
  NAME="$name" PORT="$port" ./scripts/start-instance.sh
  BASE_PORT=$((port+1))
done

echo "Scaled to $COUNT instances with base name $BASE_NAME"

