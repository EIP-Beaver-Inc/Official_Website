"""Unit tests (no database) for the BETA license feature."""
import base64
import json
import os
import re
from datetime import datetime, timedelta, timezone

import pytest
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from pydantic import ValidationError

from beta_license.config import ConfigError, load_config
from beta_license.crypto import b64url_decode, b64url_encode, sign_envelope, verify_envelope
from beta_license.keys import CROCKFORD_ALPHABET, KEY_RE, generate_key, is_valid_format, key_hash, normalize_key
from beta_license.ratelimit import SlidingWindowLimiter
from beta_license.service import ValidateRequest
from beta_license.status import compute_status
from beta_license.storage import truncate_ip
from beta_license.testvector import build_test_vector, dumps

from conftest import make_env

NOW = datetime(2026, 11, 21, 10, 0, 0, tzinfo=timezone.utc)
SPEC_REGEX = r"^BETA-[0-9A-HJKMNP-TV-Z]{4}(-[0-9A-HJKMNP-TV-Z]{4}){3}$"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ------------------------------------------------------------------ keys
def test_generated_keys_match_spec_regex_and_are_unique():
    keys = {generate_key() for _ in range(2000)}
    assert len(keys) == 2000
    assert KEY_RE.pattern == SPEC_REGEX
    for k in keys:
        assert re.fullmatch(SPEC_REGEX, k)
        assert not set(k[5:].replace("-", "")) & set("ILOU")
    assert set("".join(k[5:].replace("-", "") for k in keys)) == set(CROCKFORD_ALPHABET)


def test_normalization():
    assert normalize_key("  beta-abcd-efgh-jkmn-pqrs \n") == "BETA-ABCD-EFGH-JKMN-PQRS"
    assert normalize_key("beta-ab cd-efgh-jkmn-pqrs") == "BETA-ABCD-EFGH-JKMN-PQRS"
    assert is_valid_format(normalize_key("beta-abcd-efgh-jkmn-pqrs"))
    assert not is_valid_format("BETA-ABCD-EFGH-JKMN-PQRI")  # I excluded
    assert not is_valid_format("ABCD-EFGH-JKMN-PQRS")  # old portal format


def test_key_hash_is_hmac_and_pepper_dependent():
    k = "BETA-ABCD-EFGH-JKMN-PQRS"
    assert key_hash(b"a" * 32, k) != key_hash(b"b" * 32, k)
    assert re.fullmatch(r"[0-9a-f]{64}", key_hash(b"a" * 32, k))
    assert k not in key_hash(b"a" * 32, k)


# ------------------------------------------------------------------ status
def key(**kw):
    base = {"revoked": False, "activated_at": None, "expires_at": None, "redeem_by": NOW + timedelta(days=30)}
    base.update(kw)
    return base


def test_status_active_not_yet_activated():
    assert compute_status(key(), NOW) == "active"


def test_status_redeem_by_boundaries():
    k = key(redeem_by=NOW)
    assert compute_status(k, NOW) == "active"  # now > redeem_by is strict
    assert compute_status(k, NOW + timedelta(seconds=1)) == "expired"


def test_status_expires_at_boundaries():
    k = key(activated_at=NOW - timedelta(days=14), expires_at=NOW, redeem_by=NOW - timedelta(days=1))
    assert compute_status(k, NOW - timedelta(seconds=1)) == "active"
    assert compute_status(k, NOW) == "expired"  # now >= expires_at


def test_status_activated_key_ignores_redeem_by():
    k = key(activated_at=NOW - timedelta(days=2), expires_at=NOW + timedelta(days=12),
            redeem_by=NOW - timedelta(days=1))
    assert compute_status(k, NOW) == "active"


def test_status_revoked_wins():
    k = key(revoked=True, activated_at=NOW, expires_at=NOW + timedelta(days=14))
    assert compute_status(k, NOW) == "revoked"


def test_status_accepts_naive_mongo_datetimes():
    k = key(activated_at=datetime(2026, 11, 20), expires_at=datetime(2026, 11, 21, 10, 0, 0))
    assert compute_status(k, NOW) == "expired"


# ------------------------------------------------------------------ crypto
def test_envelope_sign_verify_and_tamper():
    from beta_license.crypto import generate_signing_key

    sk = generate_signing_key()
    env = sign_envelope(sk, "k1", {"status": "active", "message": "é"})
    assert "=" not in env["payload"] and "=" not in env["signature"]
    assert verify_envelope(sk.public_key(), env) == {"status": "active", "message": "é"}
    forged = dict(env, payload=b64url_encode(json.dumps({"status": "active", "x": 1}).encode()))
    with pytest.raises(InvalidSignature):
        verify_envelope(sk.public_key(), forged)


