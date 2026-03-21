param(
  [string]$OwnerUpn = "phil@smarthausgroup.com"
)

$departments = @(
  @{ DisplayName="Operations Hub";           MailNickname="operations" }
  @{ DisplayName="HR Hub";                   MailNickname="hr" }
  @{ DisplayName="Communication Hub";        MailNickname="communication" }
  @{ DisplayName="Engineering Hub";          MailNickname="engineering" }
  @{ DisplayName="Marketing Hub";            MailNickname="marketing" }
  @{ DisplayName="Product Hub";              MailNickname="product" }
  @{ DisplayName="Project Management Hub";   MailNickname="project-management" }
  @{ DisplayName="Studio Operations Hub";    MailNickname="studio-operations" }
  @{ DisplayName="Testing Hub";              MailNickname="testing" }
  @{ DisplayName="Design Hub";               MailNickname="design" }
)

function Resolve-GroupId {
  param($MailNickname, $DisplayName)
  $g = Get-MgGroup -Filter "mailNickname eq '$MailNickname'" -ConsistencyLevel eventual -All
  if (-not $g) {
    $g = Get-MgGroup -Filter "displayName eq '$DisplayName'" -ConsistencyLevel eventual -All
  }
  if (-not $g) { throw "Group not found: $DisplayName ($MailNickname)" }
  return $g[0].Id
}

function Ensure-GroupOwner {
  param($GroupId, $OwnerUpn)
  $owner = Get-MgUser -UserId $OwnerUpn -ErrorAction Stop
  $owners = Get-MgGroupOwner -GroupId $GroupId -All -ErrorAction SilentlyContinue
  if ($owners -and ($owners | Where-Object { $_.Id -eq $owner.Id })) {
    return
  }
  # Add owner reference
  $ref = @{ '@odata.id' = "https://graph.microsoft.com/v1.0/users/$($owner.Id)" }
  New-MgGroupOwnerByRef -GroupId $GroupId -BodyParameter $ref -ErrorAction Stop | Out-Null
}

foreach ($d in $departments) {
  try {
    $gid = Resolve-GroupId -MailNickname $d.MailNickname -DisplayName $d.DisplayName
    $existing = Get-Team -GroupId $gid -ErrorAction SilentlyContinue
    if ($existing) {
      Write-Host "✔ Team exists: $($d.DisplayName)"
      continue
    }

    Write-Host "⏳ Ensuring owner for group $($d.DisplayName) ..."
    Ensure-GroupOwner -GroupId $gid -OwnerUpn $OwnerUpn

    Write-Host "⏳ Creating Team for '$($d.DisplayName)' (GroupId: $gid)..."
    New-Team -GroupId $gid -DisplayName $d.DisplayName | Out-Null
    Start-Sleep -Seconds 15
    Write-Host "✅ Team created: $($d.DisplayName)"
  } catch {
    Write-Warning "Failed for '$($d.DisplayName)': $($_.Exception.Message)"
  }
}

Write-Host "Done. Re-run the Python bootstrap to add channels and finish setup."
