"""Computed key status (spec section 4). Single source of truth, heavily tested."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Mapping, Optional

ACTIVE = "active"
EXPIRED = "expired"
REVOKED = "revoked"
INVALID = "invalid"
MACHINE_LIMIT = "machine_limit"
UPDATE_REQUIRED = "update_required"


def as_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Mongo returns naive datetimes (UTC); make every datetime tz-aware UTC."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def compute_status(key: Mapping, now: datetime) -> str:
    """
    revoked                                         -> revoked
    activated_at is NULL and now > redeem_by        -> expired
    expires_at not NULL and now >= expires_at       -> expired
    otherwise                                       -> active
    """
    now = as_utc(now)
    if key.get("revoked"):
        return REVOKED
    activated_at = as_utc(key.get("activated_at"))
    redeem_by = as_utc(key.get("redeem_by"))
    expires_at = as_utc(key.get("expires_at"))
    if activated_at is None and redeem_by is not None and now > redeem_by:
        return EXPIRED
    if expires_at is not None and now >= expires_at:
        return EXPIRED
    return ACTIVE
