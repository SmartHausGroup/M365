# Diagnostic Script for Shared Mailbox Email Issues
# Usage: ./diagnose_shared_mailbox.ps1 -MailboxAddress technology@smarthaus.ai

param(
  [Parameter(Mandatory=$true)] [string]$MailboxAddress
)

Write-Host "🔍 Diagnosing Shared Mailbox: $MailboxAddress" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if mailbox exists
Write-Host "Step 1/7: Checking if mailbox exists..." -ForegroundColor Yellow
$mailbox = Get-Mailbox -Identity $MailboxAddress -ErrorAction SilentlyContinue
if (-not $mailbox) {
  Write-Host "  ❌ Mailbox NOT FOUND: $MailboxAddress" -ForegroundColor Red
  Write-Host "  💡 Solution: Create the mailbox first" -ForegroundColor Yellow
  Write-Host ""
  Write-Host "  To create it, run:" -ForegroundColor Cyan
  Write-Host "    New-Mailbox -Shared -Name 'Technology' -DisplayName 'Technology Shared Mailbox' -PrimarySmtpAddress '$MailboxAddress'" -ForegroundColor White
  exit 1
}
Write-Host "  ✅ Mailbox exists: $($mailbox.DisplayName)" -ForegroundColor Green
Write-Host "     Type: $($mailbox.RecipientTypeDetails)" -ForegroundColor Gray
Write-Host "     Primary SMTP: $($mailbox.PrimarySmtpAddress)" -ForegroundColor Gray
Write-Host ""

# Step 2: Check mailbox type
Write-Host "Step 2/7: Verifying mailbox type..." -ForegroundColor Yellow
if ($mailbox.RecipientTypeDetails -ne "SharedMailbox") {
  Write-Host "  ⚠️  WARNING: Mailbox is NOT a shared mailbox (Type: $($mailbox.RecipientTypeDetails))" -ForegroundColor Yellow
  Write-Host "  💡 Shared mailboxes are preferred for team email addresses" -ForegroundColor Yellow
} else {
  Write-Host "  ✅ Mailbox is a Shared Mailbox" -ForegroundColor Green
}
Write-Host ""

# Step 3: Check email addresses
Write-Host "Step 3/7: Checking email addresses..." -ForegroundColor Yellow
$emailAddresses = $mailbox.EmailAddresses
Write-Host "  Email Addresses:" -ForegroundColor Gray
foreach ($addr in $emailAddresses) {
  if ($addr -like "SMTP:*") {
    Write-Host "    ✅ Primary: $($addr -replace 'SMTP:','')" -ForegroundColor Green
  } elseif ($addr -like "smtp:*") {
    Write-Host "    📧 Alias: $($addr -replace 'smtp:','')" -ForegroundColor Cyan
  }
}
Write-Host ""

# Step 4: Check if mailbox is enabled for email
Write-Host "Step 4/7: Checking email delivery settings..." -ForegroundColor Yellow
$deliveryRestriction = Get-Mailbox -Identity $MailboxAddress | Select-Object -ExpandProperty AcceptMessagesOnlyFrom
$deliveryRestrictionDL = Get-Mailbox -Identity $MailboxAddress | Select-Object -ExpandProperty AcceptMessagesOnlyFromDLMembers
$rejectMessagesFrom = Get-Mailbox -Identity $MailboxAddress | Select-Object -ExpandProperty RejectMessagesFrom

if ($deliveryRestriction -or $deliveryRestrictionDL) {
  Write-Host "  ⚠️  WARNING: Mailbox has delivery restrictions!" -ForegroundColor Yellow
  Write-Host "     AcceptMessagesOnlyFrom: $deliveryRestriction" -ForegroundColor Gray
  Write-Host "     AcceptMessagesOnlyFromDLMembers: $deliveryRestrictionDL" -ForegroundColor Gray
  Write-Host "  💡 This may be blocking incoming emails" -ForegroundColor Yellow
} else {
  Write-Host "  ✅ No delivery restrictions (mailbox accepts from everyone)" -ForegroundColor Green
}

if ($rejectMessagesFrom) {
  Write-Host "  ⚠️  WARNING: Mailbox rejects messages from: $rejectMessagesFrom" -ForegroundColor Yellow
} else {
  Write-Host "  ✅ No rejection rules" -ForegroundColor Green
}
Write-Host ""

# Step 5: Check forwarding/redirect
Write-Host "Step 5/7: Checking forwarding/redirect settings..." -ForegroundColor Yellow
$forwarding = Get-Mailbox -Identity $MailboxAddress | Select-Object -ExpandProperty ForwardingAddress
$forwardingSMTP = Get-Mailbox -Identity $MailboxAddress | Select-Object -ExpandProperty ForwardingSmtpAddress
$deliverToMailboxAndForward = Get-Mailbox -Identity $MailboxAddress | Select-Object -ExpandProperty DeliverToMailboxAndForward

