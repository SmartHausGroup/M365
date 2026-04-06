from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import parse_qs

import httpx
import pytest
import respx
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from smarthaus_common.config import AppConfig
from smarthaus_common.errors import AuthConfigurationError
from smarthaus_common.tenant_config import AppOnlyAuthConfig, AuthConfig, AzureConfig, TenantConfig
from smarthaus_graph.client import (
    GraphClient,
    GraphTokenProvider,
    _load_client_certificate_credential,
)


class DummyTP(GraphTokenProvider):
    def __init__(self) -> None:
        self._token = None

    def get_token(self, prefer_delegated: bool = False) -> str:
        del prefer_delegated
        return "dummy-token"


def _write_executor_pem(tmp_path: Path) -> tuple[Path, x509.Certificate]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "SMARTHAUS M365 Executor")])
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(UTC) - timedelta(minutes=1))
        .not_valid_after(datetime.now(UTC) + timedelta(days=30))
        .sign(key, hashes.SHA256())
    )
    pem_path = tmp_path / "executor.pem"
    pem_path.write_text(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")
        + certificate.public_bytes(serialization.Encoding.PEM).decode("utf-8"),
        encoding="utf-8",
    )
    return pem_path, certificate


def test_graph_client_get_org() -> None:
    cfg = AppConfig()
    client = GraphClient(config=cfg)
    # Inject dummy token provider
    client._token_provider = DummyTP()

    with respx.mock(base_url="https://graph.microsoft.com") as mock:
        route = mock.get("/v1.0/organization").mock(
            return_value=httpx.Response(200, json={"value": [{"displayName": "SmartHaus"}]})
        )
        data = client.get_organization()
        assert "value" in data
        assert route.called


def test_graph_client_list_directory_roles_omits_custom_page_size() -> None:
    cfg = AppConfig()
    client = GraphClient(config=cfg)
    client._token_provider = DummyTP()

    with respx.mock(base_url="https://graph.microsoft.com") as mock:
        route = mock.get("/v1.0/directoryRoles").mock(
            return_value=httpx.Response(200, json={"value": [{"id": "role-1"}]})
        )
        data = client.list_directory_roles(top=5)

    assert data == {"value": [{"id": "role-1"}]}
    assert route.called
    assert "$top" not in route.calls[0].request.url.params
    assert route.calls[0].request.url.params["$select"] == "id,displayName,description"


def test_load_client_certificate_credential_from_pem(tmp_path: Path) -> None:
    pem_path, certificate = _write_executor_pem(tmp_path)

    credential = _load_client_certificate_credential(str(pem_path))

    assert "BEGIN PRIVATE KEY" in credential["private_key"]
    assert credential["thumbprint"] == certificate.fingerprint(hashes.SHA1()).hex().upper()
    assert "BEGIN CERTIFICATE" in credential["public_certificate"]


def test_load_client_certificate_credential_rejects_invalid_pem(tmp_path: Path) -> None:
    pem_path = tmp_path / "invalid.pem"
    pem_path.write_text("not-a-valid-cert", encoding="utf-8")

    with pytest.raises(AuthConfigurationError):
        _load_client_certificate_credential(str(pem_path))


def test_graph_token_provider_uses_direct_client_secret_flow_without_msal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_config = TenantConfig(
        azure=AzureConfig(
            tenant_id="tenant-123",
            client_id="client-123",
            client_secret="secret-123",
        ),
        auth=AuthConfig(mode="app_only", app_only=AppOnlyAuthConfig()),
    )
    provider = GraphTokenProvider(tenant_config=tenant_config)

    monkeypatch.setattr("smarthaus_graph.client.ConfidentialClientApplication", None)

    with respx.mock(base_url="https://login.microsoftonline.com") as mock:
        route = mock.post("/tenant-123/oauth2/v2.0/token").mock(
            return_value=httpx.Response(
                200,
                json={
                    "access_token": "direct-token",
                    "expires_in": 3600,
                },
            )
        )
        token = provider.get_app_token()

    assert token == "direct-token"
    assert route.called


def test_graph_token_provider_direct_client_secret_flow_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_config = TenantConfig(
        azure=AzureConfig(
            tenant_id="tenant-123",
            client_id="client-123",
            client_secret="secret-123",
        ),
        auth=AuthConfig(mode="app_only", app_only=AppOnlyAuthConfig()),
    )
    provider = GraphTokenProvider(tenant_config=tenant_config)

    monkeypatch.setattr("smarthaus_graph.client.ConfidentialClientApplication", None)

    with respx.mock(base_url="https://login.microsoftonline.com") as mock:
        mock.post("/tenant-123/oauth2/v2.0/token").mock(
            return_value=httpx.Response(
                400,
                json={"error_description": "AADSTS7000215: Invalid client secret."},
            )
        )
        with pytest.raises(AuthConfigurationError, match="Invalid client secret"):
            provider.get_app_token()


def test_graph_token_provider_uses_direct_certificate_flow_without_msal(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    pem_path, _certificate = _write_executor_pem(tmp_path)
    tenant_config = TenantConfig(
        azure=AzureConfig(
            tenant_id="tenant-123",
            client_id="client-123",
            client_secret="secret-123",
            client_certificate_path=str(pem_path),
        ),
        auth=AuthConfig(mode="app_only", app_only=AppOnlyAuthConfig()),
    )
    provider = GraphTokenProvider(tenant_config=tenant_config)

    monkeypatch.setattr("smarthaus_graph.client.ConfidentialClientApplication", None)

    with respx.mock(base_url="https://login.microsoftonline.com") as mock:
        route = mock.post("/tenant-123/oauth2/v2.0/token").mock(
            return_value=httpx.Response(
                200,
                json={
                    "access_token": "direct-cert-token",
                    "expires_in": 3600,
                },
            )
        )
        token = provider.get_app_token()

    assert token == "direct-cert-token"
    assert route.called
    body = parse_qs(route.calls[0].request.content.decode("utf-8"))
    assert body["client_id"] == ["client-123"]
    assert body["grant_type"] == ["client_credentials"]
    assert body["scope"] == ["https://graph.microsoft.com/.default"]
    assert body["client_assertion_type"] == [
        "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
    ]
    assert len(body["client_assertion"][0].split(".")) == 3
    assert "client_secret" not in body
