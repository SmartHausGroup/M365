Param(
  [Parameter(Mandatory=$true)][string]$UserPrincipalName,
  [Parameter(Mandatory=$false)][string]$DisplayName
)

$adapterUrl = $env:OPS_ADAPTER_URL
if (-not $adapterUrl) { $adapterUrl = "http://localhost:8080" }

$body = @{ params = @{ userPrincipalName = $UserPrincipalName; displayName = $DisplayName } } | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "$adapterUrl/actions/hr-generalist/employee.onboard" -ContentType 'application/json' -Body $body

