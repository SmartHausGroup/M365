import json

from provisioning_api.main import detailed_status

if __name__ == "__main__":
    # Env should be set via process environment
    data = detailed_status()
    print(json.dumps(data, indent=2))
