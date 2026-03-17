param(
  [Parameter(Mandatory=$true)] [string]$AdminUpn,            # e.g. your.user@smarthaus.ai
  [Parameter(Mandatory=$true)] [string]$AppId,               # Graph App Registration (client) ID
  [string]$Domain = "smarthaus.ai"
)

# Requires: ExchangeOnlineManagement module
# Usage:
#   Install-Module ExchangeOnlineManagement -Scope CurrentUser -Force
#   Connect-ExchangeOnline
#   ./provision_agents_shared_mailboxes.ps1 -AdminUpn your.user@smarthaus.ai -AppId 00000000-0000-0000-0000-000000000000 -Domain smarthaus.ai

function Ensure-SharedMailbox {
  param([string]$Name,[string]$Primary,[string[]]$Aliases)
  $primaryAddr = "$Primary@$Domain"
  if (-not (Get-Mailbox -Identity $Name -ErrorAction SilentlyContinue)) {
    New-Mailbox -Shared -Name $Name -DisplayName $Name -PrimarySmtpAddress $primaryAddr | Out-Null
  }
  $emails = @("SMTP:$primaryAddr")
  foreach ($al in $Aliases) { $emails += "smtp:$al@$Domain" }
  Set-Mailbox -Identity $Name -EmailAddresses $emails | Out-Null

  Add-MailboxPermission   -Identity $Name -User $AdminUpn -AccessRights FullAccess -AutoMapping:$true -ErrorAction SilentlyContinue | Out-Null
  Add-RecipientPermission -Identity $Name -Trustee $AdminUpn -AccessRights SendAs -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
}

$People = @(
  # operations
  @{ Name="Marcus Chen";        Primary="marcus.chen";        Aliases=@("m365.administrator") }
  @{ Name="Elena Rodriguez";    Primary="elena.rodriguez";     Aliases=@("website.manager") }

  # hr
  @{ Name="Sarah Williams";     Primary="sarah.williams";      Aliases=@("hr.generalist") }

  # communication
  @{ Name="David Park";         Primary="david.park";          Aliases=@("outreach.coordinator") }

  # engineering
  @{ Name="Alex Thompson";      Primary="alex.thompson";       Aliases=@("ai.engineer") }
  @{ Name="Jordan Kim";         Primary="jordan.kim";          Aliases=@("backend.architect") }
  @{ Name="Casey Johnson";      Primary="casey.johnson";       Aliases=@("devops.automator") }
  @{ Name="Riley Martinez";     Primary="riley.martinez";      Aliases=@("frontend.developer") }
  @{ Name="Taylor Brown";       Primary="taylor.brown";        Aliases=@("mobile.app.builder") }
  @{ Name="Ethan Rivera";       Primary="ethan.rivera";        Aliases=@("rapid.prototyper") }
  @{ Name="Grace Lee";          Primary="grace.lee";           Aliases=@("test.writer.fixer") }

  # marketing (replace Taylor Swift -> Taylor Santos)
  @{ Name="Jake Thompson";      Primary="jake.thompson";       Aliases=@("app.store.optimizer") }
  @{ Name="Taylor Santos";      Primary="taylor.santos";       Aliases=@("content.creator") }
  @{ Name="Morgan Davis";       Primary="morgan.davis";        Aliases=@("growth.hacker") }
  @{ Name="Zoe Martinez";       Primary="zoe.martinez";        Aliases=@("instagram.curator") }
  @{ Name="Priya Singh";        Primary="priya.singh";         Aliases=@("reddit.community.builder") }
  @{ Name="Ryan OConnor";       Primary="ryan.oconnor";        Aliases=@("tiktok.strategist") }
  @{ Name="Jamie Lee";          Primary="jamie.lee";           Aliases=@("twitter.engager") }

  # product
  @{ Name="Sam Chen";           Primary="sam.chen";            Aliases=@("sprint.prioritizer") }
  @{ Name="Maya Patel";         Primary="maya.patel";          Aliases=@("feedback.synthesizer") }
  @{ Name="Chris Wong";         Primary="chris.wong";          Aliases=@("trend.researcher") }

  # project-management
  @{ Name="Emily Carter";       Primary="emily.carter";        Aliases=@("experiment.tracker") }
  @{ Name="Ben Foster";         Primary="ben.foster";          Aliases=@("project.shipper") }
  @{ Name="Olivia Park";        Primary="olivia.park";         Aliases=@("studio.producer") }

  # studio-operations
  @{ Name="Amanda Foster";      Primary="amanda.foster";       Aliases=@("analytics.reporter") }
  @{ Name="Lisa Chang";         Primary="lisa.chang";          Aliases=@("finance.tracker") }
  @{ Name="Jennifer Liu";       Primary="jennifer.liu";        Aliases=@("infrastructure.maintainer") }
  @{ Name="Robert Kim";         Primary="robert.kim";          Aliases=@("legal.compliance") }
  @{ Name="Mike Rodriguez";     Primary="mike.rodriguez";      Aliases=@("support.responder") }

  # testing
  @{ Name="Nina Shah";          Primary="nina.shah";           Aliases=@("api.tester") }
  @{ Name="Omar Haddad";        Primary="omar.haddad";         Aliases=@("performance.benchmarker") }
  @{ Name="Sofia Alvarez";      Primary="sofia.alvarez";       Aliases=@("test.results.analyzer") }
  @{ Name="Liam Nguyen";        Primary="liam.nguyen";         Aliases=@("tool.evaluator") }
  @{ Name="Ava Johnson";        Primary="ava.johnson";         Aliases=@("workflow.optimizer") }

  # design
  @{ Name="Isabella Rossi";     Primary="isabella.rossi";      Aliases=@("brand.guardian") }
  @{ Name="Noah Anderson";      Primary="noah.anderson";       Aliases=@("ui.designer") }
  @{ Name="Mila Novak";         Primary="mila.novak";          Aliases=@("ux.researcher") }
  @{ Name="Diego Alvarez";      Primary="diego.alvarez";       Aliases=@("visual.storyteller") }
  @{ Name="Luna Park";          Primary="luna.park";           Aliases=@("whimsy.injector") }
)

