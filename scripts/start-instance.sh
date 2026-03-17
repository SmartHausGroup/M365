#!/usr/bin/env bash
set -euo pipefail

NAME=${NAME:-${1:-m365-dashboard}}
PORT=${PORT:-${2:-9000}}

# Per-instance host dirs
ROOT_DIR=${ROOT_DIR:-instances}
DATA_DIR=${HOST_DATA:-./$ROOT_DIR/$NAME/data}
CONFIG_DIR=${HOST_CONFIG:-./$ROOT_DIR/$NAME/config}
LOGS_DIR=${HOST_LOGS:-./$ROOT_DIR/$NAME/logs}

mkdir -p "$DATA_DIR" "$CONFIG_DIR" "$LOGS_DIR"

export NAME PORT HOST_DATA="$DATA_DIR" HOST_CONFIG="$CONFIG_DIR" HOST_LOGS="$LOGS_DIR"

docker compose -p "$NAME" up -d --build

echo "Started instance '$NAME' on port $PORT"
