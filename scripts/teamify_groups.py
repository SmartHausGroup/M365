import json
import sys
import time
from pathlib import Path
from typing import Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from smarthaus_graph.client import GraphClient


def main() -> int:
    # Load group IDs
    group_ids_file = Path(__file__).parent / "group_ids.json"
    with group_ids_file.open(encoding="utf-8") as f:
        groups: list[dict[str, Any]] = json.load(f)

    # Initialize Graph client
    client = GraphClient()

    print("🚀 Teamifying M365 Groups...")

    success_count = 0
    total_count = len(groups)

    for group in groups:
        display_name = group["display_name"]
        group_id = group["group_id"]

        print(f"\n📋 Processing {display_name}")
        print(f"  Group ID: {group_id}")

        try:
            # Check if team already exists
            try:
                team = client.get_team(group_id)
                if team:
                    print(f"  ✔ Team already exists for {display_name}")
                    success_count += 1
                    continue
            except Exception:
                pass  # Team doesn't exist, continue with creation

            # Teamify the group
            print("  ⏳ Teamifying group...")
            client.teamify_group(group_id)

            # Wait a bit for the team to be ready
            time.sleep(5)

            print(f"  ✅ Team created for {display_name}")
            success_count += 1

        except Exception as e:
            print(f"  ❌ Failed to teamify {display_name}: {e}")

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
