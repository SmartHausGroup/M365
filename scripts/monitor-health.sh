#!/usr/bin/env bash
set -euo pipefail

instances=$(docker ps --filter "label=com.smarthaus.m365=1" --format '{{.Names}}\t{{.Ports}}\t{{.Label "com.docker.compose.project"}}')

echo -e "NAME\tPORTS\tPROJECT\tHEALTH"
while IFS=$'\t' read -r cname ports proj; do
  health=$(docker inspect --format='{{json .State.Health.Status}}' "$cname" 2>/dev/null || echo '"unknown"')
  echo -e "$cname\t$ports\t$proj\t$health"
done <<< "$instances"

