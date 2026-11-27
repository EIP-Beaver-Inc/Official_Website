"""Tests du serveur du site, sans MongoDB ni SMTP.

`FakeDB` imite les quelques opérations Motor utilisées par orders.py et
server.py ; les mails sont capturés au lieu d'être envoyés.
"""
from __future__ import annotations

import base64
import copy
import os
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))
os.environ.setdefault("MONGO_URL", "mongodb://127.0.0.1:1")
os.environ.setdefault("DB_NAME", "beaver_test")


def _get(doc: dict, dotted: str):
    for part in dotted.split("."):
        if not isinstance(doc, dict) or part not in doc:
            return None
        doc = doc[part]
    return doc


def _set(doc: dict, dotted: str, value) -> None:
    parts = dotted.split(".")
    for part in parts[:-1]:
        doc = doc.setdefault(part, {})
    doc[parts[-1]] = value


class _Cursor:
    def __init__(self, docs: list[dict]):
        self._docs = docs

    def sort(self, key, direction=1):
        self._docs.sort(key=lambda d: (_get(d, key) or ""), reverse=direction < 0)
        return self

    def limit(self, n):
        self._docs = self._docs[:n]
        return self

    async def to_list(self, length=None):
        return self._docs[:length] if length else self._docs


class FakeCollection:
    def __init__(self):
        self.docs: list[dict] = []

    @staticmethod
    def _match(doc: dict, query: dict) -> bool:
        return all(_get(doc, k) == v for k, v in (query or {}).items())

    @staticmethod
    def _project(doc: dict) -> dict:
        out = copy.deepcopy(doc)
        out.pop("_id", None)
        return out

    async def insert_one(self, doc: dict):
        doc["_id"] = len(self.docs) + 1                # Motor adds _id to the inserted dict
        self.docs.append(copy.deepcopy(doc))

    async def find_one(self, query: dict, projection=None, sort=None):
        found = [d for d in self.docs if self._match(d, query)]
        if sort:
            key, direction = sort[0]
            found.sort(key=lambda d: _get(d, key) or "", reverse=direction < 0)
        return self._project(found[0]) if found else None

    def find(self, query=None, projection=None):
        return _Cursor([self._project(d) for d in self.docs if self._match(d, query or {})])

    async def update_one(self, query: dict, update: dict):
        for d in self.docs:
            if self._match(d, query):
                for k, v in update.get("$set", {}).items():
                    _set(d, k, v)
                for k, v in update.get("$inc", {}).items():
                    _set(d, k, (_get(d, k) or 0) + v)
                for k in update.get("$unset", {}):
                    d.pop(k, None)
                return

    async def delete_one(self, query: dict):
        self.docs = [d for d in self.docs if not self._match(d, query)]


class FakeDB:
    def __init__(self):
        self._collections: dict[str, FakeCollection] = {}

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        return self._collections.setdefault(name, FakeCollection())

    __getitem__ = __getattr__


@pytest.fixture
def signing_key(monkeypatch):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    key = Ed25519PrivateKey.generate()
    raw = key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                            serialization.NoEncryption())
    monkeypatch.setenv("LICENCE_PRIVATE_KEY", base64.b64encode(raw).decode())
    return key


@pytest.fixture
def mails(monkeypatch):
    sent: list[dict] = []

    async def capture(to, subject, greeting, paragraphs, code_blocks=(), button=None, closing=None, buttons=()):
        buttons = ([button] if button else []) + list(buttons)
        sent.append({"to": to, "subject": subject, "paragraphs": paragraphs,
                     "code_blocks": list(code_blocks), "buttons": buttons,
                     "button": buttons[0] if buttons else None, "closing": closing or []})
        return "sent"

    async def notify(_doc):
        return "sent"

    import orders
    import server
    monkeypatch.setattr(orders, "send_customer_email", capture)
    monkeypatch.setattr(server, "notify_demo_request", notify)
    monkeypatch.setattr(server, "notify_contact", notify)
    return sent


@pytest.fixture
def app_client(monkeypatch, tmp_path, signing_key, mails):
    from fastapi.testclient import TestClient

    import server
    db = FakeDB()
    monkeypatch.setattr(server, "db", db)
    # The orders router captured server.db when it was built: rebuild the app's routes on the fake.
    from fastapi import APIRouter, FastAPI

    import orders
    app = FastAPI()
    router = APIRouter(prefix="/api")
    for route in server.api_router.routes:
        if not route.path.startswith(("/api/admin/requests", "/api/admin/releases", "/api/admin/licences",
                                      "/api/beta/download", "/api/beta/licence", "/api/download")):
            router.routes.append(route)
    router.include_router(orders.build_router(db, server.require_admin, server._get_client))
    app.include_router(router)

    releases = tmp_path / "releases"
    releases.mkdir()
    monkeypatch.setenv("RELEASES_DIR", str(releases))
    monkeypatch.setenv("SITE_URL", "https://site.test")
    monkeypatch.setenv("ADMIN_TOKEN", "admin-secret")
    monkeypatch.setenv("FORM_RATE_LIMIT", "0")
    monkeypatch.setattr(server, "FORM_RATE_LIMIT", 0)
    client = TestClient(app)
    client.db = db
    client.releases = releases
    client.admin = {"X-Admin-Token": "admin-secret"}
    return client
