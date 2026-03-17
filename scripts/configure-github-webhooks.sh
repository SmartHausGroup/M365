#!/usr/bin/env bash
set -euo pipefail

CONFIG_FILE="config/services.json"

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required. Install jq and retry." >&2
  exit 1
fi

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "GITHUB_TOKEN env var is required (repo/admin:repo_hook)." >&2
  exit 1
fi

if [[ -z "${WEBHOOK_URL:-}" ]]; then
  echo "WEBHOOK_URL env var is required (e.g., https://api.smarthaus.ai/api/webhooks/github/{project})." >&2
  exit 1
fi

SECRET="${GITHUB_WEBHOOK_SECRET:-}"
if [[ -z "$SECRET" ]]; then
  echo "Warning: GITHUB_WEBHOOK_SECRET not set; proceeding without shared secret." >&2
fi

services=$(jq -c '.services[]' "$CONFIG_FILE")

for s in $services; do
  key=$(jq -r '.key' <<<"$s")
  repo=$(jq -r '.github_repo' <<<"$s")

  owner=$(cut -d'/' -f1 <<<"$repo")
  name=$(cut -d'/' -f2 <<<"$repo")

  url=${WEBHOOK_URL//\{project\}/$key}

  echo "Configuring webhook for $repo -> $url"

  # Check existing hooks
  hooks=$(curl -sS -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/$owner/$name/hooks")

  id=$(jq -r --arg url "$url" '.[] | select(.config.url == $url) | .id' <<<"$hooks" || true)

  data=$(jq -n \
    --arg url "$url" \
    --arg secret "$SECRET" \
    '{name:"web", active:true, events:["push","issues","pull_request","release","milestone"], config:{url:$url, content_type:"json", insecure_ssl:"0"}}')

  if [[ -n "$SECRET" ]]; then
    data=$(jq --arg secret "$SECRET" '.config.secret = $secret' <<<"$data")
  fi

  if [[ "$id" != "" && "$id" != "null" ]]; then
    echo "Updating existing hook id=$id"
    curl -sS -X PATCH -H "Authorization: token $GITHUB_TOKEN" \
      -H "Accept: application/vnd.github+json" \
      -d "$data" \
      "https://api.github.com/repos/$owner/$name/hooks/$id" >/dev/null
  else
    echo "Creating new hook"
    curl -sS -X POST -H "Authorization: token $GITHUB_TOKEN" \
      -H "Accept: application/vnd.github+json" \
      -d "$data" \
      "https://api.github.com/repos/$owner/$name/hooks" >/dev/null
  fi
  echo "✔ Hook configured for $repo"
done

echo "All webhooks configured."

