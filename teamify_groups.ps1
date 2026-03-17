# Teamify M365 Groups using Graph API
param(
  [string]$OwnerUpn = "phil@smarthausgroup.com"
)

# Group IDs from actual M365 groups
$groups = @(
  @{ DisplayName="Operations Hub";           GroupId="4cc86db4-d848-4f73-ada6-fa55f73e84e8" }
  @{ DisplayName="HR Hub";                   GroupId="8736ee00-3458-4fea-9e72-4f3e825a7b91" }
  @{ DisplayName="Communication Hub";        GroupId="9da4c2e7-2df1-47ef-a43e-b1b1424bfb12" }
  @{ DisplayName="Engineering Hub";          GroupId="8129fe4a-7058-4654-a20b-2c74a549e607" }
  @{ DisplayName="Marketing Hub";            GroupId="fa4d9a94-357b-46b5-8366-d283c3feaf6a" }
  @{ DisplayName="Product Hub";              GroupId="904075d1-f762-49c3-941c-e5fbe316336e" }
  @{ DisplayName="Project Management Hub";   GroupId="52a93c66-c0ae-4165-8c4e-da801102c5bb" }
  @{ DisplayName="Studio Operations Hub";    GroupId="e3bcc817-485f-40ed-a9d8-451297024be8" }
  @{ DisplayName="Testing Hub";              GroupId="e175108f-e41b-4efe-a4a8-82f5cbf1fe49" }
  @{ DisplayName="Design Hub";               GroupId="2fca9f5a-9e79-40fb-acf1-1c26a26188f8" }
)

# Connect to Graph
Connect-MgGraph -Scopes "Group.ReadWrite.All","Team.ReadWrite.All"

foreach ($g in $groups) {
  try {
    # Check if team already exists
    $existing = Get-Team -GroupId $g.GroupId -ErrorAction SilentlyContinue
    if ($existing) { 
      Write-Host "✔ Team exists: $($g.DisplayName)"
      continue 
    }

    Write-Host "⏳ Teamifying group '$($g.DisplayName)' (GroupId: $($g.GroupId))..."
    
    # Teamify the group using Graph API
    $body = @{
      "memberSettings" = @{
        "allowCreatePrivateChannels" = $true
        "allowCreateUpdateChannels" = $true
      }
      "messagingSettings" = @{
        "allowUserEditMessages" = $true
        "allowUserDeleteMessages" = $true
      }
      "funSettings" = @{
        "allowGiphy" = $true
        "giphyContentRating" = "moderate"
      }
    } | ConvertTo-Json -Depth 3

    Invoke-MgGraphRequest -Method PUT -Uri "https://graph.microsoft.com/v1.0/groups/$($g.GroupId)/team" -Body $body -ContentType "application/json"
    
    Start-Sleep -Seconds 15
    Write-Host "✅ Team created: $($g.DisplayName)"
  } catch {
    Write-Warning "Failed for '$($g.DisplayName)': $($_.Exception.Message)"
  }
}

Write-Host "Done. Re-run the Python bootstrap to add channels and finish setup."
