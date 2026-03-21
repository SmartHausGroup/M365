from smarthaus_graph.client import GraphClient

if __name__ == "__main__":
    try:
        client = GraphClient()
        data = client.get_organization()
        ok = bool(data.get("value"))
        print("m365_connectivity:", "ok" if ok else "unknown")
    except Exception:
        print("m365_connectivity:", "not_configured_or_unreachable")
