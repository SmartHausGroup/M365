#!/usr/bin/env bash
set -euo pipefail

# agent_wrapper.sh
# Orchestrates a Cursor CLI agent run with path guardrails, commits, tests, and PR creation.
# Usage:
#   scripts/agent_wrapper.sh "<instruction text>"
# Optional env:
#   ALLOWED_PATHS: space-separated path prefixes allowed to change (default below)
#   AGENT_SCOPE: short scope string for branch naming (default: mixed)
#   GITHUB_TOKEN: required for gh CLI PR creation in CI
#
# Outputs:
#   - cursor-run.txt: raw output from cursor-agent
#   - test-summary.txt: summarized test results
#   - pr_url.txt: created PR URL (if any)

instruction="${1:-}"
if [[ -z "${instruction}" ]]; then
  echo "ERROR: Instruction text is required as the first argument." >&2
  exit 2
fi

ALLOWED_PATHS_DEFAULT="smarthaus.ai/app/ docs/ api/ src/"
ALLOWED_PATHS="${ALLOWED_PATHS:-$ALLOWED_PATHS_DEFAULT}"
AGENT_SCOPE="${AGENT_SCOPE:-mixed}"

log() {
  echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] $*"
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

require_cmd() {
  if ! command_exists "$1"; then
    echo "ERROR: Required command '$1' not found in PATH." >&2
    exit 3
  fi
}

match_allowed() {
  local file="$1"
  # Reject common disallowed dirs
  case "$file" in
    .git/*|node_modules/*|dist/*|.venv/*|venv/*|.github/*|bin/opa|*.pbix)
      return 1
      ;;
  esac
  # Allow only if under an allowed prefix
  for p in $ALLOWED_PATHS; do
    if [[ "$file" == "$p"* ]]; then
      return 0
    fi
  done
  return 1
}

has_py_tests() {
  [[ -d "tests" ]] || grep -RqsE "^def test_" src/ || return 1
}

has_node_pkg() {
  [[ -f "package.json" ]]
}

has_node_script() {
  local script="$1"
  if ! has_node_pkg; then
    return 1
  fi
  if command_exists jq; then
    jq -e --arg s "$script" '.scripts[$s] // empty | length > 0' package.json >/dev/null 2>&1
  else
    # Fallback using node if available
    if command_exists node; then
      node -e "try {const p=require('./package.json'); process.exit(p.scripts && p.scripts['$script'] ? 0 : 1)} catch {process.exit(1)}" >/dev/null 2>&1
    else
      return 1
    fi
  fi
}

short_sha="$(git rev-parse --short HEAD 2>/dev/null || echo 'nosha')"
ts="$(date -u +%Y%m%d%H%M%S)"
branch="agent/${AGENT_SCOPE}/${short_sha}-${ts}"

require_cmd git
require_cmd cursor-agent
require_cmd gh

log "Creating working branch: ${branch}"
git checkout -b "${branch}"

# Build prompt file for stability with multi-line content
prompt_file="$(mktemp -t agent-prompt-XXXXXX.txt)"
cat > "${prompt_file}" <<'PROMPT'
You are a repo-aware coding agent.
Follow these rules strictly:
- Only edit files under the allowed paths listed below.
- Keep diffs minimal and focused on the instruction.
- Update CHANGELOG.md for user-facing changes.
- Run tests and fix failures; do not disable checks.
- Write descriptive commit messages summarizing changes and rationale.
- Do not touch binaries, node_modules, dist, or CI configs unless explicitly required by the task.

Deliverables:
- Applied and saved changes to the repository files.
- Local commits staged can be created by the wrapper; do not force-push.
- A short summary of changes and files touched.
PROMPT

{
  echo ""
  echo "Instruction:"
  echo "${instruction}"
  echo ""
  echo "Allowed paths:"
  echo "${ALLOWED_PATHS}"
} >> "${prompt_file}"

log "Running cursor-agent with constraints..."
# shellcheck disable=SC2046
cursor-agent -p --force --output-format text "$(cat "${prompt_file}")" | tee cursor-run.txt

log "Staging changes..."
git add -A

changed_files=()
while IFS= read -r f; do
  [[ -n "$f" ]] && changed_files+=("$f")
done < <(git diff --cached --name-only)

if [[ "${#changed_files[@]}" -eq 0 ]]; then
  log "No changes produced by the agent. Exiting without PR."
  echo "No changes produced." > test-summary.txt
  exit 0
fi

log "Enforcing path allowlist..."
blocked=()
for f in "${changed_files[@]}"; do
  if ! match_allowed "$f"; then
    blocked+=("$f")
    git restore --staged --worktree -- "$f" || true
  fi
done

if [[ "${#blocked[@]}" -gt 0 ]]; then
  log "Blocked changes outside allowlist:"
  printf ' - %s\n' "${blocked[@]}"
fi

post_filter_changed=()
while IFS= read -r f; do
  [[ -n "$f" ]] && post_filter_changed+=("$f")
done < <(git diff --cached --name-only)

if [[ "${#post_filter_changed[@]}" -eq 0 ]]; then
  log "All changes were out-of-scope and got reverted. Exiting."
  echo "All changes were out-of-scope and reverted." > test-summary.txt
  exit 0
fi

# Commit allowed changes
summary_line="$(echo "${instruction}" | tr -s ' ' | cut -c1-72)"
commit_msg="agent: ${summary_line}

Instruction:
${instruction}
"
git commit -m "${commit_msg}"

# Test summary file
echo "=== Test Summary ($(date -u +'%Y-%m-%dT%H:%M:%SZ')) ===" > test-summary.txt

py_status="SKIPPED"
if command_exists pytest && has_py_tests; then
  log "Running Python tests..."
  set +e
  pytest -q | tee -a test-summary.txt
  code=$?
  set -e
  if [[ $code -eq 0 ]]; then py_status="PASS"; else py_status="FAIL"; fi
  echo "" >> test-summary.txt
else
  echo "Python tests: not run (pytest or tests not found)" >> test-summary.txt
fi

node_status="SKIPPED"
if command_exists npm && has_node_pkg && has_node_script "test"; then
  log "Running Node tests..."
  set +e
  npm test --silent | tee -a test-summary.txt
  code=$?
  set -e
  if [[ $code -eq 0 ]]; then node_status="PASS"; else node_status="FAIL"; fi
  echo "" >> test-summary.txt
else
  echo "Node tests: not run (no package.json or test script)" >> test-summary.txt
fi

log "Pushing branch and creating PR..."
git push -u origin "${branch}"

title="Agent: ${summary_line}"
pr_body_file="$(mktemp -t agent-pr-body-XXXXXX.md)"
cat > "${pr_body_file}" <<EOF
## What
${instruction}

## How
- Changes created by Cursor CLI agent (wrapped by CI).
- Allowed path scope: ${ALLOWED_PATHS}

## Tests
$(cat test-summary.txt)

## Notes
- Blocked files (if any) outside allowlist were not included in this PR.
- Please review with CODEOWNERS. This PR is labeled as automated.
EOF

set +e
gh pr create \
  --title "${title}" \
  --body-file "${pr_body_file}" \
  --label agent \
  --label automated \
  --head "${branch}" | tee pr_url.txt
gh_status=$?
set -e

if [[ $gh_status -ne 0 ]]; then
  echo "ERROR: Failed to create PR via gh CLI." >&2
  exit 4
fi

log "Done. PR: $(cat pr_url.txt | tail -n1)"
