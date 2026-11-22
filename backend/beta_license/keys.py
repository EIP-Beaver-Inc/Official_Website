"""BETA key format (spec 2.1): BETA-XXXX-XXXX-XXXX-XXXX, Crockford base32, 80 bits."""
from __future__ import annotations

import hashlib
import hmac
import re
import secrets

CROCKFORD_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
KEY_RE = re.compile(r"^BETA-[0-9A-HJKMNP-TV-Z]{4}(-[0-9A-HJKMNP-TV-Z]{4}){3}$")
MAX_RAW_KEY_LENGTH = 64


def generate_key() -> str:
    """16 Crockford base32 characters drawn from a CSPRNG (16 x 5 = 80 bits)."""
    chars = "".join(secrets.choice(CROCKFORD_ALPHABET) for _ in range(16))
    return "BETA-" + "-".join(chars[i:i + 4] for i in range(0, 16, 4))


def normalize_key(raw: str) -> str:
    """Spec 2.1: trim, uppercase, remove spaces."""
    return raw.strip().upper().replace(" ", "")


def is_valid_format(normalized: str) -> bool:
    return bool(KEY_RE.fullmatch(normalized))


def key_hash(pepper: bytes, normalized: str) -> str:
    """HMAC-SHA256(pepper, normalized key), hex. The plaintext key is never stored."""
    return hmac.new(pepper, normalized.encode("ascii"), hashlib.sha256).hexdigest()


def key_hint(normalized: str) -> str:
    """Last 4 characters, so an admin can identify a key."""
    return normalized[-4:]
