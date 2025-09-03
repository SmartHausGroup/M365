from __future__ import annotations

import builtins
import json
import os
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from smarthaus_common.logging import get_logger

log = get_logger(__name__)


class JsonStore:
    """Very simple JSON list store per collection to avoid external deps.

    Not for production-scale use; serves as a non-blocking persistence layer
    so endpoints can function and be verified locally/CI.
    """

    def __init__(self, root: str | os.PathLike[str] | None = None) -> None:
        base = root if root is not None else os.getenv("APP_DATA", "data")
        self.root = Path(base).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self._locks: dict[str, threading.Lock] = {}

    def _file(self, collection: str) -> Path:
        return self.root / f"{collection}.json"

    def _lock(self, collection: str) -> threading.Lock:
        if collection not in self._locks:
            self._locks[collection] = threading.Lock()
        return self._locks[collection]

    def append(self, collection: str, item: dict[str, Any]) -> dict[str, Any]:
        record = {
            "id": str(uuid.uuid4()),
            "ts": int(time.time()),
            **item,
        }
        path = self._file(collection)
        with self._lock(collection):
            if path.exists():
                try:
                    data = json.loads(path.read_text())
                    if not isinstance(data, list):
                        data = []
                except Exception:
                    data = []
            else:
                data = []
            data.append(record)
            path.write_text(json.dumps(data, indent=2))
        log.debug("Appended to %s: %s", collection, record["id"])
        return record

    def list(self, collection: str) -> builtins.list[dict[str, Any]]:
        path = self._file(collection)
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text())
            if isinstance(data, list):
                return data
            return []
        except Exception:
            return []

    def search(
        self, collection: str, q: str = "", tags: builtins.list[str] | None = None
    ) -> builtins.list[dict[str, Any]]:
        q = (q or "").strip().lower()
        tags = [t.strip().lower() for t in (tags or []) if t.strip()]
        rows = self.list(collection)

        def matches(row: dict[str, Any]) -> bool:
            # Text search across common string fields
            if q:
                hay = []
                for _k, v in row.items():
                    if isinstance(v, str):
                        hay.append(v.lower())
                if hay and not any(q in s for s in hay):
                    return False
            if tags:
                row_tags = []
                v = row.get("tags")
                if isinstance(v, list):
                    row_tags = [str(x).lower() for x in v]
                if not any(t in row_tags for t in tags):
                    return False
            return True

        return [r for r in rows if matches(r)]
