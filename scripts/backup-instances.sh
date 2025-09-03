#!/usr/bin/env bash
set -euo pipefail

BACKUP_ROOT=${BACKUP_ROOT:-./backups}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_ROOT"

instances=$(docker ps --filter "label=com.smarthaus.m365=1" --format '{{.Label "com.docker.compose.project"}}' | sort -u)

for name in $instances; do
  echo "Backing up instance: $name"
  host_data="./instances/$name/data"
  if [ ! -d "$host_data" ]; then
    echo "  data directory not found at $host_data, skipping (custom mounts?)"
    continue
  fi
  tar -czf "$BACKUP_ROOT/${name}_data_${TIMESTAMP}.tgz" -C "$host_data" . || true
done

echo "Backups written to $BACKUP_ROOT"

