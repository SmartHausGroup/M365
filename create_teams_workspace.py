#!/usr/bin/env python3
"""
Create Teams workspace for Advisory Services using Microsoft Graph API
"""

import requests
import json
import os

# Configuration
TENANT_ID = os.getenv("AZURE_TENANT_ID", "6c4cb441-342c-430f-9a9d-79c3cdb18b75")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "e6fd71d3-4116-401e-a4f1-b2fda4318a8b")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")

def get_access_token():
    """Get access token from Azure AD"""
    if not CLIENT_SECRET:
        raise RuntimeError("AZURE_CLIENT_SECRET must be set in the environment")

    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    
    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': 'https://graph.microsoft.com/.default'
    }
    
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"Error getting token: {response.status_code} - {response.text}")
        return None

def create_teams_workspace(access_token):
    """Create Teams workspace"""
    graph_url = "https://graph.microsoft.com/v1.0/teams"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Teams workspace data
    team_data = {
        "displayName": "SmartHaus Advisory Services",
        "description": "Enterprise AI Governance and Advisory Services Team",
        "mailNickname": "advisory-services",
        "template@odata.bind": "https://graph.microsoft.com/v1.0/teamsTemplates('standard')",
        "visibility": "Private"
    }
    
    response = requests.post(graph_url, headers=headers, json=team_data)
    
    if response.status_code == 202:  # Accepted for async processing
        print("✅ Teams workspace creation initiated successfully!")
        print("📋 Location header:", response.headers.get('Location', 'Not provided'))
        return True
    elif response.status_code == 201:  # Created immediately
        print("✅ Teams workspace created successfully!")
        print("📋 Team ID:", response.json().get('id', 'Not provided'))
        return True
    else:
        print(f"❌ Error creating Teams workspace: {response.status_code}")
        print(f"📋 Response: {response.text}")
        return False

def main():
    print("🚀 Creating SmartHaus Advisory Services Teams Workspace...")
    print("=" * 60)
    
    # Get access token
    print("🔑 Getting access token...")
    access_token = get_access_token()
    if not access_token:
        print("❌ Failed to get access token")
        return
    
    print("✅ Access token obtained")
    
    # Create Teams workspace
    print("🏗️ Creating Teams workspace...")
    success = create_teams_workspace(access_token)
    
    if success:
        print("\n🎉 Teams workspace creation completed!")
        print("📱 Check Microsoft Teams for the new workspace")
    else:
        print("\n❌ Teams workspace creation failed")

if __name__ == "__main__":
    main()