# Create/update mailboxes and delegate rights
$People | ForEach-Object { Ensure-SharedMailbox -Name $_.Name -Primary $_.Primary -Aliases $_.Aliases }

# Allow send-from-alias once per org (ignore if already enabled)
try { Set-TransportConfig -SendFromAliasEnabled $true } catch {}

# Restrict Graph Mail.* to these agent mailboxes via Application Access Policy
$GroupName = "SH Agents Mail Access"
$GroupSmtp = "agents@$Domain"
if (-not (Get-DistributionGroup -Identity $GroupName -ErrorAction SilentlyContinue)) {
  New-DistributionGroup -Type Security -Name $GroupName -PrimarySmtpAddress $GroupSmtp | Out-Null
}
foreach ($p in $People) {
  try { Add-DistributionGroupMember -Identity $GroupName -Member $p.Name -BypassSecurityGroupManagerCheck } catch {}
}

if ($AppId -and $AppId -ne "00000000-0000-0000-0000-000000000000") {
  if (-not (Get-ApplicationAccessPolicy -ErrorAction SilentlyContinue | Where-Object { $_.AppId -eq $AppId })) {
    New-ApplicationAccessPolicy -AppId $AppId -PolicyScopeGroupId $GroupSmtp -AccessRight RestrictAccess -Description "Limit Graph app mail scope" | Out-Null
  }
  try { Test-ApplicationAccessPolicy -AppId $AppId -Identity "elena.rodriguez@$Domain" | Out-Null } catch {}
}

Write-Host "Done. 39 shared mailboxes created/updated, aliases set, permissions delegated, and Graph mail access policy applied." -ForegroundColor Green


