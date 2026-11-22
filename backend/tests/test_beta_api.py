"""End-to-end tests (HTTP + real MongoDB) for the BETA license feature.

Needs a MongoDB: MONGO_TEST_URL=mongodb://localhost:27017 pytest backend/tests
(skipped otherwise). Each test uses its own throw-away database.
"""
import asyncio
import base64
import hashlib
import json
import logging
import os
import uuid

import httpx
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from fastapi import FastAPI

from beta_license import admin, routes, storage
from beta_license.crypto import b64url_encode, public_key_b64, verify_envelope
from beta_license.service import BetaLicenseService
from conftest import MODEL_KEY

MONGO_URL = os.environ.get("MONGO_TEST_URL")
pytestmark = pytest.mark.skipif(not MONGO_URL, reason="MONGO_TEST_URL not set")


class Env:
    def __init__(self, db, config, clock):
        self.db, self.config, self.clock = db, config, clock
        self.service = BetaLicenseService(db, config, now=clock.now, monotonic=clock.monotonic)
        app = FastAPI()
        app.include_router(routes.router)
        app.state.beta_service = self.service
        self.app = routes.ScopedCORSMiddleware(app, origins=["https://beaver-website.fr"])
        self.http = httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app), base_url="https://testserver")
        self.public_key = Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key_b64(config.signing_key)))

    async def new_key(self, **kw):
        return (await admin.create_keys(self.db, self.config, label="Test User", now=self.clock.now(), **kw))[0]["key"]

    async def validate(self, key, machine="m1", nonce=None, model_key_id="beta-1", ip="203.0.113.10", **extra):
        body = {"key": key, "machine_id": hashlib.sha256(f"beaver-beta:{machine}".encode()).hexdigest(),
                "nonce": nonce or b64url_encode(os.urandom(16)), "app_version": "1.0.0", "platform": "linux",
                "model_key_id": model_key_id, **extra}
        r = await self.http.post("/api/beta/validate", json=body, headers={"x-forwarded-for": ip})
        payload = verify_envelope(self.public_key, r.json()) if r.status_code == 200 else None
        return r, payload, body


def run(scenario):
    """Run ``scenario(env)`` against a fresh database (sync test, no pytest-asyncio needed)."""
    def wrapper(config, clock):
        async def main():
            from motor.motor_asyncio import AsyncIOMotorClient

            client = AsyncIOMotorClient(MONGO_URL)
            db = client[f"beta_test_{uuid.uuid4().hex[:12]}"]
            try:
                await storage.ensure_indexes(db)
                env = Env(db, config, clock)
                async with env.http:
                    await scenario(env)
            finally:
                await client.drop_database(db.name)
                client.close()
        asyncio.run(main())
    wrapper.__name__ = scenario.__name__
    return wrapper


# ------------------------------------------------------------------ validate
@run
async def test_first_validation_activates_and_returns_signed_model_key(env):
    key = await env.new_key()
    r, p, body = await env.validate(key)
    assert r.status_code == 200 and r.json()["kid"] == "test-kid"
    assert p["status"] == "active" and p["v"] == 1
    assert p["nonce"] == body["nonce"] and p["machine_id"] == body["machine_id"]
    assert base64.b64decode(p["model_key"]) == MODEL_KEY
    assert p["server_time"] == "2026-11-21T10:00:00Z" and p["expires_at"] == "2026-12-05T10:00:00Z"
    assert p["check_after_seconds"] == 900
    doc = await env.db[storage.KEYS].find_one({})
    assert doc["activated_at"] is not None and doc["machine_count"] == 1


@run
async def test_check_after_never_exceeds_remaining_time(env):
    key = await env.new_key()
    await env.validate(key)
    env.clock.advance(14 * 86400 - 100)
    _, p, _ = await env.validate(key)
    assert p["status"] == "active" and p["check_after_seconds"] == 100
    env.clock.advance(90)
    _, p, _ = await env.validate(key)
    assert p["check_after_seconds"] == 30  # floor
    env.clock.advance(10)
    _, p, _ = await env.validate(key)
    assert p["status"] == "expired" and "model_key" not in p


