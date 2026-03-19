#!/usr/bin/env bash
set -euo pipefail
API_BASE="${API_BASE:-http://localhost:9000}"
agents=(api-tester performance-benchmarker test-results-analyzer tool-evaluator workflow-optimizer)
for a in "${agents[@]}"; do
  curl -sS -X POST "$API_BASE/api/agents/$a/tasks" -H 'Content-Type: application/json' -d '{"title":"Testing: run suite"}' >/dev/null || true
  echo "Seeded task for $a"
done
