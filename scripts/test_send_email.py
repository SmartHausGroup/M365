import asyncio
import os
import sys
from pathlib import Path


def load_env(path: str = ".env.local") -> None:
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        v = v.strip().strip('"').strip("'")
        os.environ[k.strip()] = v


async def main():
    from src.ops_adapter.actions import outreach_email_send_individual
    sender = os.getenv("OUTREACH_SENDER") or "phil@smarthausgroup.com"
    params = {
        "from": sender,
        "to": "phil@smarthausgroup.com",
        "subject": "Test: Outreach email sendMail wiring",
        "html": "<b>Hello Phil</b> — automated test",
        "saveToSent": True,
    }
    res = await outreach_email_send_individual(params, "codex-check-1")
    print(res)


if __name__ == "__main__":
    # Ensure project root on sys.path
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    load_env()
    asyncio.run(main())