@run
async def test_concurrent_first_activation_sets_activated_at_once(env):
    key = await env.new_key(max_machines=50)
    results = await asyncio.gather(*[env.validate(key, machine=f"m{i % 3}") for i in range(20)])
    assert {p["expires_at"] for _, p, _ in results} == {"2026-12-05T10:00:00Z"}
    assert await env.db[storage.EVENTS].count_documents({"type": "key_activated"}) == 1
    assert await env.db[storage.ACTIVATIONS].count_documents({}) == 3
    assert (await env.db[storage.KEYS].find_one({}))["machine_count"] == 3


@run
async def test_machine_limit(env):
    key = await env.new_key()
    assert (await env.validate(key, "m1"))[1]["status"] == "active"
    assert (await env.validate(key, "m2"))[1]["status"] == "active"
    _, p, _ = await env.validate(key, "m3")
    assert p["status"] == "machine_limit" and "model_key" not in p
    assert (await env.validate(key, "m1"))[1]["status"] == "active"  # known machine still accepted
    k = await env.db[storage.KEYS].find_one({})
    assert await admin.reset_machines(env.db, k["id"]) == 2
    assert (await env.validate(key, "m3"))[1]["status"] == "active"


@run
async def test_concurrent_new_machines_respect_limit(env):
    key = await env.new_key()
    results = await asyncio.gather(*[env.validate(key, machine=f"m{i}") for i in range(8)])
    statuses = sorted(p["status"] for _, p, _ in results)
    assert statuses.count("active") == 2 and statuses.count("machine_limit") == 6
    assert await env.db[storage.ACTIVATIONS].count_documents({}) == 2


@run
async def test_unknown_model_key_id_requires_update_without_activating(env):
    key = await env.new_key()
    _, p, _ = await env.validate(key, model_key_id="beta-0")
    assert p["status"] == "update_required" and "model_key" not in p
    doc = await env.db[storage.KEYS].find_one({})
    assert doc["activated_at"] is None and doc["machine_count"] == 0


@run
async def test_invalid_expired_revoked_never_get_model_key(env):
    _, p, _ = await env.validate("BETA-0000-0000-0000-0000")
    assert p["status"] == "invalid" and "model_key" not in p and p["expires_at"] is None

    stale = await env.new_key(redeem_days=1)
    env.clock.advance(86401)
    assert (await env.validate(stale))[1]["status"] == "expired"

    key = await env.new_key()
    await env.validate(key)
    doc = await env.db[storage.KEYS].find_one({"activated_at": {"$ne": None}})
    await admin.revoke_key(env.db, doc["id"], "test")
    _, p, _ = await env.validate(key)
    assert p["status"] == "revoked" and "model_key" not in p


@run
async def test_extend(env):
    key = await env.new_key()
    await env.validate(key)
    doc = await env.db[storage.KEYS].find_one({})
    await admin.extend_key(env.db, doc["id"], 3)
    _, p, _ = await env.validate(key)
    assert p["expires_at"] == "2026-12-08T10:00:00Z"


@pytest.mark.parametrize("mutation", [
    {"key": "ABCD-EFGH-JKMN-PQRS"}, {"machine_id": "abc"}, {"nonce": "short"}, {"platform": "android"},
])
def test_malformed_requests_get_400(config, clock, mutation):
    @run
    async def scenario(env):
        fields = {"key": "BETA-0000-0000-0000-0000", **mutation}
        r, _, _ = await env.validate(fields.pop("key"), **fields)
        assert r.status_code == 400
        r = await env.http.post("/api/beta/validate", content=b"{not json", headers={"content-type": "application/json"})
        assert r.status_code == 400
        r = await env.http.post("/api/beta/validate", content=b"x" * 5000)
        assert r.status_code == 400
    scenario(config, clock)


