import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from smarthaus_graph.client import GraphClient


def main() -> int:
    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "services.json"
    with open(config_path) as f:
        services = json.load(f)

    # Initialize Graph client
    client = GraphClient()

    print("🔍 Finding group IDs for all departments...")

    group_data = []

    for service in services["services"]:
        display_name = service.get("display_name", "")
        mail_nickname = service.get("mail_nickname", "")

        print(f"\n📋 Looking for {display_name} ({mail_nickname})")

        try:
            # Try to find group by mailNickname
            group = client.find_group_by_mailnickname(mail_nickname)
            if group:
                group_id = group.get("id")
                print(f"  ✅ Found group: {group_id}")
                group_data.append(
                    {
                        "display_name": display_name,
                        "mail_nickname": mail_nickname,
                        "group_id": group_id,
                    }
                )
            else:
                print(f"  ❌ Group not found for {mail_nickname}")
        except Exception as e:
            print(f"  ❌ Error finding group: {e}")

    # Save group IDs to a file
    output_file = Path(__file__).parent / "group_ids.json"
    with open(output_file, "w") as f:
        json.dump(group_data, f, indent=2)

    print(f"\n💾 Saved group IDs to {output_file}")
    print(f"📊 Found {len(group_data)} groups")

    return 0


if __name__ == "__main__":
    sys.exit(main())
