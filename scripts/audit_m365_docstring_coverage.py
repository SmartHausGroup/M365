#!/usr/bin/env python3
"""Audit m365 capability pack coverage and emit a JSON report.

plan:m365-cps-trkC-p3-mcp-tool-docstrings:T2 / L111

Reads `registry/agents.yaml` allowed_actions (the operator-facing
surface), classifies each action via `compute_coverage_status` (which
checks the live runtime registry + alias table), and emits a JSON
report categorizing every action as implemented / aliased / planned /
deprecated. Doubles as a CI linter: a non-zero exit code can be tied
to a coverage threshold by passing `--min-coverage` (default 0,
i.e. always passes — there is no required floor today).

Usage:
    .venv/bin/python scripts/audit_m365_docstring_coverage.py
    .venv/bin/python scripts/audit_m365_docstring_coverage.py --min-coverage 0.50
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import yaml  # noqa: E402

from ucp_m365_pack.client import compute_coverage_status  # noqa: E402


def _load_agents_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"agents": {}}
    return yaml.safe_load(path.read_text()) or {"agents": {}}


def audit(agents_yaml_path: Path) -> dict[str, Any]:
    """Classify every allowed_action in agents.yaml against the runtime surface."""
    data = _load_agents_yaml(agents_yaml_path)
    advertised: set[str] = set()
    per_agent: dict[str, list[str]] = defaultdict(list)
    for agent_id, agent_cfg in (data.get("agents") or {}).items():
        if not isinstance(agent_cfg, dict):
            continue
        allowed = agent_cfg.get("allowed_actions") or []
        for entry in allowed:
            if isinstance(entry, str):
                advertised.add(entry)
                per_agent[agent_id].append(entry)

    classified: dict[str, list[str]] = {
        "implemented": [],
        "aliased": [],
        "planned": [],
        "deprecated": [],
    }
    for action in advertised:
        coverage = compute_coverage_status(action)
        if coverage in classified:
            classified[coverage].append(action)
        else:
            classified["planned"].append(action)

    for bucket in classified.values():
        bucket.sort()

    totals = {k: len(v) for k, v in classified.items()}
    advertised_total = sum(totals.values())
    concrete = totals["implemented"] + totals["aliased"]
    coverage_pct_concrete = (
        round(concrete / advertised_total * 100, 2) if advertised_total else 0.0
    )

    return {
        "implemented": classified["implemented"],
        "aliased": classified["aliased"],
        "planned": classified["planned"],
        "deprecated": classified["deprecated"],
        "totals": totals,
        "advertised_total": advertised_total,
        "coverage_pct_concrete": coverage_pct_concrete,
        "per_agent_action_count": {agent: len(actions) for agent, actions in per_agent.items()},
        "agents_yaml": str(agents_yaml_path),
        "lemma_reference": "L111_m365_cps_c3_docstring_audit_v1",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--agents-yaml",
        type=Path,
        default=REPO_ROOT / "registry" / "agents.yaml",
        help="Path to agents.yaml (defaults to registry/agents.yaml)",
    )
    parser.add_argument(
        "--min-coverage",
        type=float,
        default=0.0,
        help="Minimum coverage_pct_concrete to require (0.0 = no floor)",
    )
    args = parser.parse_args(argv)

    report = audit(args.agents_yaml)
    print(json.dumps(report, indent=2, sort_keys=True))

    if report["coverage_pct_concrete"] < args.min_coverage:
        print(
            f"FAIL: coverage_pct_concrete={report['coverage_pct_concrete']} < min={args.min_coverage}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
