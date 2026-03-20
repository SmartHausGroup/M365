from __future__ import annotations

import pytest

from smarthaus_common.errors import SmarthausError
from provisioning_api import m365_provision


class _FakeProvisionClient:
    def __init__(self) -> None:
        self.created_libs: list[str] = []
        self.path_lookups = 0

    def find_group_by_mailnickname(self, mail_nickname: str) -> dict[str, str] | None:
        assert mail_nickname == "hr"
        return {"id": "group-123", "displayName": "Human Resources"}

    def create_group(
        self, display_name: str, mail_nickname: str, description: str | None = None
    ) -> dict[str, str]:
        raise AssertionError("create_group should not run for an existing service")

    def get_group_root_site(self, group_id: str) -> dict[str, str]:
        assert group_id == "group-123"
        return {"id": "site-456", "webUrl": "https://smarthausgroup.sharepoint.com/sites/hr2"}

    def get_site_by_path(self, hostname: str, site_path: str) -> dict[str, str]:
        self.path_lookups += 1
        raise AssertionError("path lookup should not be used when group root site resolves")

    def list_site_lists(self, site_id: str) -> list[dict[str, str]]:
        assert site_id == "site-456"
        return []

    def create_document_library(self, site_id: str, display_name: str) -> dict[str, str]:
        assert site_id == "site-456"
        self.created_libs.append(display_name)
        return {"displayName": display_name}


class _FallbackProvisionClient(_FakeProvisionClient):
    def __init__(self) -> None:
        super().__init__()
        self.root_lookups = 0

    def get_group_root_site(self, group_id: str) -> dict[str, str]:
        self.root_lookups += 1
        raise SmarthausError("group root site not ready")

    def get_site_by_path(self, hostname: str, site_path: str) -> dict[str, str]:
        self.path_lookups += 1
        assert hostname == "smarthausgroup.sharepoint.com"
        assert site_path == "hr"
        return {"id": "site-789", "webUrl": "https://smarthausgroup.sharepoint.com/sites/hr"}

    def list_site_lists(self, site_id: str) -> list[dict[str, str]]:
        assert site_id == "site-789"
        return [{"displayName": "Documents"}]


def test_provision_group_site_prefers_group_root_site_for_existing_group(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = _FakeProvisionClient()
    monkeypatch.setattr(m365_provision, "_graph_client", lambda route_key=None: fake_client)
    monkeypatch.setattr(m365_provision, "_hostname", lambda: "smarthausgroup.sharepoint.com")

    result = m365_provision.provision_group_site(
        display_name="HR Hub",
        mail_nickname="hr",
        libraries=["Documents"],
        description="Service workspace for HR Hub",
        wait_secs=3,
    )

    assert result == {
        "site_id": "site-456",
        "site_url": "https://smarthausgroup.sharepoint.com/sites/hr2",
        "group_created": False,
        "libraries_created": ["Documents"],
    }
    assert fake_client.path_lookups == 0


def test_provision_group_site_falls_back_to_path_lookup_when_root_site_not_ready(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = _FallbackProvisionClient()
    monkeypatch.setattr(m365_provision, "_graph_client", lambda route_key=None: fake_client)
    monkeypatch.setattr(m365_provision, "_hostname", lambda: "smarthausgroup.sharepoint.com")

    result = m365_provision.provision_group_site(
        display_name="HR Hub",
        mail_nickname="hr",
        libraries=["Documents"],
        description="Service workspace for HR Hub",
        wait_secs=3,
    )

    assert result == {
        "site_id": "site-789",
        "site_url": "https://smarthausgroup.sharepoint.com/sites/hr",
        "group_created": False,
        "libraries_created": [],
    }
    assert fake_client.root_lookups == 1
    assert fake_client.path_lookups == 1
