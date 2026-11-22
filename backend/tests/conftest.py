import base64
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from beta_license.config import load_config  # noqa: E402
from beta_license.crypto import generate_signing_key, private_key_b64  # noqa: E402

MODEL_KEY = bytes(range(100, 132))


class Clock:
    """Controls both wall-clock time (key status) and monotonic time (rate limits)."""

    def __init__(self, start=datetime(2026, 11, 21, 10, 0, 0, tzinfo=timezone.utc)):
        self.t = start
        self.mono = 1000.0

    def now(self):
        return self.t

    def monotonic(self):
        return self.mono

    def advance(self, seconds):
        self.t += timedelta(seconds=seconds)
        self.mono += seconds


def make_env(tmp_path=None, **overrides):
    sk = generate_signing_key()
    env = {
        "BETA_KEY_PEPPER": "p" * 40,
        "BETA_SIGNING_PRIVATE_KEY": private_key_b64(sk),
        "BETA_SIGNING_KID": "test-kid",
        "BETA_MODEL_KEYS": json.dumps({"beta-1": base64.b64encode(MODEL_KEY).decode()}),
        "BETA_RELEASES_DIR": str(tmp_path) if tmp_path else "/nonexistent",
    }
    env.update(overrides)
    return env


@pytest.fixture
def config(tmp_path):
    return load_config(make_env(tmp_path / "releases"))


@pytest.fixture
def clock():
    return Clock()
