"""Signed envelopes (spec 2.3 / 5.2) and key generation helpers.

Envelope: {"payload": b64url(JSON UTF-8), "signature": b64url(Ed25519(payload string as ASCII)), "kid"}.
base64url is emitted WITHOUT padding (RFC 7515 style); decoders should accept both.
"""
from __future__ import annotations

import base64
import json
import secrets
from datetime import datetime, timezone
from typing import Any, Mapping

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64url_decode(value: str) -> bytes:
    """Strict base64url decoding (padding optional). Raises ValueError."""
    if not isinstance(value, str) or not value or any(c not in _B64URL_CHARS for c in value.rstrip("=")):
        raise ValueError("not base64url")
    stripped = value.rstrip("=")
    return base64.urlsafe_b64decode(stripped + "=" * (-len(stripped) % 4))


_B64URL_CHARS = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_")


def iso_utc(dt: datetime) -> str:
    """UTC, ISO 8601, second precision, 'Z' suffix (spec 2.3)."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def encode_payload(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return b64url_encode(raw)


def sign_envelope(signing_key: Ed25519PrivateKey, kid: str, payload: Mapping[str, Any]) -> dict:
    payload_b64 = encode_payload(payload)
    signature = signing_key.sign(payload_b64.encode("ascii"))
    return {"payload": payload_b64, "signature": b64url_encode(signature), "kid": kid}


def verify_envelope(public_key: Ed25519PublicKey, envelope: Mapping[str, str]) -> dict:
    """Reference verification, same algorithm the software must implement.

    Raises cryptography.exceptions.InvalidSignature on a bad signature.
    """
    payload_b64 = envelope["payload"]
    public_key.verify(b64url_decode(envelope["signature"]), payload_b64.encode("ascii"))
    return json.loads(b64url_decode(payload_b64).decode("utf-8"))


def public_key_b64(private_key: Ed25519PrivateKey) -> str:
    raw = private_key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return base64.b64encode(raw).decode("ascii")


def private_key_b64(private_key: Ed25519PrivateKey) -> str:
    raw = private_key.private_bytes(
        serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption()
    )
    return base64.b64encode(raw).decode("ascii")


def generate_signing_key() -> Ed25519PrivateKey:
    return Ed25519PrivateKey.generate()


def generate_model_key() -> bytes:
    """AES-256-GCM key for the encrypted models (spec 2.7)."""
    return secrets.token_bytes(32)
