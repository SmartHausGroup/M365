from __future__ import annotations

import json
from pathlib import Path

import yaml


def _load_h3_sources() -> tuple[dict, dict, dict, str, str, str]:
    root = Path(__file__).resolve().parents[1]
    ai_team = json.loads((root / "registry" / "ai_team.json").read_text(encoding="utf-8"))
    frozen_h3_scorecard = json.loads(
        (root / "artifacts" / "scorecards" / "scorecard_l78.json").read_text(encoding="utf-8")
    )
    h3_lemma = (
        root / "docs" / "ma" / "lemmas" / "L78_m365_authoritative_persona_registry_rebase_v1.md"
    ).read_text(encoding="utf-8")
    h3_invariant = (
        root / "invariants" / "lemmas" / "L78_m365_authoritative_persona_registry_rebase_v1.yaml"
    ).read_text(encoding="utf-8")
    h3_notebook = json.loads(
        (
            root
            / "notebooks"
            / "m365"
            / "INV-M365-BZ-authoritative-persona-registry-rebase-v1.ipynb"
        ).read_text(encoding="utf-8")
    )
    h3_notebook_source = "\n".join("".join(cell.get("source", [])) for cell in h3_notebook["cells"])
    promoted_records = yaml.safe_load(
        (root / "registry" / "authoritative_digital_employee_records_v1.yaml").read_text(
            encoding="utf-8"
        )
    )["records"]
    return (
        ai_team,
        frozen_h3_scorecard,
        promoted_records,
        h3_lemma,
        h3_invariant,
        h3_notebook_source,
    )


def test_h3_authoritative_surfaces_reconcile_to_staged_truth() -> None:
    ai_team, frozen_h3_scorecard, promoted_records, h3_lemma, h3_invariant, h3_notebook_source = (
        _load_h3_sources()
    )

    assert ai_team["total_agents"] == 59
    assert len(ai_team["departments"]) == 10
    assert frozen_h3_scorecard["status"] == "green"
    assert (
        "The staged registry truth remains 34 active personas and 25 planned personas before H5 activation."
        in frozen_h3_scorecard["notes"]
    )
    assert (
        "Registry59_34_25 := total_personas = 59 AND active_personas = 34 AND planned_personas = 25"
        in h3_lemma
    )
    assert (
        "the persona registry must report exactly 34 active personas and 25 planned personas"
        in h3_invariant
    )
    assert "'total_personas': 59" in h3_notebook_source
    assert "'total_departments': 10" in h3_notebook_source
    assert "'active_personas': 34" in h3_notebook_source
    assert "'planned_personas': 25" in h3_notebook_source
    assert len(promoted_records) == 20


def test_h3_promoted_personas_are_authoritative_but_still_planned() -> None:
    ai_team, frozen_h3_scorecard, promoted_records, h3_lemma, h3_invariant, h3_notebook_source = (
        _load_h3_sources()
    )

    roster_members = {
        member["agent"]: member for members in ai_team["departments"].values() for member in members
    }
    for agent_id, record in promoted_records.items():
        roster_entry = roster_members[agent_id]

        assert roster_entry["name"] == record["display_name"]
        assert roster_entry["role"] == record["title"]
        assert roster_entry["manager"] == record["manager"]
        assert roster_entry["escalation_owner"] == record["escalation_owner"]
        assert f"'{agent_id}':" in h3_notebook_source

    assert (
        "Promoted personas are authoritative in H3 but remain persona-contract-only with zero actions and zero domains."
        in frozen_h3_scorecard["notes"]
    )
    assert "every promoted persona remains `persona-contract-only`" in h3_lemma
    assert (
        "every promoted persona must remain persona-contract-only with zero allowed actions and zero allowed domains"
        in h3_invariant
    )
    assert (
        "ActivationSeparation := FOR ALL promoted_persona, allowed_actions = [] AND allowed_domains = [] AND action_count = 0"
        in h3_lemma
    )
    assert "assert persona['coverage_status'] == 'persona-contract-only'" in h3_notebook_source
    assert "assert persona['status'] == 'planned'" in h3_notebook_source
