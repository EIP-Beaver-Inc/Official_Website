"""Admin operations (used by the CLI; there is no public admin API)."""
from __future__ import annotations

import hashlib
import os
import re
from datetime import datetime, timedelta
from typing import List, Optional

from pymongo.errors import DuplicateKeyError

from . import storage
from .config import BetaConfig
from .keys import generate_key, key_hash, key_hint
from .status import as_utc, compute_status

PLATFORMS = ("windows", "linux", "macos")


class AdminError(RuntimeError):
    pass


async def create_keys(db, config: BetaConfig, *, label: str, count: int = 1, days: Optional[int] = None,
                      max_machines: Optional[int] = None, max_downloads: Optional[int] = None,
                      redeem_days: Optional[int] = None, now: Optional[datetime] = None) -> List[dict]:
    """Create keys. Returns [{"key": plaintext, ...}]: the ONLY time the plaintext exists."""
    if count < 1 or count > 500:
        raise AdminError("count must be between 1 and 500")
    now = now or storage.utcnow()
    created = []
    for _ in range(count):
        for _attempt in range(5):
            plaintext = generate_key()
            doc = {
                "id": storage.new_id(),
                "key_hash": key_hash(config.key_pepper, plaintext),
                "key_hint": key_hint(plaintext),
                "label": label,
                "revoked": False,
                "revoked_at": None,
                "revoke_reason": None,
                "created_at": now,
                "redeem_by": now + timedelta(days=redeem_days or config.redeem_window_days),
                "activated_at": None,
                "expires_at": None,
                "duration_days": days or config.duration_days,
                "max_machines": max_machines or config.max_machines,
                "max_downloads": config.max_downloads if max_downloads is None else max_downloads,
                "download_count": 0,
                "machine_count": 0,
            }
            try:
                await db[storage.KEYS].insert_one(dict(doc))
                break
            except DuplicateKeyError:  # pragma: no cover - 80-bit collision
                continue
        else:  # pragma: no cover
            raise AdminError("could not generate a unique key")
        await storage.log_event(db, "key_created", key_id=doc["id"], at=now, details={"label": label[:80]})
        public = ("id", "key_hint", "label", "redeem_by", "duration_days", "max_machines")
        created.append({"key": plaintext, **{k: doc[k] for k in public}})
    return created


async def find_key(db, ident: str) -> dict:
    """Find a key by full id, id prefix (>= 6 chars) or hint (4 chars)."""
    ident = ident.strip()
    col = db[storage.KEYS]
    doc = await col.find_one({"id": ident}, {"_id": 0})
    if doc:
        return doc
    if len(ident) == 4:
        matches = await col.find({"key_hint": ident.upper()}, {"_id": 0}).to_list(length=10)
    elif len(ident) >= 6:
        matches = await col.find({"id": {"$regex": "^" + re.escape(ident)}}, {"_id": 0}).to_list(length=10)
    else:
        matches = []
    if not matches:
        raise AdminError(f"no key matches {ident!r}")
    if len(matches) > 1:
        raise AdminError(f"{ident!r} is ambiguous ({len(matches)} keys); use the full id")
    return matches[0]


async def list_keys(db, now: Optional[datetime] = None) -> List[dict]:
    now = now or storage.utcnow()
    rows = []
    async for k in db[storage.KEYS].find({}, {"_id": 0, "key_hash": 0}).sort("created_at", -1):
        last = await db[storage.ACTIVATIONS].find_one({"key_id": k["id"]}, sort=[("last_seen_at", -1)])
        rows.append({**k, "status": compute_status(k, now),
                     "machines": await db[storage.ACTIVATIONS].count_documents({"key_id": k["id"]}),
                     "last_seen_at": last["last_seen_at"] if last else None})
    return rows


async def show_key(db, ident: str, now: Optional[datetime] = None) -> dict:
    now = now or storage.utcnow()
    k = await find_key(db, ident)
    k.pop("key_hash", None)
    machines = await db[storage.ACTIVATIONS].find({"key_id": k["id"]}, {"_id": 0}).sort(
        "first_seen_at", 1).to_list(length=100)
    events = await db[storage.EVENTS].find({"key_id": k["id"]}, {"_id": 0}).sort("at", -1).to_list(length=20)
    return {"key": {**k, "status": compute_status(k, now)}, "machines": machines, "events": events}


