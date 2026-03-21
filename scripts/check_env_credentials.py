#!/usr/bin/env python3
"""Test .env credentials; return list of keys that failed (so caller can clear values)."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any

# Load .env
ENV_PATH = os.path.join(os.path.dirname(__file__), "..", ".env")
if not os.path.exists(ENV_PATH):
    ENV_PATH = ".env"

env: dict[str, str] = {}
with open(ENV_PATH) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        if k and " " not in k:
            env[k] = v.strip()


def req(
    url: str,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    data: dict[str, Any] | bytes | None = None,
    timeout: int = 10,
) -> tuple[int | None, bytes | str]:
    request_headers = headers or {}
    payload: bytes | None
    if isinstance(data, dict):
        payload = json.dumps(data).encode() if method == "POST" else None
    else:
        payload = data
    request_obj = urllib.request.Request(url, data=payload, headers=request_headers, method=method)
    if payload:
        request_obj.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request_obj, timeout=timeout) as response:
            return response.getcode(), response.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        return None, str(e)


def test_openai() -> bool | None:
    k = os.environ.get("OPENAI_API_KEY") or env.get("OPENAI_API_KEY")
    if not k:
        return None
    code, _ = req("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {k}"})
    return code == 200


def test_anthropic() -> bool | None:
    k = os.environ.get("ANTHROPIC_API_KEY") or env.get("ANTHROPIC_API_KEY")
    if not k:
        return None
    code, _ = req(
        "https://api.anthropic.com/v1/messages",
        method="POST",
        headers={
            "x-api-key": k,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        data={
            "model": "claude-3-haiku-20240307",
            "max_tokens": 1,
            "messages": [{"role": "user", "content": "x"}],
        },
    )
    return code in (200, 400)  # 400 = auth ok, bad request


def test_perplexity() -> bool | None:
    k = os.environ.get("PERPLEXITY_API_KEY") or env.get("PERPLEXITY_API_KEY")
    if not k:
        return None
    code, _ = req(
        "https://api.perplexity.ai/chat/completions",
        method="POST",
        headers={"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
        data={
            "model": "llama-3.1-sonar-small-128k-online",
            "max_tokens": 1,
            "messages": [{"role": "user", "content": "hi"}],
        },
    )
    return code in (200, 400, 422)


def test_cohere() -> bool | None:
    k = os.environ.get("COHERE_API_KEY") or env.get("COHERE_API_KEY")
    if not k:
        return None
    code, _ = req(
        "https://api.cohere.ai/v1/tokenize",
        method="POST",
        headers={"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
        data={"model": "command", "text": "x"},
    )
    return code in (200, 400, 401)


def test_hubspot() -> bool | None:
    k = os.environ.get("HUBSPOT_ACCESS_TOKEN") or env.get("HUBSPOT_ACCESS_TOKEN")
    if not k:
        return None
    code, _ = req("https://api.hubapi.com/account-info", headers={"Authorization": f"Bearer {k}"})
    return code == 200


def test_vercel() -> bool | None:
    k = os.environ.get("VERCEL_TOKEN") or env.get("VERCEL_TOKEN")
    if not k:
        return None
    code, _ = req("https://api.vercel.com/v2/user", headers={"Authorization": f"Bearer {k}"})
    return code == 200


def test_github() -> bool | None:
    k = os.environ.get("GH_TOKEN") or env.get("GH_TOKEN")
    if not k:
        return None
    code, _ = req(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {k}", "Accept": "application/vnd.github.v3+json"},
    )
    return code == 200


def test_huggingface() -> bool | None:
    k = os.environ.get("HUGGINGFACE_TOKEN") or env.get("HUGGINGFACE_TOKEN")
    if not k:
        return None
    code, _ = req("https://huggingface.co/api/whoami-v2", headers={"Authorization": f"Bearer {k}"})
    return code == 200


def test_pinecone() -> bool | None:
    k = os.environ.get("PINECONE_API_KEY") or env.get("PINECONE_API_KEY")
    host = (os.environ.get("PINECONE_HOST") or env.get("PINECONE_HOST") or "").replace(
        "https://", ""
    )
    if not k or not host:
        return None
    code, _ = req(
        f"https://{host}/describe_index_stats",
        method="POST",
        headers={"Api-Key": k, "Content-Type": "application/json"},
        data={},
    )
    return code in (200, 400, 404)


def test_weaviate() -> bool | None:
    url = (
        os.environ.get("WEAVIATE_REST_ENDPOINT") or env.get("WEAVIATE_REST_ENDPOINT") or ""
    ).rstrip("/")
    k = os.environ.get("WEAVIATE_API_KEY") or env.get("WEAVIATE_API_KEY")
    if not url:
        return None
    code, _ = req(
        f"{url}/v1/.well-known/ready", headers={"Authorization": f"Bearer {k}"} if k else {}
    )
    return code == 200


def test_tavily() -> bool | None:
    k = os.environ.get("TAVILY_API_KEY") or env.get("TAVILY_API_KEY")
    if not k:
        return None
    code, _ = req(
        "https://api.tavily.com/search",
        method="POST",
        headers={"Content-Type": "application/json"},
        data={"api_key": k, "query": "test", "search_depth": "basic", "max_results": 1},
    )
    return code in (200, 400)


def test_crunchbase() -> bool | None:
    k = os.environ.get("CRUNCHBASE_API_KEY") or env.get("CRUNCHBASE_API_KEY")
    if not k:
        return None
    code, _ = req("https://api.crunchbase.com/api/v4/entities/organizations?user_key=" + k)
    return code == 200


def test_langchain(key: str = "LANGCHAIN_API_KEY") -> bool | None:
    k = os.environ.get(key) or env.get(key)
    if not k:
        return None
    code, _ = req("https://api.smith.langchain.com/api/v1/sessions", headers={"x-api-key": k})
    return code in (200, 401, 403)


def test_mongodb() -> bool | None:
    uri = os.environ.get("MONGODB_URI") or env.get("MONGODB_URI")
    if not uri or not uri.startswith("mongodb"):
        return None
    try:
        from pymongo import MongoClient

        c = MongoClient(uri, serverSelectionTimeoutMS=5000)
        c.admin.command("ping")
        return True
    except Exception:
        return False


def test_sentry_dsn() -> bool | None:
    dsn = os.environ.get("SENTRY_DSN") or env.get("SENTRY_DSN")
    if not dsn:
        return None
    # DSN format: https://key@host/project
    m = re.match(r"https://[^@]+@[^/]+/\d+", dsn)
    return bool(m)


# Keys we test and the function to run (function returns True=ok, False=fail, None=skip)
CredentialCheck = Callable[[], bool | None]

TESTS: list[tuple[str, CredentialCheck]] = [
    ("OPENAI_API_KEY", lambda: test_openai()),
    ("ANTHROPIC_API_KEY", lambda: test_anthropic()),
    ("PERPLEXITY_API_KEY", lambda: test_perplexity()),
    ("COHERE_API_KEY", lambda: test_cohere()),
    ("HUBSPOT_ACCESS_TOKEN", lambda: test_hubspot()),
    ("VERCEL_TOKEN", lambda: test_vercel()),
    ("GH_TOKEN", lambda: test_github()),
    ("HUGGINGFACE_TOKEN", lambda: test_huggingface()),
    ("PINECONE_API_KEY", lambda: test_pinecone()),
    ("WEAVIATE_API_KEY", lambda: test_weaviate()),
    ("TAVILY_API_KEY", lambda: test_tavily()),
    ("CRUNCHBASE_API_KEY", lambda: test_crunchbase()),
    ("LANGCHAIN_API_KEY", lambda: test_langchain("LANGCHAIN_API_KEY")),
    ("LANGCHAIN_TAI_API_KEY", lambda: test_langchain("LANGCHAIN_TAI_API_KEY")),
    ("MONGODB_URI", lambda: test_mongodb()),
    ("SENTRY_DSN", lambda: test_sentry_dsn()),
]


def main() -> int:
    base = os.path.dirname(os.path.abspath(ENV_PATH))
    if base:
        os.chdir(base)
    for k, v in env.items():
        os.environ.setdefault(k, v)

    failed: list[str] = []
    for key, fn in TESTS:
        try:
            r = fn()
        except Exception:
            r = False
        if r is False:
            failed.append(key)
        elif r is True:
            print(f"OK {key}", file=sys.stderr)
        # None = skip

    # Output only failed keys, one per line (for scripting)
    for k in failed:
        print(k)

    return 0


if __name__ == "__main__":
    sys.exit(main())
