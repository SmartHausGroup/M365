param(
  [Parameter(Mandatory=$true)] [string]$AppId,
  [Parameter(Mandatory=$true)] [string]$Organization, # e.g. smarthaus.onmicrosoft.com
  [Parameter(Mandatory=$true)] [string]$CertificateThumbprint
)

Import-Module ExchangeOnlineManagement -ErrorAction Stop
Connect-ExchangeOnline -AppId $AppId -CertificateThumbprint $CertificateThumbprint -Organization $Organization


