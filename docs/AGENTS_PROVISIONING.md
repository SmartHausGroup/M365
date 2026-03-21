# SmartHaus AI Agents – Identity Provisioning (No Extra Licenses)

This sets up 39 AI agent identities as shared mailboxes at `smarthaus.ai` with real names and role aliases, delegates access to an admin, and restricts Graph Mail.* to only these mailboxes.

## Prerequisites
- Accepted domain: `smarthaus.ai` in Microsoft 365
- ExchangeOnlineManagement module
- App registration (Entra ID) with Graph application permissions you intend to use (at least Mail.Send). Note the App (client) ID.

## Run
```powershell
Install-Module ExchangeOnlineManagement -Scope CurrentUser -Force
Connect-ExchangeOnline

# From repo root
cd scripts

# Provision (replace values)
./provision_agents_shared_mailboxes.ps1 `
  -AdminUpn your.user@smarthaus.ai `
  -AppId 00000000-0000-0000-0000-000000000000 `
  -Domain smarthaus.ai
```

What it does:
- Creates 39 shared mailboxes with real names (e.g., `elena.rodriguez@smarthaus.ai`) and role aliases (e.g., `website.manager@smarthaus.ai`)
- Grants FullAccess + SendAs to `-AdminUpn`
- Enables org-wide send-from-alias (if not already)
- Creates security group `SH Agents Mail Access` and adds all agent mailboxes
- Applies Application Access Policy to restrict Graph Mail.* for `-AppId` to that group only

## Verify
```powershell
Get-Mailbox -ResultSize Unlimited | Where-Object {$_.RecipientTypeDetails -eq 'SharedMailbox' -and $_.PrimarySmtpAddress -like '*@smarthaus.ai'} | ft DisplayName,PrimarySmtpAddress
Get-DistributionGroupMember -Identity "SH Agents Mail Access" | ft Name,RecipientType
Test-ApplicationAccessPolicy -AppId <APP_ID> -Identity elena.rodriguez@smarthaus.ai
```

## Notes
- Shared mailbox storage limit ≤ 50GB (no license). If you need litigation hold/compliance, assign licenses selectively.
- Multi-domain aliases can be added later; this baseline uses `@smarthaus.ai` only.
- Teams presence is via Incoming Webhooks or a Teams bot (RSC) using app identity; no user licenses needed for personas.
- For Graph app permissions (example minimal): Mail.Send, Sites.ReadWrite.All, Tasks.ReadWrite.All, ChannelMessage.Send. Grant tenant admin consent.
