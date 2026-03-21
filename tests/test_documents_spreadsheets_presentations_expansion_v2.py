from __future__ import annotations

from collections.abc import Generator
import io
import zipfile
from typing import Any

import pytest

from provisioning_api.routers import m365 as m365_router
from smarthaus_common.approval_risk import (
    reload_approval_risk_registry,
    resolve_action_approval_risk,
)
from smarthaus_common.auth_model import reload_auth_model_registry, resolve_action_auth
from smarthaus_common.executor_routing import (
    executor_route_for_action,
    reload_executor_routing_registry,
)
from smarthaus_common.office_generation import (
    generate_docx_bytes,
    generate_pptx_bytes,
    generate_xlsx_bytes,
)


@pytest.fixture(autouse=True)
def _reload_registries() -> Generator[None, None, None]:
    reload_executor_routing_registry()
    reload_auth_model_registry()
    reload_approval_risk_registry()
    yield
    reload_executor_routing_registry()
    reload_auth_model_registry()
    reload_approval_risk_registry()


def _zip_entries(payload: bytes) -> set[str]:
    with zipfile.ZipFile(io.BytesIO(payload), "r") as archive:
        return set(archive.namelist())


def test_e2e_office_generation_is_deterministic_and_contains_expected_entries() -> None:
    doc_bytes_a = generate_docx_bytes(title="Quarterly Update", paragraphs=["Alpha", "Beta"])
    doc_bytes_b = generate_docx_bytes(title="Quarterly Update", paragraphs=["Alpha", "Beta"])
    assert doc_bytes_a == doc_bytes_b
    assert {"[Content_Types].xml", "_rels/.rels", "word/document.xml"}.issubset(
        _zip_entries(doc_bytes_a)
    )

    workbook_bytes_a = generate_xlsx_bytes(
        [{"name": "Sheet1", "rows": [["Name", "Value"], ["Alpha", 1]]}]
    )
    workbook_bytes_b = generate_xlsx_bytes(
        [{"name": "Sheet1", "rows": [["Name", "Value"], ["Alpha", 1]]}]
    )
    assert workbook_bytes_a == workbook_bytes_b
    assert {
        "[Content_Types].xml",
        "_rels/.rels",
        "xl/workbook.xml",
        "xl/worksheets/sheet1.xml",
    }.issubset(_zip_entries(workbook_bytes_a))

    presentation_bytes_a = generate_pptx_bytes(
        title="Board Review",
        slides=[{"title": "Overview", "bullets": ["Revenue", "Margin"]}],
    )
    presentation_bytes_b = generate_pptx_bytes(
        title="Board Review",
        slides=[{"title": "Overview", "bullets": ["Revenue", "Margin"]}],
    )
    assert presentation_bytes_a == presentation_bytes_b
    assert {
        "[Content_Types].xml",
        "_rels/.rels",
        "ppt/presentation.xml",
        "ppt/slides/slide1.xml",
    }.issubset(_zip_entries(presentation_bytes_a))


def test_e2e_instruction_schema_includes_productivity_actions() -> None:
    supported = {item["action"] for item in m365_router.INSTRUCTION_ACTIONS_SCHEMA}
    assert {
        "create_document",
        "update_document",
        "create_workbook",
        "update_workbook",
        "create_presentation",
        "update_presentation",
    }.issubset(supported)


def test_e2e_actions_route_to_sharepoint_and_use_hybrid_auth() -> None:
    for action in (
        "create_document",
        "update_document",
        "create_workbook",
        "update_workbook",
        "create_presentation",
        "update_presentation",
    ):
        assert executor_route_for_action(None, action) == "sharepoint"
        resolution = resolve_action_auth("m365-administrator", action, {})
        assert resolution.executor_domain == "sharepoint"
        assert resolution.auth_class == "hybrid"


