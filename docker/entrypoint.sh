#!/usr/bin/env sh
set -eu

PORT="${PORT:-9000}"
exec "$@" --port "$PORT"
