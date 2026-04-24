import hashlib
import json

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

import app.api.deps.webhooks.zalo_webhook_deps as zalo_webhook_deps
from app.api.deps.webhooks.zalo_webhook_deps import build_zalo_webhook_signature_content
from app.main import app

FAKE_SECRET_KEY = "test_secret_key"
WEBHOOK_URL = "/api/webhooks/zalo"

client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def mock_secret_key():
    with patch.object(
        zalo_webhook_deps.settings, "ZALO_OA_SECRET_KEY", FAKE_SECRET_KEY
    ):
        yield


def make_payload(event_name: str, extra: dict | None = None) -> dict:
    """Build a schema-shaped ``user_send_text`` body for signature tests."""
    payload_extra = {} if extra is None else dict(extra)
    if event_name != "user_send_text":
        raise ValueError(f"make_payload only supports user_send_text, got {event_name!r}")

    message = {"msg_id": "test-msg-id", "text": "hi"}
    if "message" in payload_extra:
        message = {**message, **dict(payload_extra["message"])}

    base: dict = {
        "app_id": "834173419644127119",
        "timestamp": 1636707354448,
        "event_name": "user_send_text",
        "sender": {"id": "8309215952164870311"},
        "recipient": {"id": "3970966762224483791"},
        "message": message,
    }
    for key, value in payload_extra.items():
        if key == "message":
            continue
        base[key] = value
    return base


def make_signature(payload: dict) -> str:
    content = build_zalo_webhook_signature_content(payload)
    message = content + FAKE_SECRET_KEY
    return hashlib.sha256(message.encode("utf-8")).hexdigest()


def post_webhook(payload: dict, signature: str):
    return client.post(
        WEBHOOK_URL,
        content=json.dumps(payload, separators=(",", ":")),
        headers={
            "Content-Type": "application/json",
            "x-zevent-signature": signature,
        },
    )