def test_b64url_strict():
    assert b64url_decode(b64url_encode(b"\xff\xfe" * 9)) == b"\xff\xfe" * 9
    assert b64url_decode("AAA=") == b"\x00\x00"
    for bad in ("", "a+b/", "a b", "é"):
        with pytest.raises(ValueError):
            b64url_decode(bad)


# ------------------------------------------------------------------ config
def test_config_requires_all_mandatory_vars(tmp_path):
    for name in ("BETA_KEY_PEPPER", "BETA_SIGNING_PRIVATE_KEY", "BETA_SIGNING_KID", "BETA_MODEL_KEYS"):
        env = make_env(tmp_path)
        env.pop(name)
        with pytest.raises(ConfigError, match=name):
            load_config(env)


@pytest.mark.parametrize("override", [
    {"BETA_KEY_PEPPER": "short"},
    {"BETA_SIGNING_PRIVATE_KEY": base64.b64encode(b"x" * 16).decode()},
    {"BETA_MODEL_KEYS": '{"beta-1": "AAAA"}'},
    {"BETA_MODEL_KEYS": "[]"},
    {"BETA_MAX_MACHINES": "zero"},
])
def test_config_rejects_bad_values(tmp_path, override):
    with pytest.raises(ConfigError):
        load_config(make_env(tmp_path, **override))


def test_config_defaults_match_spec(config):
    assert (config.duration_days, config.redeem_window_days, config.max_machines, config.max_downloads,
            config.check_interval_seconds, config.download_url_ttl_seconds) == (14, 30, 2, 5, 900, 600)
    assert "p" * 40 not in repr(config)  # secrets hidden from repr


# ------------------------------------------------------------------ request schema
GOOD = {"key": "beta-abcd-efgh-jkmn-pqrs", "machine_id": "a" * 64, "nonce": b64url_encode(b"n" * 16),
        "app_version": "1.2.3", "platform": "linux", "model_key_id": "beta-1"}


def test_validate_request_ok_and_normalizes():
    req = ValidateRequest.model_validate(GOOD)
    assert req.key == "BETA-ABCD-EFGH-JKMN-PQRS"
    assert req.nonce == GOOD["nonce"]


@pytest.mark.parametrize("field,value", [
    ("key", "ABCD-EFGH-JKMN-PQRS"), ("key", "x" * 100), ("machine_id", "a" * 63), ("machine_id", "g" * 64),
    ("nonce", b64url_encode(b"n" * 15)), ("nonce", b64url_encode(b"n" * 33)), ("nonce", "!" * 24),
    ("platform", "android"), ("app_version", ""), ("app_version", "1.2.3; rm"), ("model_key_id", "../x"),
])
def test_validate_request_rejects(field, value):
    with pytest.raises(ValidationError):
        ValidateRequest.model_validate({**GOOD, field: value})


# ------------------------------------------------------------------ misc
def test_rate_limiter_window():
    t = [0.0]
    rl = SlidingWindowLimiter(3, 60, clock=lambda: t[0])
    assert [rl.hit("k") for _ in range(3)] == [None, None, None]
    assert rl.hit("k") == 60
    t[0] = 59.0
    assert rl.hit("k") == 1
    t[0] = 60.0
    assert rl.hit("k") is None
    assert rl.hit("other") is None


def test_truncate_ip():
    assert truncate_ip("203.0.113.77") == "203.0.113.0/24"
    assert truncate_ip("2001:db8:abcd:1234::1") == "2001:db8:abcd::/48"
    assert truncate_ip("::ffff:198.51.100.9") == "198.51.100.0/24"
    assert truncate_ip("garbage") is None and truncate_ip(None) is None


# ------------------------------------------------------------------ shared test vector
def test_test_vector_verifies_and_is_committed():
    vector = build_test_vector()
    pub = Ed25519PublicKey.from_public_bytes(base64.b64decode(vector["test_keypair"]["public_key_b64"]))
    active = verify_envelope(pub, vector["responses"]["active"]["envelope"])
    expired = verify_envelope(pub, vector["responses"]["expired"]["envelope"])
    assert active == vector["responses"]["active"]["payload_json"] and "model_key" in active
    assert expired["status"] == "expired" and "model_key" not in expired
    assert active["nonce"] == vector["request_example"]["nonce"]
    with pytest.raises(InvalidSignature):
        verify_envelope(pub, vector["negative_cases"]["tampered_payload_must_fail"])
    ValidateRequest.model_validate(vector["request_example"])
    with open(os.path.join(REPO_ROOT, "docs", "beta", "test-vector.json"), encoding="utf-8") as fh:
        assert fh.read() == dumps(vector), "regenerate: python -m beta_license.cli beta-crypto test-vector --out ..."
