#!/usr/bin/env bash
set -euo pipefail

NAME=${NAME:-${1:-}}
ARCHIVE=${ARCHIVE:-${2:-}}

if [ -z "$NAME" ] || [ -z "$ARCHIVE" ]; then
  echo "Usage: NAME=<instance> ARCHIVE=<backup.tgz> $0"
  exit 1
fi

DATA_DIR=${HOST_DATA:-./instances/$NAME/data}
mkdir -p "$DATA_DIR"

tar -xzf "$ARCHIVE" -C "$DATA_DIR"
echo "Restored $ARCHIVE to $DATA_DIR"
