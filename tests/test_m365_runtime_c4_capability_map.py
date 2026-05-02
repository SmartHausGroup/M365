"""Tests for C4 Capability Map generator. plan:m365-cps-trkC-p4-operator-capability-map / L112"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "generate_m365_capability_map.py"


def _run() -> str:
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    return result.stdout


def test_c4_generator_present() -> None:
    """L112.L_GENERATOR_PRESENT."""
    assert SCRIPT.is_file()


def test_c4_doc_has_three_sections() -> None:
    """L112.L_DOC_HAS_THREE_SECTIONS."""
    text = _run()
    assert "## Implemented actions" in text
    assert "## Legacy aliases" in text
    assert "## Coverage status by agent" in text


def test_c4_output_deterministic() -> None:
    """L112.L_OUTPUT_DETERMINISTIC — two runs are byte-identical."""
    a = _run()
    b = _run()
    assert a == b


def test_c4_doc_references_live_data() -> None:
    """L112.L_DOC_REFERENCES_LIVE_DATA — counts reflect current registry/aliases."""
    text = _run()
    from m365_runtime.graph.registry import READ_ONLY_REGISTRY
    from ucp_m365_pack.client import LEGACY_ACTION_TO_RUNTIME_ACTION

    assert f"**{len(READ_ONLY_REGISTRY)}**" in text
    assert f"**{len(LEGACY_ACTION_TO_RUNTIME_ACTION)}**" in text


def test_c4_writes_to_out_path(tmp_path: Path) -> None:
    """--out path works."""
    out = tmp_path / "cap_map.md"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--out", str(out)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0
    assert out.is_file()
    assert out.stat().st_size > 0
