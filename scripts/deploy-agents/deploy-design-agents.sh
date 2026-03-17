#!/usr/bin/env bash
set -euo pipefail
API_BASE="${API_BASE:-http://localhost:9000}"
agents=(brand-guardian ui-designer ux-researcher visual-storyteller whimsy-injector)
for a in "${agents[@]}"; do
  curl -sS -X POST "$API_BASE/api/agents/$a/tasks" -H 'Content-Type: application/json' -d '{"title":"Design: kick off"}' >/dev/null || true
  echo "Seeded task for $a"
done

