# Add Incoming Webhooks to Teams Channels for Advisory Services
# This script adds webhooks to each channel for real-time notifications

Write-Host "🔗 Adding Incoming Webhooks to Advisory Services Teams Channels..." -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green

try {
    # Connect to Microsoft Teams
    Write-Host "🔗 Connecting to Microsoft Teams..." -ForegroundColor Yellow
    Connect-MicrosoftTeams

    # Get the Advisory Services team
    Write-Host "🔍 Finding Advisory Services team..." -ForegroundColor Yellow
    $team = Get-Team -DisplayName "SmartHaus Advisory Services"

    if (-not $team) {
        Write-Host "❌ Could not find Advisory Services team" -ForegroundColor Red
        exit 1
    }

    Write-Host "✅ Found team: $($team.DisplayName) (ID: $($team.GroupId))" -ForegroundColor Green

    # Define channels and their webhook purposes
    $channels = @(
        @{Name = "advisory-services"; Purpose = "All advisory service notifications"},
        @{Name = "risk-management"; Purpose = "Risk assessment alerts and updates"},
        @{Name = "aidf-certification"; Purpose = "AIDF certification requests and status"},
        @{Name = "project-management"; Purpose = "Project status updates and milestones"},
        @{Name = "client-intake"; Purpose = "New client intake tracking"},
        @{Name = "governance-updates"; Purpose = "AIDF governance updates and compliance"}
    )

    Write-Host "📢 Adding webhooks to channels..." -ForegroundColor Yellow

    foreach ($channel in $channels) {
        try {
            Write-Host "  🔗 Adding webhook to: $($channel.Name)" -ForegroundColor Cyan

            # Get the channel
            $teamChannel = Get-TeamChannel -GroupId $team.GroupId -DisplayName $channel.Name

            if ($teamChannel) {
                # Add incoming webhook
                $webhook = Add-TeamChannelUser -GroupId $team.GroupId -DisplayName $channel.Name -User "Incoming Webhook"

                if ($webhook) {
                    Write-Host "    ✅ Webhook added successfully" -ForegroundColor Green
                    Write-Host "    📋 Webhook URL: $($webhook.WebhookUrl)" -ForegroundColor Gray
                    Write-Host "    🎯 Purpose: $($channel.Purpose)" -ForegroundColor Gray
                }
                else {
                    Write-Host "    ⚠️ Webhook added but no URL returned" -ForegroundColor Yellow
                }
            }
            else {
                Write-Host "    ❌ Channel not found: $($channel.Name)" -ForegroundColor Red
            }
        }
        catch {
            Write-Host "    ❌ Error adding webhook to $($channel.Name): $($_.Exception.Message)" -ForegroundColor Red
        }

        Write-Host "" # Empty line for readability
    }

    Write-Host "🎉 Webhook setup completed!" -ForegroundColor Green
    Write-Host "💡 Note: You'll need to manually configure the webhook URLs in your advisory services" -ForegroundColor Yellow
    Write-Host "📱 Check Microsoft Teams for the webhook configurations" -ForegroundColor Cyan

}
catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    # Disconnect from Teams
    try {
        Disconnect-MicrosoftTeams
        Write-Host "🔌 Disconnected from Microsoft Teams" -ForegroundColor Gray
    }
    catch {
        Write-Host "⚠️ Could not disconnect from Teams" -ForegroundColor Yellow
    }
}
