#!/bin/bash

# Add phil@smarthausgroup.com as owner to all M365 groups
USER_EMAIL="phil@smarthausgroup.com"

# Group IDs from our discovery
declare -A GROUPS=(
    ["Operations Hub"]="4cc86db4-d848-4f73-ada6-fa55f73e84e8"
    ["HR Hub"]="8736ee00-3458-4fea-9e72-4f3e825a7b91"
    ["Communication Hub"]="9da4c2e7-2df1-47ef-a43e-b1b1424bfb12"
    ["Engineering Hub"]="8129fe4a-7058-4654-a20b-2c74a549e607"
    ["Marketing Hub"]="fa4d9a94-357b-46b5-8366-d283c3feaf6a"
    ["Product Hub"]="904075d1-f762-49c3-941c-e5fbe316336e"
    ["Project Management Hub"]="52a93c66-c0ae-4165-8c4e-da801102c5bb"
    ["Studio Operations Hub"]="e3bcc817-485f-40ed-a9d8-451297024be8"
    ["Testing Hub"]="e175108f-e41b-4efe-a4a8-82f5cbf1fe49"
    ["Design Hub"]="2fca9f5a-9e79-40fb-acf1-1c26a26188f8"
)

echo "🚀 Adding $USER_EMAIL as owner to all M365 groups..."

for group_name in "${!GROUPS[@]}"; do
    group_id="${GROUPS[$group_name]}"
    echo ""
    echo "📋 Processing $group_name"
    echo "  Group ID: $group_id"

    # Add user as owner
    if az ad group owner add --group "$group_id" --owner-object-id "$(az ad user show --id "$USER_EMAIL" --query id -o tsv)" 2>/dev/null; then
        echo "  ✅ Added $USER_EMAIL as owner"
    else
        echo "  ⚠️  Failed to add owner (may already be owner or permission issue)"
    fi
done

echo ""
echo "🎯 Done! Now you can run the teamify script."
