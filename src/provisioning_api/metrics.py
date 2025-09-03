from __future__ import annotations

import threading
import time
from dataclasses import dataclass


@dataclass
class Counters:
    total_requests: int = 0
    sites_created: int = 0
    teams_created: int = 0


_counters = Counters()
_lock = threading.Lock()
_start_time = time.time()


def inc_requests() -> None:
    with _lock:
        _counters.total_requests += 1


def inc_sites_created(n: int = 1) -> None:
    with _lock:
        _counters.sites_created += n


def inc_teams_created(n: int = 1) -> None:
    with _lock:
        _counters.teams_created += n


def snapshot() -> dict:
    with _lock:
        return {
            "total_requests": _counters.total_requests,
            "sites_created": _counters.sites_created,
            "teams_created": _counters.teams_created,
            "uptime_seconds": int(time.time() - _start_time),
            "started_at": _start_time,
        }
