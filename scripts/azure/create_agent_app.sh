#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./create_agent_app.sh "SmartHaus Agent Platform" smarthaus.ai
# Requires: az CLI logged in as tenant admin

APP_NAME=${1:-SmartHaus Agent Platform}
TENANT_DOMAIN=${2:-smarthaus.ai}

echo "Creating Entra ID application: $APP_NAME"
APP_JSON=$(az ad app create --display-name "$APP_NAME" --query '{appId:appId,id:id}' -o json)
APP_ID=$(echo "$APP_JSON" | jq -r .appId)
OBJ_ID=$(echo "$APP_JSON" | jq -r .id)
echo "AppId: $APP_ID  ObjectId: $OBJ_ID"

echo "Creating service principal"
az ad sp create --id "$APP_ID" 1>/dev/null

echo "Adding Microsoft Graph application permissions"
# Minimal set; adjust as needed
GRAPH_APP_ID=00000003-0000-0000-c000-000000000000
PERMS=(
  "Mail.Send"
  "Mail.ReadWrite"
  "Sites.ReadWrite.All"
  "Tasks.ReadWrite.All"
  "ChannelMessage.Send"
  "User.Read.All"
  "Group.ReadWrite.All"
)
for P in "${PERMS[@]}"; do
  az ad app permission add --id "$APP_ID" --api "$GRAPH_APP_ID" --api-permissions "$(az ad sp show --id $GRAPH_APP_ID --query "oauth2Permissions[?value=='$P'].id" -o tsv)=Role" 1>/dev/null || true
  az ad app permission add --id "$APP_ID" --api "$GRAPH_APP_ID" --api-permissions "$(az ad sp show --id $GRAPH_APP_ID --query "appRoles[?value=='$P'].id" -o tsv)=Role" 1>/dev/null || true
done

echo "Granting admin consent (requires tenant admin)"
az ad app permission admin-consent --id "$APP_ID"

echo "Creating self-signed certificate (1 year)"
mkdir -p certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -subj "/CN=$APP_NAME" \
  -keyout certs/agent_app.key -out certs/agent_app.crt 1>/dev/null
openssl pkcs12 -export -out certs/agent_app.pfx -inkey certs/agent_app.key -in certs/agent_app.crt -passout pass:

THUMBPRINT=$(openssl x509 -in certs/agent_app.crt -noout -fingerprint | sed 's/.*=//;s/://g')
echo "Cert thumbprint: $THUMBPRINT"

echo "Uploading certificate to app"
az ad app certificate add --id "$APP_ID" --cert "@certs/agent_app.crt" 1>/dev/null

TENANT_ID=$(az account show --query tenantId -o tsv)
echo "\nDone. Save these values:"
echo "APP_ID=$APP_ID"
echo "TENANT_ID=$TENANT_ID"
echo "CERT_THUMBPRINT=$THUMBPRINT"
echo "PFX=./certs/agent_app.pfx (no password)"
