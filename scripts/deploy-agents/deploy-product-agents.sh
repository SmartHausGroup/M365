#!/usr/bin/env bash
set -euo pipefail
API_BASE="${API_BASE:-http://localhost:9000}"
agents=(sprint-prioritizer feedback-synthesizer trend-researcher)
for a in "${agents[@]}"; do
  curl -sS -X POST "$API_BASE/api/agents/$a/tasks" -H 'Content-Type: application/json' -d '{"title":"Product: prioritize backlog"}' >/dev/null || true
  echo "Seeded task for $a"
done
