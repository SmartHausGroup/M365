# SmartHaus Agent App – Entra ID & Exchange App-Only

## Create the app (Azure CLI)
```bash
cd scripts/azure
./create_agent_app.sh "SmartHaus Agent Platform" smarthaus.ai
# Capture outputs: APP_ID, TENANT_ID, CERT_THUMBPRINT
```

## Connect to Exchange Online (app-only)
```powershell
Install-Module ExchangeOnlineManagement -Scope CurrentUser -Force
Connect-ExchangeOnline
# or use the helper:
cd scripts/exchange
./connect_exo_apponly.ps1 -AppId <APP_ID> -Organization <yourtenant>.onmicrosoft.com -CertificateThumbprint <CERT_THUMBPRINT>
```

## Provision agents
```powershell
cd scripts
./provision_agents_shared_mailboxes.ps1 -AdminUpn your.user@smarthaus.ai -AppId <APP_ID> -Domain smarthaus.ai
```

## Scope Graph Mail.* to agent mailboxes only
The provisioning script creates a security group `SH Agents Mail Access` and applies an Application Access Policy for the app.

## Wire credentials for Ops Adapter
- AppId: `<APP_ID>`
- TenantId: `<TENANT_ID>`
- Certificate: `scripts/azure/certs/agent_app.pfx` (no password) or upload to Key Vault and reference from your runtime.


