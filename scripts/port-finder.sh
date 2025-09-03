#!/usr/bin/env bash
set -euo pipefail

BASE_PORT=${1:-8000}
MAX=${2:-20000}

is_free() {
  local p="$1"
  if command -v lsof >/dev/null 2>&1; then
    ! lsof -iTCP -sTCP:LISTEN -P -n | awk '{print $9}' | grep -q ":${p}$"
  else
    (echo > /dev/tcp/127.0.0.1/${p}) >/dev/null 2>&1 && return 1 || return 0
  fi
}

port=$BASE_PORT
while [ "$port" -le "$MAX" ]; do
  if is_free "$port"; then
    echo "$port"
    exit 0
  fi
  port=$((port+1))
done

echo "No free port found between $BASE_PORT and $MAX" >&2
exit 1

