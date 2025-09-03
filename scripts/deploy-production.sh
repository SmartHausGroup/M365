#!/usr/bin/env bash
set -euo pipefail

# Example production deploy using docker compose with image

NAME=${NAME:-m365-prod}
PORT=${PORT:-8080}
IMAGE=${IMAGE:-smarthaus/m365-dashboard:latest}

DATA_DIR=${HOST_DATA:-/var/opt/m365/$NAME/data}
CONFIG_DIR=${HOST_CONFIG:-/var/opt/m365/$NAME/config}
LOGS_DIR=${HOST_LOGS:-/var/log/m365/$NAME}

mkdir -p "$DATA_DIR" "$CONFIG_DIR" "$LOGS_DIR"

cat > production/docker-compose.$NAME.yml <<EOF
services:
  dashboard:
    image: ${IMAGE}
    environment:
      - PORT=${PORT}
      - INSTANCE_NAME=${NAME}
      - INSTANCE_ENV=production
      - GRAPH_TENANT_ID
      - GRAPH_CLIENT_ID
      - GRAPH_CLIENT_SECRET
      - SP_HOSTNAME=${SP_HOSTNAME:-smarthausgroup.sharepoint.com}
    ports:
      - "${PORT}:8000"
    volumes:
      - ${DATA_DIR}:/app/data:rw
      - ${CONFIG_DIR}:/app/config:ro
      - ${LOGS_DIR}:/app/logs:rw
    restart: unless-stopped
    labels:
      - "com.smarthaus.m365=1"
      - "com.smarthaus.instance=${NAME}"
EOF

docker compose -f production/docker-compose.$NAME.yml -p "$NAME" up -d
echo "Deployed production instance '$NAME' on port $PORT"

