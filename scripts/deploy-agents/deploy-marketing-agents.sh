#!/usr/bin/env bash
set -euo pipefail
API_BASE="${API_BASE:-http://localhost:9000}"
agents=(app-store-optimizer content-creator growth-hacker instagram-curator reddit-community-builder tiktok-strategist twitter-engager)
for a in "${agents[@]}"; do
  curl -sS -X POST "$API_BASE/api/agents/$a/tasks" -H 'Content-Type: application/json' -d '{"title":"Marketing: initial task"}' >/dev/null || true
  echo "Seeded task for $a"
done

