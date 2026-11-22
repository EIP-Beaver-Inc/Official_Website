"""MongoDB collections and indexes for BETA licenses.

The project uses MongoDB (no SQL migrations): ``ensure_indexes`` is the
"migration". It is idempotent, runs at backend startup and via
``beta-db init``. The collection names are distinct from the website's beta
portal (``beta_keys`` / ``beta_clients``), which is a separate system.
"""
from __future__ import annotations

import ipaddress
import uuid
from datetime import datetime, timezone
from typing import Optional

KEYS = "beta_license_keys"
ACTIVATIONS = "beta_activations"
EVENTS = "beta_events"
RELEASES = "beta_releases"
DOWNLOAD_TOKENS = "beta_download_tokens"


async def ensure_indexes(db) -> None:
    await db[KEYS].create_index("id", unique=True)
    await db[KEYS].create_index("key_hash", unique=True)
    await db[ACTIVATIONS].create_index([("key_id", 1), ("machine_hash", 1)], unique=True)
    await db[EVENTS].create_index([("key_id", 1), ("at", -1)])
    await db[EVENTS].create_index([("at", -1)])
    await db[RELEASES].create_index("id", unique=True)
    await db[RELEASES].create_index([("platform", 1), ("is_active", 1), ("created_at", -1)])
    await db[DOWNLOAD_TOKENS].create_index("jti", unique=True)
    # Mongo's TTL monitor removes tokens once expired (validity is also checked in code).
    await db[DOWNLOAD_TOKENS].create_index("expires_at", expireAfterSeconds=0)


def new_id() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def truncate_ip(ip: Optional[str]) -> Optional[str]:
    """IPv4 -> /24, IPv6 -> /48 (spec section 4)."""
    if not ip:
        return None
    try:
        addr = ipaddress.ip_address(ip.strip())
    except ValueError:
        return None
    if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped:
        addr = addr.ipv4_mapped
    prefix = 24 if addr.version == 4 else 48
    return str(ipaddress.ip_network(f"{addr}/{prefix}", strict=False))


async def log_event(db, type_: str, *, key_id: Optional[str] = None, ip_truncated: Optional[str] = None,
                    details: Optional[dict] = None, at: Optional[datetime] = None) -> None:
    """Audit log. ``details`` must stay short and NEVER contain a key or a model key."""
    await db[EVENTS].insert_one({
        "id": new_id(),
        "key_id": key_id,
        "type": type_,
        "at": at or utcnow(),
        "ip_truncated": ip_truncated,
        "details": details or {},
    })
