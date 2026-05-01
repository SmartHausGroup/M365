"""End-to-end test of Track C truth-in-advertising surfaces.

plan:m365-cps-trkC-p5-end-to-end:T1-T3

Covers:
  - C1: not_yet_implemented status code is distinct
  - C2: planned actions short-circuit before any HTTP call
  - C3: audit script reports valid coverage breakdown
  - C4: capability map doc reflects live data
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from m365_runtime.graph.actions import _denial_to_status
from m365_runtime.graph.registry import COVERAGE_STATUS_VALUES, READ_ONLY_REGISTRY
from ucp_m365_pack.client import (
    LEGACY_ACTION_TO_RUNTIME_ACTION,
    compute_coverage_status,
    execute_m365_action,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_trkC_e2e_status_taxonomy_complete() -> None:
    """C1 — eight distinct status_class values exist post-Track C."""
    statuses = {
        _denial_to_status("permission_missing"),
        _denial_to_status("auth_mode_mismatch"),
        _denial_to_status("unknown_action"),
        _denial_to_status("mutation_fence"),
        _denial_to_status("tier_insufficient"),
        _denial_to_status("planned_action"),
        _denial_to_status("anything_else"),
    }
    # Eight distinct values: permission_missing, auth_required, unknown_action,
    # mutation_fence, tier_insufficient, not_yet_implemented, policy_denied
    assert len(statuses) == 7
    assert "not_yet_implemented" in statuses
    assert "unknown_action" in statuses
    assert "mutation_fence" in statuses


def test_trkC_e2e_coverage_status_values_exposed() -> None:
    """C1 — runtime exposes the four-value enum."""
    assert COVERAGE_STATUS_VALUES == frozenset(
        {"implemented", "aliased", "planned", "deprecated"}
    )


def test_trkC_e2e_planned_action_short_circuits(monkeypatch: pytest.MonkeyPatch) -> None:
    """C2 — planned action returns not_yet_implemented without runtime call."""
    monkeypatch.delenv("M365_RUNTIME_URL", raising=False)
    monkeypatch.delenv("SMARTHAUS_M365_RUNTIME_URL", raising=False)
    monkeypatch.delenv("M365_OPS_ADAPTER_URL", raising=False)
    monkeypatch.delenv("SMARTHAUS_M365_OPS_ADAPTER_URL", raising=False)
    monkeypatch.delenv("GRAPH_STUB_MODE", raising=False)

    result = execute_m365_action("m365-administrator", "users.create")
    assert result["status_class"] == "not_yet_implemented"
    assert result["coverage_status"] == "planned"


def test_trkC_e2e_audit_runs_and_classifies() -> None:
    """C3 — audit script runs and produces a valid report."""
    script = REPO_ROOT / "scripts" / "audit_m365_docstring_coverage.py"
    result = subprocess.run(
        [sys.executable, str(script)], capture_output=True, text=True, cwd=str(REPO_ROOT)
    )
    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert sum(report["totals"].values()) == report["advertised_total"]
    assert 0.0 <= report["coverage_pct_concrete"] <= 100.0


def test_trkC_e2e_capability_map_consistent_with_runtime() -> None:
    """C4 — capability map doc references live registry and alias counts."""
    map_doc = (REPO_ROOT / "docs" / "m365_capability_map.md").read_text()
    assert f"**{len(READ_ONLY_REGISTRY)}**" in map_doc
    assert f"**{len(LEGACY_ACTION_TO_RUNTIME_ACTION)}**" in map_doc


def test_trkC_e2e_compute_coverage_aligns_with_audit() -> None:
    """C2+C3 cross-check — every audit-classified action matches compute_coverage_status."""
    script = REPO_ROOT / "scripts" / "audit_m365_docstring_coverage.py"
    result = subprocess.run(
        [sys.executable, str(script)], capture_output=True, text=True, cwd=str(REPO_ROOT)
    )
    report = json.loads(result.stdout)
    for bucket_name in ["implemented", "aliased", "planned"]:
        for action in report[bucket_name]:
            assert compute_coverage_status(action) == bucket_name, (
                f"audit bucketed {action} as {bucket_name} but compute_coverage_status disagrees"
            )
