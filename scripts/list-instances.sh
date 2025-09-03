#!/usr/bin/env bash
set -euo pipefail

docker ps --filter "label=com.smarthaus.m365=1" --format '{{.Names}}\t{{.Ports}}\t{{.Label "com.docker.compose.project"}}\t{{.Label "com.smarthaus.instance"}}'

