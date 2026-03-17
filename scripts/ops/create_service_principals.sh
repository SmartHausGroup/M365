#!/usr/bin/env bash
set -euo pipefail

# Requires: az CLI logged in with appropriate permissions
# Inputs: registry/agents.yaml

REGISTRY_FILE=${1:-registry/agents.yaml}
KEYVAULT_NAME=${KEYVAULT_NAME:-}
TENANT_ID=${TENANT_ID:-${AZURE_TENANT_ID:-}}

if [[ -z "$KEYVAULT_NAME" || -z "$TENANT_ID" ]]; then
  echo "Set KEYVAULT_NAME and TENANT_ID (or AZURE_TENANT_ID) env vars." >&2
  exit 1
fi

echo "Creating app registrations for agents from $REGISTRY_FILE"

python - <<'PY' "$REGISTRY_FILE"
import os, sys, yaml, json, subprocess

reg = yaml.safe_load(open(sys.argv[1]))
agents = reg.get('agents', {})
kv = os.environ['KEYVAULT_NAME']

for key, agent in agents.items():
    name = f"shg-{key}"
    print(f"\n=== {name} ===")
    app_json = subprocess.check_output([
        'az','ad','app','create','--display-name',name,'--sign-in-audience','AzureADMyOrg','--enable-id-token-issuance','false'
    ])
    app = json.loads(app_json)
    app_id = app['appId']
    print('App ID:', app_id)
    sp_json = subprocess.check_output(['az','ad','sp','create','--id',app_id])
    sp = json.loads(sp_json)
    print('SP Object ID:', sp.get('id'))

    # Create an expiring certificate credential (placeholder)
    subprocess.check_call(['az','ad','app','credential','reset','--id',app_id,'--append','--cert','--years','1','--display-name','ops-adapter'])

    print('Reminder: upload the certificate to Key Vault:', kv, 'and assign app roles as per registry policy')

print('\nDone. Assign required app roles per registry/agents.yaml')
PY

