from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
import pytest
import respx
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from smarthaus_common.config import AppConfig
from smarthaus_common.errors import AuthConfigurationError
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


def test_load_client_certificate_credential_from_pem(tmp_path: Path) -> None:
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

    credential = _load_client_certificate_credential(str(pem_path))

    assert "BEGIN PRIVATE KEY" in credential["private_key"]
    assert credential["thumbprint"] == certificate.fingerprint(hashes.SHA1()).hex().upper()
    assert "BEGIN CERTIFICATE" in credential["public_certificate"]


def test_load_client_certificate_credential_rejects_invalid_pem(tmp_path: Path) -> None:
    pem_path = tmp_path / "invalid.pem"
    pem_path.write_text("not-a-valid-cert", encoding="utf-8")

    with pytest.raises(AuthConfigurationError):
        _load_client_certificate_credential(str(pem_path))
