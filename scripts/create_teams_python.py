#!/usr/bin/env python3
"""
Create Teams from existing M365 Groups using Graph API with app-only authentication.
This script adds the admin user as an owner to each group, then creates Teams.
"""

import os
import sys
import time
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from smarthaus_graph.client import GraphClient

def get_admin_user_id(client, admin_email):
    """Get the user ID for the admin email."""
    try:
        # Use the _request method directly to get user
        r = client._request("GET", f"/users/{admin_email}")
        user = r.json()
        return user.get('id')
    except Exception as e:
        print(f"❌ Failed to get user ID for {admin_email}: {e}")
        return None

def ensure_group_owner(client, group_id, owner_id):
    """Ensure the admin user is an owner of the group."""
    try:
        # Check if user is already an owner
        r = client._request("GET", f"/groups/{group_id}/owners")
        owners = r.json().get('value', [])
        if any(owner.get('id') == owner_id for owner in owners):
            print(f"  ✔ User already owner of group {group_id}")
            return True
        
        # Add user as owner
        ref = {"@odata.id": f"https://graph.microsoft.com/v1.0/users/{owner_id}"}
        client._request("POST", f"/groups/{group_id}/owners/$ref", json=ref)
        print(f"  ✅ Added user as owner of group {group_id}")
        return True
    except Exception as e:
        print(f"  ❌ Failed to add owner to group {group_id}: {e}")
        return False

def create_team_from_group(client, group_id, display_name):
    """Create a Team from an existing M365 Group."""
    try:
        # Check if team already exists
        try:
            team = client.get_team(group_id)
            if team:
                print(f"  ✔ Team already exists for {display_name}")
                return True
        except:
            pass  # Team doesn't exist, continue with creation
        
        # Create team using teamify_group method
        client.teamify_group(group_id)
        print(f"  ✅ Created Team for {display_name}")
        return True
    except Exception as e:
        print(f"  ❌ Failed to create Team for {display_name}: {e}")
        return False

def main():
    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "services.json"
    with open(config_path) as f:
        services = json.load(f)
    
    # Get admin email from environment or use default
    admin_email = os.getenv("ADMIN_EMAIL", "phil@smarthausgroup.com")
    
    # Initialize Graph client
    client = GraphClient()
    
    print(f"🚀 Creating Teams for {len(services)} departments...")
    print(f"👤 Using admin email: {admin_email}")
    
    # Get admin user ID
    admin_user_id = get_admin_user_id(client, admin_email)
    if not admin_user_id:
        print("❌ Could not get admin user ID. Exiting.")
        return 1
    
    print(f"✅ Admin user ID: {admin_user_id}")
    
    success_count = 0
    total_count = len(services)
    
    for service in services:
        display_name = service.get('display_name', '')
        mail_nickname = service.get('mail_nickname', '')
        group_id = service.get('group_id')
        
        if not group_id:
            print(f"⚠️  Skipping {display_name} - no group_id found")
            continue
        
        print(f"\n📋 Processing {display_name} ({mail_nickname})")
        print(f"  Group ID: {group_id}")
        
        # Step 1: Ensure admin is owner
        if not ensure_group_owner(client, group_id, admin_user_id):
            print(f"  ❌ Failed to ensure ownership for {display_name}")
            continue
        
        # Step 2: Create Team
        if create_team_from_group(client, group_id, display_name):
            success_count += 1
            print(f"  ✅ Successfully processed {display_name}")
        else:
            print(f"  ❌ Failed to create Team for {display_name}")
        
        # Small delay between operations
        time.sleep(2)
    
    print(f"\n🎯 Summary: {success_count}/{total_count} Teams created successfully")
    
    if success_count == total_count:
        print("✅ All Teams created! Ready to run bootstrap for channels.")
        return 0
    else:
        print("⚠️  Some Teams failed to create. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