def test_e2e_productivity_actions_resolve_expected_approval_profiles() -> None:
    for action in (
        "create_document",
        "update_document",
        "create_workbook",
        "update_workbook",
        "create_presentation",
        "update_presentation",
    ):
        resolution = resolve_action_approval_risk("m365-administrator", action, {})
        assert resolution.risk_class == "medium"
        assert resolution.approval_profile == "medium-operational"
        assert resolution.approval_required is False


def test_e2e_instruction_contract_executes_productivity_actions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, Any]] = []

    class _FakeClient:
        def upload_bytes(
            self,
            *,
            file_bytes: bytes,
            remote_path: str,
            drive_id: str | None = None,
            group_id: str | None = None,
            site_id: str | None = None,
            user_id_or_upn: str | None = None,
            conflict_behavior: str = "replace",
            content_type: str | None = None,
            source_name: str = "generated.bin",
        ) -> dict[str, Any]:
            calls.append(
                {
                    "size": len(file_bytes),
                    "remote_path": remote_path,
                    "drive_id": drive_id,
                    "group_id": group_id,
                    "site_id": site_id,
                    "user_id_or_upn": user_id_or_upn,
                    "conflict_behavior": conflict_behavior,
                    "content_type": content_type,
                    "source_name": source_name,
                }
            )
            return {"id": f"item-{len(calls)}", "name": source_name, "size": len(file_bytes)}

    monkeypatch.setenv("ALLOW_M365_MUTATIONS", "true")
    monkeypatch.setattr(m365_router, "_graph_client", lambda action=None: _FakeClient())

    document_payload = m365_router.execute_instruction_contract(
        action="create_document",
        params_payload={
            "siteId": "site-1",
            "remotePath": "deliverables/q1-update",
            "title": "Q1 Update",
            "paragraphs": ["Alpha", "Beta"],
        },
        trace_id="trace-document",
    )
    workbook_payload = m365_router.execute_instruction_contract(
        action="update_workbook",
        params_payload={
            "groupId": "group-1",
            "remotePath": "reports/weekly.xlsx",
            "worksheets": [{"name": "Summary", "rows": [["Metric", "Value"], ["Open", 4]]}],
        },
        trace_id="trace-workbook",
    )
    presentation_payload = m365_router.execute_instruction_contract(
        action="create_presentation",
        params_payload={
            "userPrincipalName": "m365-validation@smarthausgroup.com",
            "remotePath": "briefings/launch",
            "title": "Launch Briefing",
            "slides": [{"title": "Agenda", "bullets": ["Open", "Close"]}],
        },
        trace_id="trace-presentation",
    )

    assert document_payload["ok"] is True
    assert document_payload["result"]["status"] == "created"
    assert document_payload["result"]["document"]["name"] == "q1-update.docx"

    assert workbook_payload["ok"] is True
    assert workbook_payload["result"]["status"] == "updated"
    assert workbook_payload["result"]["workbook"]["name"] == "weekly.xlsx"

    assert presentation_payload["ok"] is True
    assert presentation_payload["result"]["status"] == "created"
    assert presentation_payload["result"]["presentation"]["name"] == "launch.pptx"

    assert calls[0]["site_id"] == "site-1"
    assert calls[0]["remote_path"] == "deliverables/q1-update.docx"
    assert calls[1]["group_id"] == "group-1"
    assert calls[1]["remote_path"] == "reports/weekly.xlsx"
    assert calls[2]["user_id_or_upn"] == "m365-validation@smarthausgroup.com"
    assert calls[2]["remote_path"] == "briefings/launch.pptx"


def test_e2e_fails_closed_on_mismatched_extension() -> None:
    payload = m365_router.execute_instruction_contract(
        action="create_document",
        params_payload={"siteId": "site-1", "remotePath": "deliverables/q1-update.txt"},
        trace_id="trace-bad-extension",
    )

    assert payload["ok"] is False
    assert "must end with '.docx'" in payload["error"]
