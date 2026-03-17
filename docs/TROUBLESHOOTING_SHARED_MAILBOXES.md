# Troubleshooting Shared Mailbox Email Issues

## Quick Answer: technology@smarthaus.ai Not Receiving Emails

**Most Common Issues:**

1. **Mailbox doesn't exist** - Need to create it
2. **Delivery restrictions** - Mailbox configured to only accept from specific senders
3. **Forwarding misconfigured** - Emails forwarded but not delivered to mailbox
4. **Domain not accepted** - `smarthaus.ai` domain not properly configured in Exchange
5. **Mail flow rules** - Transport rules blocking delivery

---

## Diagnostic Steps

### Step 1: Check if Mailbox Exists

```powershell
Connect-ExchangeOnline
Get-Mailbox -Identity technology@smarthaus.ai
```

**If mailbox doesn't exist:**
```powershell
New-Mailbox -Shared -Name "Technology" -DisplayName "Technology Shared Mailbox" -PrimarySmtpAddress technology@smarthaus.ai
```

### Step 2: Check Delivery Restrictions

```powershell
$mbx = Get-Mailbox -Identity technology@smarthaus.ai
$mbx | Select-Object AcceptMessagesOnlyFrom, AcceptMessagesOnlyFromDLMembers, RejectMessagesFrom
```

**If restrictions exist, remove them:**
```powershell
Set-Mailbox -Identity technology@smarthaus.ai -AcceptMessagesOnlyFrom $null -AcceptMessagesOnlyFromDLMembers $null -RejectMessagesFrom $null
```

### Step 3: Check Forwarding Settings

```powershell
$mbx = Get-Mailbox -Identity technology@smarthaus.ai
$mbx | Select-Object ForwardingAddress, ForwardingSmtpAddress, DeliverToMailboxAndForward
```

**If forwarding is enabled but DeliverToMailboxAndForward is false:**
```powershell
Set-Mailbox -Identity technology@smarthaus.ai -DeliverToMailboxAndForward $true
```

**Or disable forwarding entirely:**
```powershell
Set-Mailbox -Identity technology@smarthaus.ai -ForwardingAddress $null -ForwardingSmtpAddress $null
```

### Step 4: Check Domain Configuration

```powershell
Get-AcceptedDomain | Where-Object {$_.Name -eq "smarthaus.ai"}
```

**If domain not found, add it:**
```powershell
New-AcceptedDomain -Name smarthaus.ai -DomainType Authoritative
```

### Step 5: Check Mail Flow Rules

```powershell
Get-TransportRule | Where-Object {$_.Name -like "*technology*" -or $_.Name -like "*smarthaus.ai*"}
```

**Review rules that might be blocking emails.**

### Step 6: Check Mailbox Statistics

```powershell
Get-MailboxStatistics -Identity technology@smarthaus.ai | Select-Object DisplayName,ItemCount,TotalItemSize,StorageLimitStatus
```

**If mailbox is full, increase quota or clean it up.**

---

## Using the Diagnostic Script

We've created a diagnostic script to automate these checks:

```powershell
cd scripts
./diagnose_shared_mailbox.ps1 -MailboxAddress technology@smarthaus.ai
```

This will check all common issues and provide specific fixes.

---

## Using the Fix Script

To automatically fix common issues:

```powershell
cd scripts
./fix_shared_mailbox_email.ps1 -MailboxAddress technology@smarthaus.ai -CreateIfMissing -RemoveRestrictions -FixForwarding
```

**Options:**
- `-CreateIfMissing` - Creates mailbox if it doesn't exist
- `-RemoveRestrictions` - Removes delivery restrictions
- `-FixForwarding` - Ensures emails stay in mailbox if forwarding is enabled

---

## Common Fixes

### Fix 1: Create Missing Mailbox

```powershell
New-Mailbox -Shared -Name "Technology" -DisplayName "Technology Shared Mailbox" -PrimarySmtpAddress technology@smarthaus.ai
```

### Fix 2: Remove All Restrictions

```powershell
Set-Mailbox -Identity technology@smarthaus.ai `
  -AcceptMessagesOnlyFrom $null `
  -AcceptMessagesOnlyFromDLMembers $null `
  -RejectMessagesFrom $null
```

### Fix 3: Ensure Emails Stay in Mailbox

```powershell
Set-Mailbox -Identity technology@smarthaus.ai -DeliverToMailboxAndForward $true
```

### Fix 4: Add Domain (if missing)

```powershell
New-AcceptedDomain -Name smarthaus.ai -DomainType Authoritative
```

---

## Testing Email Delivery

After fixing, test with:

```powershell
Send-MailMessage `
  -To technology@smarthaus.ai `
  -From your.email@smarthausgroup.com `
  -Subject "Test Email" `
  -Body "Testing mailbox delivery" `
  -SmtpServer smtp.office365.com `
  -UseSsl `
  -Credential (Get-Credential)
```

Or use Outlook to send a test email.

---

## Why technology@smarthaus.ai Isn't in the Provisioning Script

The `provision_agents_shared_mailboxes.ps1` script only creates **39 agent personas** (individual names like "Marcus Chen", "Elena Rodriguez", etc.), not department mailboxes like "technology@smarthaus.ai".

**If you need department mailboxes**, you can either:

1. **Add them to the script** - Modify `$People` array to include department mailboxes
2. **Create them manually** - Use the commands above
3. **Create a separate script** - For department mailboxes

---

## Next Steps

1. **Run diagnostic script** to identify the issue
2. **Run fix script** to apply fixes
3. **Test email delivery** with a test message
4. **Add mailbox to provisioning script** if you want it automated

---

**Last Updated:** 2025-01-28
