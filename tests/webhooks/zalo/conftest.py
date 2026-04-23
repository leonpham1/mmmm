import hashlib
import json

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

import app.api.deps as api_deps
from app.main import app

FAKE_SECRET_KEY = "test_secret_key"
WEBHOOK_URL = "/api/webhooks/zalo"

client = TestClient(app, raise_server_exceptions=False)

@pytest.fixture(autouse=True)
def mock_secret_key():
    with patch.object(api_deps.settings, "ZALO_OA_SECRET_KEY", FAKE_SECRET_KEY):
        yield

def make_payload(event_name: str, extra: dict = {}) -> dict:
    base = {
        "app_id": "834173419644127119",
        "oa_id": "3970966762224483791",
        "user_id": "8309215952164870311",
        "user_id_by_app": "9028998061845239436",
        "event_name": event_name,
        "timestamp": "1636707354448",
    }
    return {**base, **extra}

def make_signature(payload: dict) -> str:
    raw = json.dumps(payload, separators=(",", ":"))
    # digest = sha256(app_id + raw_body + timestamp + secret_key)
    message = payload["app_id"] + raw + payload["timestamp"] + FAKE_SECRET_KEY
    return hashlib.sha256(message.encode()).hexdigest()

def post_webhook(payload: dict, signature: str):
    return client.post(
        WEBHOOK_URL,
        content=json.dumps(payload, separators=(",", ":")),
        headers={
            "Content-Type": "application/json",
            "x-zevent-signature": signature,
        },
    )