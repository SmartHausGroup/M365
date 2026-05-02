"""Tests for C3 Docstring Audit script. plan:m365-cps-trkC-p3-mcp-tool-docstrings / L111"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "audit_m365_docstring_coverage.py"


def test_c3_audit_script_exists() -> None:
    """L111.L_AUDIT_SCRIPT_PRESENT."""
    assert SCRIPT.is_file()
    assert SCRIPT.stat().st_size > 0


def _run_audit() -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, f"stderr: {result.stderr}\nstdout: {result.stdout[:500]}"
    return json.loads(result.stdout)


def test_c3_audit_output_has_required_keys() -> None:
    """L111.L_AUDIT_OUTPUT_VALID."""
    report = _run_audit()
    required = {
        "implemented",
        "aliased",
        "planned",
        "deprecated",
        "totals",
        "advertised_total",
        "coverage_pct_concrete",
    }
    assert required.issubset(set(report.keys()))


def test_c3_audit_buckets_partition_advertised_total() -> None:
    """totals sum to advertised_total."""
    report = _run_audit()
    total = sum(report["totals"].values())
    assert total == report["advertised_total"]


def test_c3_audit_lists_are_sorted() -> None:
    """L111.L_LINTER_DETERMINISTIC — buckets are sorted lists."""
    report = _run_audit()
    for bucket in ["implemented", "aliased", "planned", "deprecated"]:
        assert report[bucket] == sorted(report[bucket])


def test_c3_audit_deterministic_across_runs() -> None:
    """L111.L_LINTER_DETERMINISTIC — same input -> same output."""
    a = _run_audit()
    b = _run_audit()
    assert a == b


def test_c3_audit_coverage_pct_in_valid_range() -> None:
    """coverage_pct_concrete is a percentage in [0, 100]."""
    report = _run_audit()
    assert 0.0 <= report["coverage_pct_concrete"] <= 100.0


def test_c3_audit_min_coverage_floor_enforced() -> None:
    """--min-coverage exits non-zero when floor not met."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--min-coverage", "999.0"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 1
    assert "FAIL" in result.stderr
