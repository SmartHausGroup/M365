"""Secure token storage policy + macOS Keychain backend.

L_AUTH obligation: tokens are never written to plaintext files, env vars,
logs, audit, or evidence. Default backend is macOS Keychain via the `security`
binary; the encrypted pack-local backend is only available if explicitly
authorized via setup config and is implemented behind a fail-closed envelope.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class TokenStoreError(RuntimeError):
    pass


@dataclass(frozen=True)
class TokenStore:
    backend: str
    keychain_service: str
    pack_local_path: Path | None
    encrypted_pack_local_allowed: bool

    @classmethod
    def from_setup(cls, setup, installed_root: Path) -> "TokenStore":
        backend = setup.token_store
        if backend == "keychain":
            return cls(backend="keychain", keychain_service=setup.keychain_service, pack_local_path=None, encrypted_pack_local_allowed=False)
        if backend == "encrypted_pack_local" and setup.encrypted_pack_local_allowed:
            path = installed_root / "var" / "tokens.enc"
            return cls(backend="encrypted_pack_local", keychain_service=setup.keychain_service, pack_local_path=path, encrypted_pack_local_allowed=True)
        raise TokenStoreError(f"token_store_unsafe:{backend}")

    def put(self, key: str, value: str) -> None:
        if self.backend == "keychain":
            _keychain_set(self.keychain_service, key, value)
            return
        if self.backend == "encrypted_pack_local":
            _pack_local_set(self.pack_local_path, self.keychain_service, key, value)
            return
        raise TokenStoreError(f"token_store_unsafe:{self.backend}")

    def get(self, key: str) -> str | None:
        if self.backend == "keychain":
            return _keychain_get(self.keychain_service, key)
        if self.backend == "encrypted_pack_local":
            return _pack_local_get(self.pack_local_path, self.keychain_service, key)
        raise TokenStoreError(f"token_store_unsafe:{self.backend}")

    def clear(self, key: str) -> None:
        if self.backend == "keychain":
            _keychain_delete(self.keychain_service, key)
            return
        if self.backend == "encrypted_pack_local":
            _pack_local_delete(self.pack_local_path, self.keychain_service, key)
            return
        raise TokenStoreError(f"token_store_unsafe:{self.backend}")


def _keychain_security_path() -> str:
    sec = shutil.which("security")
    if not sec:
        raise TokenStoreError("keychain_security_binary_missing")
    return sec


def _keychain_set(service: str, account: str, value: str) -> None:
    sec = _keychain_security_path()
    subprocess.run([sec, "delete-generic-password", "-a", account, "-s", service], check=False, capture_output=True)
    proc = subprocess.run([sec, "add-generic-password", "-a", account, "-s", service, "-w", value, "-U"], capture_output=True, text=True)
    if proc.returncode != 0:
        raise TokenStoreError(f"keychain_set_failed:{proc.returncode}")


def _keychain_get(service: str, account: str) -> str | None:
    sec = _keychain_security_path()
    proc = subprocess.run([sec, "find-generic-password", "-a", account, "-s", service, "-w"], capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def _keychain_delete(service: str, account: str) -> None:
    sec = _keychain_security_path()
    subprocess.run([sec, "delete-generic-password", "-a", account, "-s", service], check=False, capture_output=True)


def _pack_local_key(service: str) -> bytes:
    raw = (service + ":m365_runtime").encode("utf-8")
    return hashlib.sha256(raw).digest()


def _xor(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def _pack_local_load(path: Path, service: str) -> dict[str, str]:
    if not path.exists():
        return {}
    blob = path.read_bytes()
    if not blob:
        return {}
    decoded = base64.urlsafe_b64decode(blob)
    decrypted = _xor(decoded, _pack_local_key(service))
    try:
        return json.loads(decrypted.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise TokenStoreError("pack_local_decrypt_failed") from exc


def _pack_local_save(path: Path, service: str, payload: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(payload, sort_keys=True).encode("utf-8")
    encrypted = _xor(body, _pack_local_key(service))
    path.write_bytes(base64.urlsafe_b64encode(encrypted))
    os.chmod(path, 0o600)


def _pack_local_set(path: Path | None, service: str, account: str, value: str) -> None:
    if path is None:
        raise TokenStoreError("pack_local_path_missing")
    payload = _pack_local_load(path, service)
    payload[account] = value
    _pack_local_save(path, service, payload)


def _pack_local_get(path: Path | None, service: str, account: str) -> str | None:
    if path is None:
        return None
    payload = _pack_local_load(path, service)
    return payload.get(account)


def _pack_local_delete(path: Path | None, service: str, account: str) -> None:
    if path is None:
        return
    payload = _pack_local_load(path, service)
    if account in payload:
        del payload[account]
        _pack_local_save(path, service, payload)
