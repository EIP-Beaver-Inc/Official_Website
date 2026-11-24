"""Licences du logiciel BEAVER : émission et signature.

Une licence est un texte signé avec la clé privée du site (Ed25519). Le
logiciel ne contient que la clé publique correspondante et vérifie la licence
sans connexion internet : une licence ne peut être ni inventée ni modifiée.

Format, identique à celui que lit le logiciel (Beaver/frontend/services/licence.py) :

    BVR1.<payload>.<signature>

    payload    base64url sans « = » d'un JSON compact UTF-8 :
               {"v": 1, "id": "LIC-…", "product": "beaver", "customer": "…",
                "email": "…", "issued": "AAAA-MM-JJ", "expires": "AAAA-MM-JJ" | null,
                "seats": 1}
    signature  base64url sans « = » de la signature Ed25519 des octets ASCII
               « BVR1.<payload> »

Toute évolution du format se fait des deux côtés à la fois, sous un nouveau
préfixe (BVR2).

Configuration : LICENCE_PRIVATE_KEY, la clé privée Ed25519 brute (32 octets)
en base64. Elle se génère avec :

    python licensing.py generate

qui affiche aussi la clé publique à reporter dans le logiciel (PUBLIC_KEY).
Perdre la clé privée, c'est ne plus pouvoir émettre de licence que les
logiciels déjà installés acceptent : la sauvegarder hors du serveur.
"""
from __future__ import annotations

import base64
import json
import os
import secrets
from dataclasses import dataclass
from datetime import date
from typing import Optional

PREFIX = "BVR1"
PRODUCT = "beaver"


class LicensingNotConfigured(RuntimeError):
    """LICENCE_PRIVATE_KEY absente ou illisible."""


@dataclass(frozen=True)
class IssuedLicence:
    id: str
    key: str
    customer: str
    email: str
    issued: str
    expires: Optional[str]
    seats: int


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _private_key():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    raw = os.environ.get("LICENCE_PRIVATE_KEY", "").strip()
    if not raw:
        raise LicensingNotConfigured(
            "LICENCE_PRIVATE_KEY n'est pas configurée : impossible d'émettre une licence.")
    try:
        return Ed25519PrivateKey.from_private_bytes(base64.b64decode(raw))
    except ValueError as exc:
        raise LicensingNotConfigured("LICENCE_PRIVATE_KEY est illisible.") from exc


def is_configured() -> bool:
    try:
        _private_key()
        return True
    except LicensingNotConfigured:
        return False


def public_key_b64() -> str:
    from cryptography.hazmat.primitives import serialization

    raw = _private_key().public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return base64.b64encode(raw).decode("ascii")


def new_licence_id() -> str:
    return "LIC-" + secrets.token_hex(4).upper()


def issue(customer: str, email: str, expires: Optional[date], seats: int = 1,
          licence_id: Optional[str] = None, issued: Optional[date] = None) -> IssuedLicence:
    """Une licence signée pour `customer`. `expires` None : sans limite de durée."""
    if seats < 1:
        raise ValueError("seats doit valoir au moins 1")
    issued = issued or date.today()
    if expires is not None and expires < issued:
        raise ValueError("la date de fin précède la date d'émission")
    payload = {
        "v": 1,
        "id": licence_id or new_licence_id(),
        "product": PRODUCT,
        "customer": " ".join(customer.split()),
        "email": email.strip(),
        "issued": issued.isoformat(),
        "expires": expires.isoformat() if expires else None,
        "seats": int(seats),
    }
    body = f"{PREFIX}." + _b64(json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    key = body + "." + _b64(_private_key().sign(body.encode("ascii")))
    return IssuedLicence(payload["id"], key, payload["customer"], payload["email"],
                         payload["issued"], payload["expires"], payload["seats"])


def _generate() -> None:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    key = Ed25519PrivateKey.generate()
    private = key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                                serialization.NoEncryption())
    public = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    print("LICENCE_PRIVATE_KEY=" + base64.b64encode(private).decode())
    print("# Clé publique, à mettre dans Beaver/frontend/services/licence.py (PUBLIC_KEY) :")
    print(base64.b64encode(public).decode())


if __name__ == "__main__":
    import sys

    if sys.argv[1:] == ["generate"]:
        _generate()
    elif sys.argv[1:] == ["public"]:
        print(public_key_b64())
    else:
        print("usage : python licensing.py generate | public")
        sys.exit(2)
