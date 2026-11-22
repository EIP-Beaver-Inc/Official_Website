"""Server logic for /api/beta/validate, /api/beta/download and the /beta web page."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import math
import os
import secrets
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pymongo.errors import DuplicateKeyError

from . import storage
from .config import MODEL_KEY_ID_RE, BetaConfig
from .crypto import b64url_decode, b64url_encode, iso_utc, sign_envelope
from .keys import MAX_RAW_KEY_LENGTH, is_valid_format, key_hash, normalize_key
from .ratelimit import SlidingWindowLimiter
from .status import ACTIVE, EXPIRED, INVALID, MACHINE_LIMIT, REVOKED, UPDATE_REQUIRED, as_utc, compute_status

CONTACT_EMAIL = "betatest.beaver@gmail.com"

MESSAGES = {
    ACTIVE: "Clé BETA active.",
    EXPIRED: f"Votre accès beta a expiré. Contact : {CONTACT_EMAIL}",
    REVOKED: f"Cette clé BETA a été révoquée. Contact : {CONTACT_EMAIL}",
    INVALID: f"Clé BETA inconnue. Contact : {CONTACT_EMAIL}",
    MACHINE_LIMIT: f"Nombre maximal de machines atteint pour cette clé. Contact : {CONTACT_EMAIL}",
    UPDATE_REQUIRED: "Cette version de Beaver n'est plus prise en charge : téléchargez la dernière version.",
}

Platform = Literal["windows", "linux", "macos"]


# ---------------------------------------------------------------------------
# Request schemas (strict; any violation -> HTTP 400)
# ---------------------------------------------------------------------------
def _validate_key(value: str) -> str:
    if len(value) > MAX_RAW_KEY_LENGTH:
        raise ValueError("key too long")
    normalized = normalize_key(value)
    if not is_valid_format(normalized):
        raise ValueError("bad key format")
    return normalized


class ValidateRequest(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=False)

    key: str = Field(max_length=MAX_RAW_KEY_LENGTH)
    machine_id: str = Field(pattern=r"^[0-9a-fA-F]{64}$")
    nonce: str = Field(min_length=16, max_length=64)
    app_version: str = Field(min_length=1, max_length=32, pattern=r"^[0-9A-Za-z.+_-]+$")
    platform: Platform
    model_key_id: str = Field(pattern=MODEL_KEY_ID_RE.pattern)

    check_key = field_validator("key")(_validate_key)

    @field_validator("nonce")
    @classmethod
    def _nonce(cls, value: str) -> str:
        try:
            raw = b64url_decode(value)
        except ValueError as exc:
            raise ValueError("nonce must be base64url") from exc
        if not 16 <= len(raw) <= 32:
            raise ValueError("nonce must be 16 to 32 bytes")
        return value


class KeyRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    key: str = Field(max_length=MAX_RAW_KEY_LENGTH)
    check_key = field_validator("key")(_validate_key)


class DownloadRequest(KeyRequest):
    platform: Platform


# ---------------------------------------------------------------------------
# Errors mapped to HTTP responses by routes.py
# ---------------------------------------------------------------------------
class RateLimited(Exception):
    def __init__(self, retry_after: int, detail: str = "rate_limited"):
        super().__init__(detail)
        self.retry_after = retry_after
        self.detail = detail


class Denied(Exception):
    def __init__(self, http_status: int, body: dict):
        super().__init__(body)
        self.http_status = http_status
        self.body = body


@dataclass
class FileToServe:
    path: str
    filename: str
    size: int


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------
class BetaLicenseService:
    def __init__(self, db, config: BetaConfig, *, now: Callable[[], datetime] = storage.utcnow,
                 monotonic: Callable[[], float] = time.monotonic):
        self.db = db
        self.config = config
        self.now = now
        self.per_key = SlidingWindowLimiter(config.validate_per_key_per_hour, 3600, monotonic)
        self.web_per_key = SlidingWindowLimiter(config.validate_per_key_per_hour, 3600, monotonic)
        self.ip_failures = SlidingWindowLimiter(config.failures_per_ip, config.failures_window_seconds, monotonic)
        self._monotonic = monotonic
        self._rl_logged: dict = {}

    # ---------------- helpers ----------------
    @property
    def keys(self):
        return self.db[storage.KEYS]

    async def _event(self, type_: str, *, key_id=None, ip=None, details=None) -> None:
        await storage.log_event(self.db, type_, key_id=key_id, ip_truncated=ip, details=details, at=self.now())

    async def _rate_limited(self, wait: int, bucket: str, ip: Optional[str], key_id: Optional[str] = None):
        # Audit once per bucket and window, so that an attack does not flood beta_events.
        last = self._rl_logged.get(bucket)
        mono = self._monotonic()
        if last is None or mono - last > wait:
            self._rl_logged[bucket] = mono
            if len(self._rl_logged) > 10_000:
                self._rl_logged.clear()
            await self._event("rate_limited", key_id=key_id, ip=ip, details={"bucket": bucket.split(":", 1)[0]})
        raise RateLimited(wait)

    async def _check_ip(self, ip: Optional[str]) -> None:
        wait = self.ip_failures.retry_after(ip)
        if wait is not None:
            await self._rate_limited(wait, f"ip:{ip}", ip)

    async def _rate_limit_key(self, limiter: SlidingWindowLimiter, h: str, ip: Optional[str]) -> None:
        wait = limiter.hit(h)
        if wait is not None:
            await self._rate_limited(wait, f"key:{h}", ip)

    async def _lookup(self, normalized: str, ip: Optional[str], limiter: SlidingWindowLimiter) -> Optional[dict]:
        """Rate limits first (no DB access), then lookup by HMAC. Unknown key counts as an IP failure."""
        await self._check_ip(ip)
        h = key_hash(self.config.key_pepper, normalized)
        await self._rate_limit_key(limiter, h, ip)
        key = await self.keys.find_one({"key_hash": h}, {"_id": 0})
        if key is None:
            self.ip_failures.record(ip)
        return key

    def _check_after(self, status: str, expires_at: Optional[datetime], now: datetime) -> int:
        interval = self.config.check_interval_seconds
        if status == ACTIVE and expires_at is not None:
            remaining = int((expires_at - now).total_seconds())
            interval = min(interval, remaining)
        return max(30, interval)

    def _envelope(self, status: str, req: ValidateRequest, now: datetime, key: Optional[dict] = None,
                  model_key: Optional[bytes] = None) -> dict:
        expires_at = as_utc(key.get("expires_at")) if key else None
        payload = {
            "v": 1,
            "status": status,
            "nonce": req.nonce,
            "machine_id": req.machine_id,
            "server_time": iso_utc(now),
            "expires_at": iso_utc(expires_at) if expires_at else None,
            "check_after_seconds": self._check_after(status, expires_at, now),
            "model_key_id": req.model_key_id,
            "message": MESSAGES[status],
        }
        if status == ACTIVE:
            assert model_key is not None
            payload["model_key"] = base64.b64encode(model_key).decode("ascii")
        return sign_envelope(self.config.signing_key, self.config.signing_kid, payload)

    # ---------------- /api/beta/validate ----------------
    async def validate(self, req: ValidateRequest, ip: Optional[str]) -> dict:
        key = await self._lookup(req.key, ip, self.per_key)
        now = self.now()
        if key is None:
            await self._event("validate_denied", ip=ip, details={"status": INVALID})
            return self._envelope(INVALID, req, now)

        status = compute_status(key, now)
        if status != ACTIVE:
            await self._event("validate_denied", key_id=key["id"], ip=ip, details={"status": status})
            return self._envelope(status, req, now, key)

        # Resolved before activation: an outdated binary must not start the 14-day
        # clock nor consume a machine slot.
        model_key = self.config.model_keys.get(req.model_key_id)
        if model_key is None:
            await self._event("validate_denied", key_id=key["id"], ip=ip,
                              details={"status": UPDATE_REQUIRED, "model_key_id": req.model_key_id})
            return self._envelope(UPDATE_REQUIRED, req, now, key)

        if not await self._register_machine(key, req, now, ip):
            await self._event("validate_denied", key_id=key["id"], ip=ip, details={"status": MACHINE_LIMIT})
            return self._envelope(MACHINE_LIMIT, req, now, key)

        if key.get("activated_at") is None:
            duration = int(key.get("duration_days") or self.config.duration_days)
            result = await self.keys.update_one(
                {"id": key["id"], "activated_at": None},  # atomic: only the first request wins
                {"$set": {"activated_at": now, "expires_at": now + timedelta(days=duration)}},
            )
            if result.modified_count == 1:
                await self._event("key_activated", key_id=key["id"], ip=ip, details={"platform": req.platform})
            key = await self.keys.find_one({"id": key["id"]}, {"_id": 0})
            status = compute_status(key, now)
            if status != ACTIVE:  # pragma: no cover - revoked in between
                return self._envelope(status, req, now, key)

        await self._event("validate_ok", key_id=key["id"], ip=ip,
                          details={"platform": req.platform, "app_version": req.app_version})
        return self._envelope(ACTIVE, req, now, key, model_key)

    async def _register_machine(self, key: dict, req: ValidateRequest, now: datetime, ip: Optional[str]) -> bool:
        activations = self.db[storage.ACTIVATIONS]
        machine_hash = req.machine_id.lower()
        seen = {"last_seen_at": now, "app_version": req.app_version, "platform": req.platform,
                "last_ip_truncated": ip}
        if await activations.find_one_and_update({"key_id": key["id"], "machine_hash": machine_hash},
                                                 {"$set": seen}):
            return True
        # Reserve a slot atomically (machine_count < max_machines), then insert.
        slot = await self.keys.find_one_and_update(
            {"id": key["id"], "$expr": {"$lt": [{"$ifNull": ["$machine_count", 0]}, "$max_machines"]}},
            {"$inc": {"machine_count": 1}},
        )
        if slot is None:
            return False
        try:
            await activations.insert_one({"id": storage.new_id(), "key_id": key["id"], "machine_hash": machine_hash,
                                          "first_seen_at": now, **seen})
            await self._event("machine_registered", key_id=key["id"], ip=ip, details={"platform": req.platform})
        except DuplicateKeyError:
            # Same machine registered concurrently: give the slot back.
            await self.keys.update_one({"id": key["id"]}, {"$inc": {"machine_count": -1}})
            await activations.update_one({"key_id": key["id"], "machine_hash": machine_hash}, {"$set": seen})
        return True

    # ---------------- web page /beta ----------------
    async def _active_key_or_deny(self, normalized: str, ip: Optional[str], event: str) -> dict:
        key = await self._lookup(normalized, ip, self.web_per_key)
        if key is None:
            await self._event(event, ip=ip, details={"status": INVALID})
            raise Denied(403, {"status": INVALID})
        status = compute_status(key, self.now())
        if status != ACTIVE:
            await self._event(event, key_id=key["id"], ip=ip, details={"status": status})
            raise Denied(403, {"status": status})
        return key

    async def _active_releases(self) -> list:
        releases = {}
        cursor = self.db[storage.RELEASES].find({"is_active": True}, {"_id": 0}).sort("created_at", -1)
        async for rel in cursor:
            releases.setdefault(rel["platform"], rel)
        return [releases[p] for p in ("windows", "macos", "linux") if p in releases]

    async def key_info(self, req: KeyRequest, ip: Optional[str]) -> dict:
        key = await self._active_key_or_deny(req.key, ip, "info_denied")
        now = self.now()
        expires_at = as_utc(key.get("expires_at"))
        days_remaining = None
        if expires_at is not None:
            days_remaining = max(0, math.ceil((expires_at - now).total_seconds() / 86400))
        return {
            "status": ACTIVE,
            "activated": key.get("activated_at") is not None,
            "duration_days": int(key.get("duration_days") or self.config.duration_days),
            "days_remaining": days_remaining,
            "expires_at": iso_utc(expires_at) if expires_at else None,
            "redeem_by": iso_utc(as_utc(key["redeem_by"])) if key.get("redeem_by") else None,
            "downloads_remaining": max(0, int(key.get("max_downloads", 0)) - int(key.get("download_count", 0))),
            "releases": [
                {k: r[k] for k in ("platform", "version", "filename", "sha256", "size")}
                for r in await self._active_releases()
            ],
        }

    # ---------------- /api/beta/download ----------------
    async def issue_download(self, req: DownloadRequest, ip: Optional[str], base_url: str) -> dict:
        key = await self._active_key_or_deny(req.key, ip, "download_denied")
        release = await self.db[storage.RELEASES].find_one(
            {"platform": req.platform, "is_active": True}, {"_id": 0}, sort=[("created_at", -1)]
        )
        if release is None:
            raise Denied(404, {"detail": "no_release"})

        reserved = await self.keys.find_one_and_update(
            {"id": key["id"], "$expr": {"$lt": [{"$ifNull": ["$download_count", 0]}, "$max_downloads"]}},
            {"$inc": {"download_count": 1}},
        )
        if reserved is None:
            await self._event("download_denied", key_id=key["id"], ip=ip, details={"status": "download_limit"})
            raise RateLimited(3600, "download_limit")

        now = self.now()
        ttl = self.config.download_url_ttl_seconds
        expires_at = now + timedelta(seconds=ttl)
        jti = secrets.token_urlsafe(16)
        await self.db[storage.DOWNLOAD_TOKENS].insert_one({
            "jti": jti, "key_id": key["id"], "release_id": release["id"],
            "created_at": now, "expires_at": expires_at, "used": False,
        })
        token = self._make_token(jti, release["id"], expires_at)
        await self._event("download_issued", key_id=key["id"], ip=ip,
                          details={"platform": release["platform"], "version": release["version"]})
        return {
            "url": f"{base_url.rstrip('/')}/api/beta/files/{token}",
            "filename": release["filename"],
            "version": release["version"],
            "sha256": release["sha256"],
            "size": release["size"],
            "expires_in": ttl,
        }

    def _make_token(self, jti: str, release_id: str, expires_at: datetime) -> str:
        body = b64url_encode(json.dumps({"j": jti, "r": release_id, "e": int(expires_at.timestamp())},
                                        separators=(",", ":")).encode())
        mac = hmac.new(self.config.download_token_secret, body.encode("ascii"), hashlib.sha256).digest()
        return f"{body}.{b64url_encode(mac)}"

    def _parse_token(self, token: str) -> dict:
        try:
            body, mac = token.split(".", 1)
            expected = hmac.new(self.config.download_token_secret, body.encode("ascii"), hashlib.sha256).digest()
            if not hmac.compare_digest(expected, b64url_decode(mac)):
                raise ValueError("bad mac")
            data = json.loads(b64url_decode(body))
            return {"jti": str(data["j"]), "release_id": str(data["r"]), "exp": int(data["e"])}
        except (ValueError, KeyError, TypeError, UnicodeError):
            raise Denied(403, {"detail": "invalid_link"}) from None

    async def resolve_download(self, token: str, ip: Optional[str]) -> FileToServe:
        if len(token) > 512:
            raise Denied(403, {"detail": "invalid_link"})
        data = self._parse_token(token)
        now = self.now()
        if now.timestamp() >= data["exp"]:
            raise Denied(410, {"detail": "link_expired"})
        # Single use: atomically flip `used`.
        doc = await self.db[storage.DOWNLOAD_TOKENS].find_one_and_update(
            {"jti": data["jti"], "used": False, "expires_at": {"$gt": now}},
            {"$set": {"used": True, "used_at": now}},
        )
        if doc is None:
            raise Denied(410, {"detail": "link_expired"})
        key = await self.keys.find_one({"id": doc["key_id"]}, {"_id": 0})
        if key is None or compute_status(key, now) != ACTIVE:
            raise Denied(403, {"status": compute_status(key, now) if key else INVALID})
        release = await self.db[storage.RELEASES].find_one({"id": doc["release_id"]}, {"_id": 0})
        if release is None:
            raise Denied(404, {"detail": "no_release"})
        root = os.path.realpath(self.config.releases_dir)
        path = os.path.realpath(os.path.join(root, release["storage_path"]))
        if os.path.commonpath([root, path]) != root or not os.path.isfile(path):
            raise Denied(404, {"detail": "no_release"})
        await self._event("download_served", key_id=key["id"], ip=ip,
                          details={"platform": release["platform"], "version": release["version"]})
        return FileToServe(path=path, filename=release["filename"], size=release["size"])