async def revoke_key(db, ident: str, reason: Optional[str] = None) -> dict:
    k = await find_key(db, ident)
    now = storage.utcnow()
    await db[storage.KEYS].update_one({"id": k["id"]}, {"$set": {"revoked": True, "revoked_at": now,
                                                                 "revoke_reason": reason}})
    await storage.log_event(db, "key_revoked", key_id=k["id"], details={"reason": (reason or "")[:200]})
    return await find_key(db, k["id"])


async def extend_key(db, ident: str, days: int) -> dict:
    """Activated key: expires_at += days. Never activated: redeem_by += days."""
    if days == 0 or abs(days) > 3650:
        raise AdminError("days must be non-zero and reasonable")
    k = await find_key(db, ident)
    field = "expires_at" if k.get("activated_at") else "redeem_by"
    new_value = as_utc(k[field]) + timedelta(days=days)
    await db[storage.KEYS].update_one({"id": k["id"]}, {"$set": {field: new_value}})
    await storage.log_event(db, "key_extended", key_id=k["id"], details={"field": field, "days": days})
    return await find_key(db, k["id"])


async def reset_machines(db, ident: str) -> int:
    k = await find_key(db, ident)
    result = await db[storage.ACTIVATIONS].delete_many({"key_id": k["id"]})
    await db[storage.KEYS].update_one({"id": k["id"]}, {"$set": {"machine_count": 0}})
    await storage.log_event(db, "machines_reset", key_id=k["id"], details={"removed": result.deleted_count})
    return result.deleted_count


def _safe_filename(name: str) -> str:
    name = os.path.basename(name)
    name = re.sub(r"[^A-Za-z0-9._+-]", "_", name).strip("._") or "beaver-beta"
    return name[:120]


async def register_release(db, config: BetaConfig, *, platform: str, version: str, file_path: str) -> dict:
    """Copy the binary into the PRIVATE releases dir, hash it, activate it for its platform."""
    if platform not in PLATFORMS:
        raise AdminError(f"platform must be one of {', '.join(PLATFORMS)}")
    if not re.fullmatch(r"[0-9A-Za-z.+_-]{1,32}", version):
        raise AdminError("invalid version")
    if not os.path.isfile(file_path):
        raise AdminError(f"file not found: {file_path}")

    filename = _safe_filename(file_path)
    rel_dir = os.path.join(platform, version)
    dest_dir = os.path.join(config.releases_dir, rel_dir)
    os.makedirs(dest_dir, mode=0o700, exist_ok=True)
    dest = os.path.join(dest_dir, filename)

    digest = hashlib.sha256()
    tmp = dest + ".part"
    with open(file_path, "rb") as src, open(tmp, "wb") as out:
        for chunk in iter(lambda: src.read(1024 * 1024), b""):
            digest.update(chunk)
            out.write(chunk)
    os.chmod(tmp, 0o600)
    os.replace(tmp, dest)

    now = storage.utcnow()
    release = {
        "id": storage.new_id(), "platform": platform, "version": version, "filename": filename,
        "storage_path": os.path.join(rel_dir, filename), "sha256": digest.hexdigest(),
        "size": os.path.getsize(dest), "is_active": False, "created_at": now,
    }
    col = db[storage.RELEASES]
    await col.insert_one(dict(release))
    await col.update_many({"platform": platform, "id": {"$ne": release["id"]}}, {"$set": {"is_active": False}})
    await col.update_one({"id": release["id"]}, {"$set": {"is_active": True}})
    release["is_active"] = True
    await storage.log_event(db, "release_registered", details={"platform": platform, "version": version})
    return release


async def list_releases(db) -> List[dict]:
    return await db[storage.RELEASES].find({}, {"_id": 0}).sort("created_at", -1).to_list(length=200)
