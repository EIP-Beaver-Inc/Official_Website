"""Configuration of the BETA license feature, read from environment variables.

Mandatory: BETA_KEY_PEPPER, BETA_SIGNING_PRIVATE_KEY, BETA_SIGNING_KID, BETA_MODEL_KEYS.
If one is missing or malformed, ``load_config`` raises ``ConfigError`` and the
server keeps running with the feature disabled (routes answer 503).
"""
from __future__ import annotations

import base64
import json
import os
import re
from dataclasses import dataclass, field
from typing import Mapping, Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

MODEL_KEY_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


class ConfigError(RuntimeError):
    pass


def b64decode_any(value: str) -> bytes:
    """Decode standard or url-safe base64, padded or not."""
    value = value.strip()
    value += "=" * (-len(value) % 4)
    return base64.b64decode(value.replace("-", "+").replace("_", "/"), validate=True)


def _int(env: Mapping[str, str], name: str, default: int, minimum: int = 0) -> int:
    raw = env.get(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer") from exc
    if value < minimum:
        raise ConfigError(f"{name} must be >= {minimum}")
    return value


@dataclass(frozen=True)
class BetaConfig:
    key_pepper: bytes = field(repr=False)
    signing_key: Ed25519PrivateKey = field(repr=False)
    signing_kid: str
    model_keys: Mapping[str, bytes] = field(repr=False)
    duration_days: int = 14
    redeem_window_days: int = 30
    max_machines: int = 2
    max_downloads: int = 5
    check_interval_seconds: int = 900
    download_url_ttl_seconds: int = 600
    releases_dir: str = "/data/beta-releases"
    public_base_url: Optional[str] = None
    # Rate limits (section 5.4 of the spec)
    validate_per_key_per_hour: int = 60
    failures_per_ip: int = 30
    failures_window_seconds: int = 900

    @property
    def download_token_secret(self) -> bytes:
        """Secret for download tokens, derived from the pepper (no extra env var)."""
        import hashlib
        import hmac

        return hmac.new(self.key_pepper, b"beaver-beta:download-token:v1", hashlib.sha256).digest()


def load_config(env: Optional[Mapping[str, str]] = None) -> BetaConfig:
    env = os.environ if env is None else env

    missing = [
        name
        for name in ("BETA_KEY_PEPPER", "BETA_SIGNING_PRIVATE_KEY", "BETA_SIGNING_KID", "BETA_MODEL_KEYS")
        if not env.get(name, "").strip()
    ]
    if missing:
        raise ConfigError("missing environment variables: " + ", ".join(missing))

    pepper = env["BETA_KEY_PEPPER"].strip().encode("utf-8")
    if len(pepper) < 32:
        raise ConfigError("BETA_KEY_PEPPER must be at least 32 characters")

    try:
        seed = b64decode_any(env["BETA_SIGNING_PRIVATE_KEY"])
    except ValueError as exc:
        raise ConfigError("BETA_SIGNING_PRIVATE_KEY is not valid base64") from exc
    if len(seed) != 32:
        raise ConfigError("BETA_SIGNING_PRIVATE_KEY must be 32 bytes (raw Ed25519 seed, base64)")
    signing_key = Ed25519PrivateKey.from_private_bytes(seed)

    kid = env["BETA_SIGNING_KID"].strip()
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,32}", kid):
        raise ConfigError("BETA_SIGNING_KID must match [A-Za-z0-9._-]{1,32}")

    try:
        raw_keys = json.loads(env["BETA_MODEL_KEYS"])
    except json.JSONDecodeError as exc:
        raise ConfigError("BETA_MODEL_KEYS must be a JSON object") from exc
    if not isinstance(raw_keys, dict) or not raw_keys:
        raise ConfigError("BETA_MODEL_KEYS must be a non-empty JSON object")
    model_keys = {}
    for key_id, value in raw_keys.items():
        if not MODEL_KEY_ID_RE.fullmatch(str(key_id)):
            raise ConfigError(f"BETA_MODEL_KEYS: invalid key id {key_id!r}")
        try:
            decoded = b64decode_any(str(value))
        except ValueError as exc:
            raise ConfigError(f"BETA_MODEL_KEYS[{key_id}] is not valid base64") from exc
        if len(decoded) != 32:
            raise ConfigError(f"BETA_MODEL_KEYS[{key_id}] must decode to 32 bytes")
        model_keys[str(key_id)] = decoded

    base_url = env.get("BETA_PUBLIC_BASE_URL", "").strip().rstrip("/") or None

    return BetaConfig(
        key_pepper=pepper,
        signing_key=signing_key,
        signing_kid=kid,
        model_keys=model_keys,
        duration_days=_int(env, "BETA_DURATION_DAYS", 14, 1),
        redeem_window_days=_int(env, "BETA_REDEEM_WINDOW_DAYS", 30, 1),
        max_machines=_int(env, "BETA_MAX_MACHINES", 2, 1),
        max_downloads=_int(env, "BETA_MAX_DOWNLOADS", 5, 0),
        check_interval_seconds=_int(env, "BETA_CHECK_INTERVAL_SECONDS", 900, 30),
        download_url_ttl_seconds=_int(env, "BETA_DOWNLOAD_URL_TTL_SECONDS", 600, 30),
        releases_dir=env.get("BETA_RELEASES_DIR", "").strip() or "/data/beta-releases",
        public_base_url=base_url,
    )
