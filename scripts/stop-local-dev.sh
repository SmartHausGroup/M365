#!/usr/bin/env bash
set -euo pipefail

echo "Stopping local development API..."
docker compose -f docker-compose.local.yml down || true
echo "✅ Stopped"