@run
async def test_rate_limit_per_key(env):
    key = await env.new_key()
    for i in range(60):
        r, _, _ = await env.validate(key, ip=f"198.51.{i}.1")
        assert r.status_code == 200
    r, _, _ = await env.validate(key, ip="192.0.2.1")
    assert r.status_code == 429 and int(r.headers["retry-after"]) > 0
    env.clock.advance(3600)
    assert (await env.validate(key))[0].status_code == 200
    assert await env.db[storage.EVENTS].count_documents({"type": "rate_limited"}) == 1


@run
async def test_rate_limit_invalid_keys_per_ip(env):
    for i in range(30):
        r, p, _ = await env.validate(f"BETA-0000-0000-0000-{i:04d}", ip="203.0.113.5")
        assert p["status"] == "invalid"
    r, _, _ = await env.validate("BETA-0000-0000-0001-0000", ip="203.0.113.99")  # same /24
    assert r.status_code == 429 and "retry-after" in r.headers
    key = await env.new_key()
    assert (await env.validate(key, ip="198.51.100.1"))[0].status_code == 200  # other IPs unaffected


# ------------------------------------------------------------------ secrets never stored / logged
@run
async def test_plaintext_keys_and_model_key_never_in_db_or_logs(env):
    records = []
    handler = logging.Handler()
    handler.emit = lambda rec: records.append(rec.getMessage())
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.DEBUG)
    try:
        key = await env.new_key()
        await env.validate(key)
        await env.validate("BETA-0000-0000-0000-0000")
        await env.http.post("/api/beta/key-info", json={"key": key})
    finally:
        logging.getLogger().removeHandler(handler)
    dump = ""
    for name in await env.db.list_collection_names():
        dump += json.dumps(await env.db[name].find({}, {"_id": 0}).to_list(length=None), default=str)
    model_b64 = base64.b64encode(MODEL_KEY).decode()
    for secret in (key, key.replace("-", ""), model_b64, env.config.key_pepper.decode()):
        assert secret not in dump
        assert not any(secret in m for m in records)


# ------------------------------------------------------------------ download
async def _release(env, tmp_dir, platform="linux", content=b"BEAVER-BINARY" * 1000):
    src = os.path.join(tmp_dir, "Beaver beta.zip")
    with open(src, "wb") as fh:
        fh.write(content)
    return await admin.register_release(env.db, env.config, platform=platform, version="1.2.3", file_path=src)


def test_download_flow(config, clock, tmp_path):
    @run
    async def scenario(env):
        key = await env.new_key(max_downloads=2)
        r = await env.http.post("/api/beta/download", json={"key": key, "platform": "linux"})
        assert r.status_code == 404  # no release yet

        content = b"BEAVER-BINARY" * 1000
        rel = await _release(env, str(tmp_path), content=content)
        assert rel["sha256"] == hashlib.sha256(content).hexdigest() and rel["filename"] == "Beaver_beta.zip"
        assert not os.path.abspath(config.releases_dir).startswith(os.path.abspath("public"))

        info = (await env.http.post("/api/beta/key-info", json={"key": key})).json()
        assert info["activated"] is False and info["days_remaining"] is None and info["duration_days"] == 14
        assert info["releases"][0]["sha256"] == rel["sha256"] and info["downloads_remaining"] == 2

        r = await env.http.post("/api/beta/download", json={"key": key, "platform": "linux"})
        d = r.json()
        assert r.status_code == 200 and d["expires_in"] == 600 and d["size"] == len(content)
        assert d["url"].startswith("https://testserver/api/beta/files/")
        path = d["url"].replace("https://testserver", "")
        f = await env.http.get(path)
        assert f.status_code == 200 and hashlib.sha256(f.content).hexdigest() == d["sha256"]
        assert "attachment" in f.headers["content-disposition"]
        assert (await env.http.get(path)).status_code == 410  # single use

        d2 = (await env.http.post("/api/beta/download", json={"key": key, "platform": "linux"})).json()
        env.clock.advance(601)
        assert (await env.http.get(d2["url"].replace("https://testserver", ""))).status_code == 410  # expired
        tampered = path[:-3] + ("AAA" if not path.endswith("AAA") else "BBB")
        assert (await env.http.get(tampered)).status_code in (403, 410)

        r = await env.http.post("/api/beta/download", json={"key": key, "platform": "linux"})
        assert r.status_code == 429  # max_downloads=2 reached

        bad = await env.http.post("/api/beta/download", json={"key": "BETA-0000-0000-0000-0000", "platform": "linux"})
        assert bad.status_code == 403 and bad.json() == {"status": "invalid"}
    scenario(config, clock)


