Param(
  [Parameter(Mandatory=$true)][string]$UserPrincipalName
)

$adapterUrl = $env:OPS_ADAPTER_URL
if (-not $adapterUrl) { $adapterUrl = "http://localhost:8080" }

$body = @{ params = @{ userPrincipalName = $UserPrincipalName } } | ConvertTo-Json

# Offboarding requires approval per policy
$resp = Invoke-RestMethod -Method Post -Uri "$adapterUrl/actions/hr-generalist/employee.offboard" -ContentType 'application/json' -Body $body
$resp | ConvertTo-Json -Depth 5

