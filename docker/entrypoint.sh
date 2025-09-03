#!/usr/bin/env sh
set -eu

PORT="${PORT:-8000}"
exec "$@" --port "$PORT"

