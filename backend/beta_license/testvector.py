"""Shared test vector (spec section 8), deterministic so it can be regenerated and diffed.

THE KEY PAIR BELOW IS FOR TESTS ONLY. NEVER USE IT IN PRODUCTION.
"""
from __future__ import annotations

import base64
import hashlib
import json
from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from .crypto import b64url_encode, iso_utc, private_key_b64, public_key_b64, sign_envelope

TEST_SEED = hashlib.sha256(b"beaver-beta TEST VECTOR - DO NOT USE IN PRODUCTION").digest()
TEST_KID = "test-0000"
TEST_MODEL_KEY = bytes(range(32))


def build_test_vector() -> dict:
    sk = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    machine_id = hashlib.sha256(b"beaver-beta:" + b"00000000000000000000000000000001").hexdigest()
    request = {
        "key": "BETA-TEST-0000-0000-0001",
        "machine_id": machine_id,
        "nonce": b64url_encode(bytes(range(16))),
        "app_version": "1.2.3",
        "platform": "linux",
        "model_key_id": "beta-1",
    }
    server_time = datetime(2026, 11, 21, 10, 0, 0, tzinfo=timezone.utc)
    common = {"v": 1, "nonce": request["nonce"], "machine_id": machine_id, "server_time": iso_utc(server_time),
              "model_key_id": "beta-1"}
    active = {**common, "status": "active", "expires_at": iso_utc(server_time + timedelta(days=14)),
              "check_after_seconds": 900, "model_key": base64.b64encode(TEST_MODEL_KEY).decode(),
              "message": "Clé BETA active."}
    expired = {**common, "status": "expired", "expires_at": iso_utc(server_time - timedelta(days=1)),
               "check_after_seconds": 900,
               "message": "Votre accès beta a expiré. Contact : betatest.beaver@gmail.com"}

    def case(payload):
        env = sign_envelope(sk, TEST_KID, payload)
        return {"payload_json": payload, "envelope": env}

    return {
        "WARNING": "TEST KEY PAIR - NEVER USE IN PRODUCTION",
        "description": (
            "Shared reference for BETA envelope verification (spec 2.3). signature = Ed25519 over the ASCII bytes "
            "of envelope.payload as-is; payload = base64url WITHOUT padding of UTF-8 JSON (decoders must accept "
            "padding too); signature = base64url without padding. Keys are raw 32-byte Ed25519 keys, base64."
        ),
        "test_keypair": {
            "kid": TEST_KID,
            "private_key_seed_b64": private_key_b64(sk),
            "public_key_b64": public_key_b64(sk),
            "public_key_hex": base64.b64decode(public_key_b64(sk)).hex(),
        },
        "test_model_key": {"id": "beta-1", "b64": base64.b64encode(TEST_MODEL_KEY).decode(),
                           "hex": TEST_MODEL_KEY.hex()},
        "request_example": request,
        "responses": {"active": case(active), "expired": case(expired)},
        "negative_cases": {
            "tampered_payload_must_fail": {
                **case(active)["envelope"],
                "payload": case(expired)["envelope"]["payload"],
            },
        },
    }


def dumps(vector: dict) -> str:
    return json.dumps(vector, ensure_ascii=False, indent=2) + "\n"
