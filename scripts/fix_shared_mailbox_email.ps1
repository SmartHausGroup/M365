# Fix Shared Mailbox Email Delivery Issues
# Usage: ./fix_shared_mailbox_email.ps1 -MailboxAddress technology@smarthaus.ai

param(
  [Parameter(Mandatory=$true)] [string]$MailboxAddress,
  [switch]$CreateIfMissing,
  [switch]$RemoveRestrictions,
  [switch]$FixForwarding
)

Write-Host "🔧 Fixing Shared Mailbox: $MailboxAddress" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if mailbox exists
$mailbox = Get-Mailbox -Identity $MailboxAddress -ErrorAction SilentlyContinue

if (-not $mailbox) {
  if ($CreateIfMissing) {
    Write-Host "📧 Creating shared mailbox: $MailboxAddress" -ForegroundColor Yellow
    $name = ($MailboxAddress -split '@')[0]
    $displayName = "$name Shared Mailbox"
    New-Mailbox -Shared -Name $name -DisplayName $displayName -PrimarySmtpAddress $MailboxAddress
    Write-Host "  ✅ Mailbox created" -ForegroundColor Green
    Start-Sleep -Seconds 2
    $mailbox = Get-Mailbox -Identity $MailboxAddress
  } else {
    Write-Host "  ❌ Mailbox does not exist. Use -CreateIfMissing to create it." -ForegroundColor Red
    exit 1
  }
}

Write-Host "✅ Mailbox found: $($mailbox.DisplayName)" -ForegroundColor Green
Write-Host ""

# Fix 1: Remove delivery restrictions
if ($RemoveRestrictions) {
  Write-Host "🔓 Removing delivery restrictions..." -ForegroundColor Yellow
  Set-Mailbox -Identity $MailboxAddress -AcceptMessagesOnlyFrom $null -AcceptMessagesOnlyFromDLMembers $null -RejectMessagesFrom $null
  Write-Host "  ✅ Delivery restrictions removed" -ForegroundColor Green
  Write-Host ""
}

# Fix 2: Fix forwarding (ensure emails stay in mailbox)
if ($FixForwarding) {
  Write-Host "📬 Fixing forwarding settings..." -ForegroundColor Yellow
  $currentForwarding = Get-Mailbox -Identity $MailboxAddress | Select-Object -ExpandProperty ForwardingAddress
  $currentForwardingSMTP = Get-Mailbox -Identity $MailboxAddress | Select-Object -ExpandProperty ForwardingSmtpAddress

  if ($currentForwarding -or $currentForwardingSMTP) {
    Write-Host "  ⚠️  Forwarding detected. Setting DeliverToMailboxAndForward to true..." -ForegroundColor Yellow
    Set-Mailbox -Identity $MailboxAddress -DeliverToMailboxAndForward $true
    Write-Host "  ✅ Emails will now be delivered to mailbox AND forwarded" -ForegroundColor Green
  } else {
    Write-Host "  ✅ No forwarding configured (emails stay in mailbox)" -ForegroundColor Green
  }
  Write-Host ""
}

# Fix 3: Ensure mailbox is enabled
Write-Host "✅ Ensuring mailbox is enabled for email..." -ForegroundColor Yellow
Set-Mailbox -Identity $MailboxAddress -EmailAddresses @{Add="$MailboxAddress"}
Write-Host "  ✅ Mailbox email address confirmed" -ForegroundColor Green
Write-Host ""

# Fix 4: Check domain
$domain = ($MailboxAddress -split '@')[1]
$acceptedDomain = Get-AcceptedDomain | Where-Object { $_.Name -eq $domain }
if (-not $acceptedDomain) {
  Write-Host "⚠️  Domain '$domain' not accepted. Adding..." -ForegroundColor Yellow
  New-AcceptedDomain -Name $domain -DomainType Authoritative
  Write-Host "  ✅ Domain added" -ForegroundColor Green
} else {
  Write-Host "✅ Domain '$domain' is accepted" -ForegroundColor Green
}
Write-Host ""

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✅ Fixes Applied" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📧 Mailbox should now receive emails." -ForegroundColor Green
Write-Host ""
Write-Host "To verify, check mailbox with:" -ForegroundColor Cyan
Write-Host "  Get-Mailbox -Identity '$MailboxAddress' | Select-Object DisplayName,PrimarySmtpAddress,RecipientTypeDetails" -ForegroundColor White
Write-Host ""
