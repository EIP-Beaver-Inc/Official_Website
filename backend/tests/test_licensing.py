"""Licences signées (licensing.py)."""
import base64
import json
from datetime import date

import pytest

import licensing


def _decode(part: str) -> bytes:
    return base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))


def test_the_licence_is_signed_with_the_configured_key(signing_key):
    lic = licensing.issue("Scierie  du   Lac", " achat@lac.fr ", date(2027, 11, 24), seats=2,
                          issued=date(2026, 11, 24))
    prefix, payload, signature = lic.key.split(".")
    assert prefix == "BVR1"
    signing_key.public_key().verify(_decode(signature), f"{prefix}.{payload}".encode("ascii"))
    data = json.loads(_decode(payload))
    assert data == {"v": 1, "id": lic.id, "product": "beaver", "customer": "Scierie du Lac",
                    "email": "achat@lac.fr", "issued": "2026-11-24", "expires": "2027-11-24", "seats": 2}
    assert lic.id.startswith("LIC-") and lic.expires == "2027-11-24"


def test_a_licence_without_end_date(signing_key):
    lic = licensing.issue("Scierie", "a@b.fr", None)
    assert lic.expires is None
    assert json.loads(_decode(lic.key.split(".")[1]))["expires"] is None


def test_nonsense_is_refused(signing_key):
    with pytest.raises(ValueError):
        licensing.issue("Scierie", "a@b.fr", date(2020, 1, 1), issued=date(2026, 1, 1))
    with pytest.raises(ValueError):
        licensing.issue("Scierie", "a@b.fr", None, seats=0)


def test_without_a_key_nothing_is_issued(monkeypatch):
    monkeypatch.delenv("LICENCE_PRIVATE_KEY", raising=False)
    assert not licensing.is_configured()
    with pytest.raises(licensing.LicensingNotConfigured):
        licensing.issue("Scierie", "a@b.fr", None)


def test_the_public_key_matches(signing_key):
    from cryptography.hazmat.primitives import serialization
    expected = signing_key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    assert licensing.public_key_b64() == base64.b64encode(expected).decode()
