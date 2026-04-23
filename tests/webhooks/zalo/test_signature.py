import hashlib

from app.api.deps.zalo_webhook_deps import build_zalo_webhook_signature_content
from tests.webhooks.zalo.conftest import (
    client,
    make_payload,
    make_signature,
    post_webhook,
    WEBHOOK_URL,
)

class TestHackerAttacks:
    def test_wrong_signature_returns_403(self):
        payload = make_payload("user_send_text", {"message": {"text": "Hello"}})
        response = post_webhook(payload, "deadbeefdeadbeef")
        assert response.status_code == 403

    def test_tampered_app_id_returns_403(self):
        # Sign before → tamper after → signature no longer matches
        payload = make_payload("user_send_text", {"message": {"text": "Hello"}})
        signature = make_signature(payload)
        payload["app_id"] = "999999999999999999"
        response = post_webhook(payload, signature)
        assert response.status_code == 403

    def test_tampered_timestamp_returns_403(self):
        payload = make_payload("user_send_text", {"message": {"text": "Hello"}})
        signature = make_signature(payload)
        payload["timestamp"] = "0000000000000"
        response = post_webhook(payload, signature)
        assert response.status_code == 403

    def test_tampered_body_content_returns_403(self):
        payload = make_payload("user_send_text", {"message": {"text": "Hello"}})
        signature = make_signature(payload)
        payload["user_id"] = "hacked_user_id"
        response = post_webhook(payload, signature)
        assert response.status_code == 403

    def test_empty_signature_returns_403(self):
        payload = make_payload("user_send_text", {"message": {"text": "Hello"}})
        response = post_webhook(payload, "")
        assert response.status_code == 403

    def test_signature_from_different_secret_returns_403(self):
        payload = make_payload("user_send_text", {"message": {"text": "Hello"}})
        content = build_zalo_webhook_signature_content(payload)
        wrong_sig = hashlib.sha256(
            (content + "wrong_secret").encode("utf-8")
        ).hexdigest()
        response = post_webhook(payload, wrong_sig)
        assert response.status_code == 403

    def test_replayed_signature_with_different_body_returns_403(self):
        # Reuse the old signature for the new body
        original = make_payload("user_send_text", {"message": {"text": "Hello"}})
        signature = make_signature(original)
        tampered = make_payload("user_send_text", {"message": {"text": "Hacked"}})
        response = post_webhook(tampered, signature)
        assert response.status_code == 403

class TestNaiveUserMistakes:
    def test_missing_signature_header_returns_422(self):
        payload = make_payload("user_send_text")
        response = client.post(WEBHOOK_URL, json=payload)
        assert response.status_code == 422

    def test_empty_body_returns_422(self):
        response = client.post(
            WEBHOOK_URL,
            content="",
            headers={"Content-Type": "application/json", "x-zevent-signature": "abc"},
        )
        assert response.status_code == 422

    def test_invalid_json_returns_422(self):
        response = client.post(
            WEBHOOK_URL,
            content="not json",
            headers={"Content-Type": "application/json", "x-zevent-signature": "abc"},
        )
        assert response.status_code == 422

    def test_missing_app_id_returns_422(self):
        payload = make_payload("user_send_text")
        del payload["app_id"]
        response = client.post(
            WEBHOOK_URL,
            json=payload,
            headers={"x-zevent-signature": "abc"},
        )
        assert response.status_code == 422

    def test_missing_timestamp_returns_422(self):
        payload = make_payload("user_send_text")
        del payload["timestamp"]
        response = client.post(
            WEBHOOK_URL,
            json=payload,
            headers={"x-zevent-signature": "abc"},
        )
        assert response.status_code == 422

    def test_get_method_returns_405(self):
        response = client.get(WEBHOOK_URL)
        assert response.status_code == 405

    def test_plain_text_content_type_returns_422(self):
        payload = make_payload("user_send_text")
        signature = make_signature(payload)
        response = client.post(
            WEBHOOK_URL,
            content="some text",
            headers={"Content-Type": "text/plain", "x-zevent-signature": signature},
        )
        assert response.status_code == 422