if ($forwarding -or $forwardingSMTP) {
  Write-Host "  ⚠️  WARNING: Mailbox has forwarding configured!" -ForegroundColor Yellow
  Write-Host "     ForwardingAddress: $forwarding" -ForegroundColor Gray
  Write-Host "     ForwardingSmtpAddress: $forwardingSMTP" -ForegroundColor Gray
  Write-Host "     DeliverToMailboxAndForward: $deliverToMailboxAndForward" -ForegroundColor Gray
  if (-not $deliverToMailboxAndForward) {
    Write-Host "  ⚠️  Emails are being forwarded ONLY (not delivered to mailbox)" -ForegroundColor Red
    Write-Host "  💡 Set DeliverToMailboxAndForward to true to keep copies in mailbox" -ForegroundColor Yellow
  }
} else {
  Write-Host "  ✅ No forwarding configured (emails stay in mailbox)" -ForegroundColor Green
}
Write-Host ""

# Step 6: Check permissions
Write-Host "Step 6/7: Checking mailbox permissions..." -ForegroundColor Yellow
$permissions = Get-MailboxPermission -Identity $MailboxAddress | Where-Object { $_.User -notlike "NT AUTHORITY\*" -and $_.User -notlike "S-1-*" }
if ($permissions) {
  Write-Host "  Users with access:" -ForegroundColor Gray
  foreach ($perm in $permissions) {
    Write-Host "    - $($perm.User): $($perm.AccessRights)" -ForegroundColor Cyan
  }
} else {
  Write-Host "  ⚠️  No explicit user permissions found" -ForegroundColor Yellow
  Write-Host "  💡 Add permissions so users can access the mailbox" -ForegroundColor Yellow
}
Write-Host ""

# Step 7: Check domain and mail flow
Write-Host "Step 7/7: Checking domain configuration..." -ForegroundColor Yellow
$domain = ($MailboxAddress -split '@')[1]
$acceptedDomain = Get-AcceptedDomain | Where-Object { $_.Name -eq $domain }
if ($acceptedDomain) {
  Write-Host "  ✅ Domain '$domain' is accepted in Exchange" -ForegroundColor Green
  Write-Host "     Domain Type: $($acceptedDomain.DomainType)" -ForegroundColor Gray
} else {
  Write-Host "  ❌ Domain '$domain' is NOT accepted in Exchange!" -ForegroundColor Red
  Write-Host "  💡 This will prevent email delivery" -ForegroundColor Yellow
  Write-Host "  💡 Add domain with: New-AcceptedDomain -Name '$domain' -DomainType 'Authoritative'" -ForegroundColor Cyan
}
Write-Host ""

# Summary
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "📋 DIAGNOSIS SUMMARY" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

$issues = @()
if (-not $mailbox) { $issues += "Mailbox does not exist" }
if ($mailbox.RecipientTypeDetails -ne "SharedMailbox") { $issues += "Mailbox is not a shared mailbox" }
if ($deliveryRestriction -or $deliveryRestrictionDL) { $issues += "Delivery restrictions may block emails" }
if ($forwarding -and -not $deliverToMailboxAndForward) { $issues += "Emails forwarded only (not delivered to mailbox)" }
if (-not $acceptedDomain) { $issues += "Domain not accepted in Exchange" }

if ($issues.Count -eq 0) {
  Write-Host "✅ No issues found! Mailbox should receive emails." -ForegroundColor Green
  Write-Host ""
  Write-Host "If emails still aren't arriving, check:" -ForegroundColor Yellow
  Write-Host "  - Mail flow rules (Get-TransportRule)" -ForegroundColor Gray
  Write-Host "  - Spam filter settings" -ForegroundColor Gray
  Write-Host "  - External sender restrictions" -ForegroundColor Gray
  Write-Host "  - Mailbox storage quota (Get-MailboxStatistics)" -ForegroundColor Gray
} else {
  Write-Host "⚠️  Issues found:" -ForegroundColor Yellow
  foreach ($issue in $issues) {
    Write-Host "  - $issue" -ForegroundColor Red
  }
  Write-Host ""
  Write-Host "💡 Run the suggested commands above to fix these issues" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "📧 To test email delivery:" -ForegroundColor Cyan
Write-Host "  Send-MailMessage -To '$MailboxAddress' -From 'test@$domain' -Subject 'Test' -Body 'Test message' -SmtpServer 'smtp.office365.com'" -ForegroundColor White
Write-Host ""
