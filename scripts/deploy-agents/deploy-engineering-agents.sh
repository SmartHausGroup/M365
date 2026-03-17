#!/usr/bin/env bash
set -euo pipefail
API_BASE="${API_BASE:-http://localhost:9000}"
agents=(ai-engineer backend-architect devops-automator frontend-developer mobile-app-builder rapid-prototyper test-writer-fixer)
for a in "${agents[@]}"; do
  curl -sS -X POST "$API_BASE/api/agents/$a/tasks" -H 'Content-Type: application/json' -d '{"title":"Eng: bootstrap task"}' >/dev/null || true
  echo "Seeded task for $a"
done