def test_download_refused_for_expired_and_revoked(config, clock, tmp_path):
    @run
    async def scenario(env):
        await _release(env, str(tmp_path))
        key = await env.new_key()
        await env.validate(key)
        issued = (await env.http.post("/api/beta/download", json={"key": key, "platform": "linux"})).json()
        doc = await env.db[storage.KEYS].find_one({})
        await admin.revoke_key(env.db, doc["id"])
        r = await env.http.post("/api/beta/download", json={"key": key, "platform": "linux"})
        assert r.status_code == 403 and r.json() == {"status": "revoked"}
        assert (await env.http.get(issued["url"].replace("https://testserver", ""))).status_code == 403

        key2 = await env.new_key()
        await env.validate(key2)
        env.clock.advance(15 * 86400)
        r = await env.http.post("/api/beta/download", json={"key": key2, "platform": "linux"})
        assert r.status_code == 403 and r.json() == {"status": "expired"}
    scenario(config, clock)


@run
async def test_key_info_days_remaining(env):
    key = await env.new_key()
    await env.validate(key)
    env.clock.advance(3 * 86400 + 60)
    info = (await env.http.post("/api/beta/key-info", json={"key": key})).json()
    assert info["activated"] is True and info["days_remaining"] == 11


# ------------------------------------------------------------------ CORS scoping / disabled feature
@run
async def test_cors_scoping(env):
    origin = {"origin": "https://evil.example", "access-control-request-method": "POST"}
    r = await env.http.options("/api/beta/validate", headers=origin)
    assert "access-control-allow-origin" not in r.headers
    site = {"origin": "https://beaver-website.fr", "access-control-request-method": "POST"}
    r = await env.http.options("/api/beta/validate", headers=site)
    assert "access-control-allow-origin" not in r.headers  # native-only route
    r = await env.http.options("/api/beta/key-info", headers=site)
    assert r.headers.get("access-control-allow-origin") == "https://beaver-website.fr"
    r = await env.http.options("/api/beta/key-info", headers=origin)
    assert r.headers.get("access-control-allow-origin") != "https://evil.example"


def test_feature_disabled_returns_503():
    async def main():
        app = FastAPI()
        app.include_router(routes.router)
        app.state.beta_service = None
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
            assert (await c.post("/api/beta/validate", json={})).status_code == 503
    asyncio.run(main())


# ------------------------------------------------------------------ CLI
def test_cli_create_shows_plaintext_once(config, clock, capsys, monkeypatch, tmp_path):
    from beta_license import cli
    from conftest import make_env

    db_name = f"beta_test_{uuid.uuid4().hex[:12]}"
    for k, v in {**make_env(tmp_path), "MONGO_URL": MONGO_URL, "DB_NAME": db_name}.items():
        monkeypatch.setenv(k, v)
    try:
        cli.main(["beta-keys", "create", "--label", "Jane Doe", "--count", "2", "--csv", str(tmp_path / "k.csv")])
        out = capsys.readouterr().out
        keys = [w for w in out.split() if w.startswith("BETA-")]
        assert len(keys) == 2 and "ONLY NOW" in out
        assert oct(os.stat(tmp_path / "k.csv").st_mode & 0o777) == "0o600"
        cli.main(["beta-keys", "list"])
        listing = capsys.readouterr().out
        assert "Jane Doe" in listing and not any(k in listing for k in keys)
        assert keys[0][-4:] in listing
        hint = keys[0][-4:]
        cli.main(["beta-keys", "show", hint])
        assert "key_created" in capsys.readouterr().out
    finally:
        from pymongo import MongoClient

        MongoClient(MONGO_URL).drop_database(db_name)
