#!/usr/bin/env bash
set -euo pipefail

echo "Starting local development API (Docker) on http://localhost:8000 ..."
docker compose -f docker-compose.local.yml up -d --build
echo "✅ Local API is starting. Tail logs with: make docker-dev-logs"

