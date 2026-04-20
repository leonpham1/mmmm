import hashlib
import hmac
import json
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from app.api.endpoints.webhooks.zalo import router

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI()
app.include_router(router)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

APP_ID = "360846524940903967"
OA_SECRET_KEY = "test_secret_key"
WEBHOOK_URL = "/zalo"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def generate_signature(app_id: str, data: str, timestamp: str, secret: str) -> str:
    raw = app_id + data + timestamp + secret
    return hmac.new(secret.encode(), raw.encode(), hashlib.sha256).hexdigest()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def base_payload() -> dict:
    return {
        "app_id": APP_ID,
        "sender": {"id": "246845883529197922"},
        "user_id_by_app": "552177279717587730",
        "recipient": {"id": "388613280878808645"},
        "event_name": "user_send_text",
        "message": {
            "text": "hello",
            "msg_id": "96d3cdf3af150460909"
        },
        "timestamp": "154390853474"
    }


@pytest.fixture
def valid_headers(base_payload: dict) -> dict:
    data = json.dumps(base_payload, separators=(",", ":"), ensure_ascii=False)
    sig = generate_signature(APP_ID, data, base_payload["timestamp"], OA_SECRET_KEY)
    return {
        "Content-Type": "application/json",
        "X-ZEvent-Signature": sig,
    }


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# ---------------------------------------------------------------------------
# 1. Signature Validation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_missing_signature_returns_401(client: AsyncClient, base_payload: dict):
    """
    BEHAVIOR: If X-ZEvent-Signature header is absent, the endpoint must
    reject the request with HTTP 401 Unauthorized.
    """
    # TODO: implement signature validation in handle_zalo_webhook
    response = await client.post(
        WEBHOOK_URL,
        json=base_payload,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_signature_returns_401(client: AsyncClient, base_payload: dict):
    """
    BEHAVIOR: If X-ZEvent-Signature header contains a wrong/tampered MAC,
    the endpoint must reject the request with HTTP 401 Unauthorized.
    """
    # TODO: implement signature validation in handle_zalo_webhook
    response = await client.post(
        WEBHOOK_URL,
        json=base_payload,
        headers={
            "Content-Type": "application/json",
            "X-ZEvent-Signature": "invalidsignature",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_valid_signature_returns_200(client: AsyncClient, base_payload: dict, valid_headers: dict):
    """
    BEHAVIOR: If X-ZEvent-Signature is a correct sha256 MAC of
    (appId + data + timeStamp + OAsecretKey), the endpoint must accept
    the request and return HTTP 200.
    """
    # TODO: implement signature validation in handle_zalo_webhook
    response = await client.post(WEBHOOK_URL, json=base_payload, headers=valid_headers)
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# 2. Payload Validation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.parametrize("missing_field", ["app_id", "sender", "event_name", "timestamp"])
async def test_missing_required_field_returns_422(
    client: AsyncClient, base_payload: dict, valid_headers: dict, missing_field: str
):
    """
    BEHAVIOR: If any required field (app_id, sender, event_name, timestamp)
    is absent from the payload, the endpoint must return HTTP 422 Unprocessable Entity.
    """
    # TODO: add Pydantic request body validation to handle_zalo_webhook
    payload = {k: v for k, v in base_payload.items() if k != missing_field}
    response = await client.post(WEBHOOK_URL, json=payload, headers=valid_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_unknown_event_name_returns_422(
    client: AsyncClient, base_payload: dict, valid_headers: dict
):
    """
    BEHAVIOR: If event_name is not one of the supported Zalo event types,
    the endpoint must return HTTP 422 Unprocessable Entity.
    """
    # TODO: add event_name enum validation in Pydantic schema
    payload = {**base_payload, "event_name": "user_do_something_unknown"}
    response = await client.post(WEBHOOK_URL, json=payload, headers=valid_headers)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# 3. Event Routing
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_user_send_text(client: AsyncClient, base_payload: dict, valid_headers: dict):
    """
    BEHAVIOR: user_send_text event with message.text present must return 200
    and acknowledge the event correctly.
    """
    # TODO: implement routing/handling for user_send_text
    payload = {
        **base_payload,
        "event_name": "user_send_text",
        "message": {"text": "hello world", "msg_id": "abc001"},
    }
    response = await client.post(WEBHOOK_URL, json=payload, headers=valid_headers)
    assert response.status_code == 200
    assert response.json().get("event") == "user_send_text"


@pytest.mark.asyncio
async def test_user_send_image(client: AsyncClient, base_payload: dict, valid_headers: dict):
    """
    BEHAVIOR: user_send_image event must include attachments[0].type == 'image'
    and return 200.
    """
    # TODO: implement routing/handling for user_send_image
    payload = {
        **base_payload,
        "event_name": "user_send_image",
        "message": {"msg_id": "abc002"},
        "attachments": [
            {"type": "image", "payload": {"url": "http://example.com/img.jpg", "thumbnail": "http://example.com/thumb.jpg"}}
        ],
    }
    response = await client.post(WEBHOOK_URL, json=payload, headers=valid_headers)
    assert response.status_code == 200
    assert response.json().get("event") == "user_send_image"


@pytest.mark.asyncio
async def test_user_send_gif(client: AsyncClient, base_payload: dict, valid_headers: dict):
    """
    BEHAVIOR: user_send_gif event must include attachments[0].type == 'gif'
    and return 200.
    """
    # TODO: implement routing/handling for user_send_gif
    payload = {
        **base_payload,
        "event_name": "user_send_gif",
        "message": {"msg_id": "abc003"},
        "attachments": [
            {"type": "gif", "payload": {"url": "http://example.com/anim.gif", "thumbnail": "http://example.com/thumb.jpg"}}
        ],
    }
    response = await client.post(WEBHOOK_URL, json=payload, headers=valid_headers)
    assert response.status_code == 200
    assert response.json().get("event") == "user_send_gif"


@pytest.mark.asyncio
async def test_user_send_link(client: AsyncClient, base_payload: dict, valid_headers: dict):
    """
    BEHAVIOR: user_send_link event must include attachments[0].type == 'link'
    and return 200.
    """
    # TODO: implement routing/handling for user_send_link
    payload = {
        **base_payload,
        "event_name": "user_send_link",
        "message": {"msg_id": "abc004"},
        "attachments": [
            {"type": "link", "payload": {"url": "https://developers.zalo.me/", "description": "Zalo Dev", "thumbnail": ""}}
        ],
    }
    response = await client.post(WEBHOOK_URL, json=payload, headers=valid_headers)
    assert response.status_code == 200
    assert response.json().get("event") == "user_send_link"


@pytest.mark.asyncio
async def test_user_send_audio(client: AsyncClient, base_payload: dict, valid_headers: dict):
    """
    BEHAVIOR: user_send_audio event must include attachments[0].type == 'audio'
    and return 200.
    """
    # TODO: implement routing/handling for user_send_audio
    payload = {
        **base_payload,
        "event_name": "user_send_audio",
        "message": {"msg_id": "abc005"},
        "attachments": [
            {"type": "audio", "payload": {"url": "http://example.com/audio.amr"}}
        ],
    }
    response = await client.post(WEBHOOK_URL, json=payload, headers=valid_headers)
    assert response.status_code == 200
    assert response.json().get("event") == "user_send_audio"


@pytest.mark.asyncio
async def test_user_send_video(client: AsyncClient, base_payload: dict, valid_headers: dict):
    """
    BEHAVIOR: user_send_video event must include attachments[0].type == 'video'
    and return 200.
    """
    # TODO: implement routing/handling for user_send_video
    payload = {
        **base_payload,
        "event_name": "user_send_video",
        "message": {"msg_id": "abc006"},
        "attachments": [
            {"type": "video", "payload": {"url": "https://example.com/video.mp4", "thumbnail": "", "description": ""}}
        ],
    }
    response = await client.post(WEBHOOK_URL, json=payload, headers=valid_headers)
    assert response.status_code == 200
    assert response.json().get("event") == "user_send_video"


@pytest.mark.asyncio
async def test_user_send_sticker(client: AsyncClient, base_payload: dict, valid_headers: dict):
    """
    BEHAVIOR: user_send_sticker event must include attachments[0].type == 'sticker'
    and return 200.
    """
    # TODO: implement routing/handling for user_send_sticker
    payload = {
        **base_payload,
        "event_name": "user_send_sticker",
        "message": {"msg_id": "abc007"},
        "attachments": [
            {"type": "sticker", "payload": {"url": "https://api.zalo.me/sticker.png", "id": "sticker_001"}}
        ],
    }
    response = await client.post(WEBHOOK_URL, json=payload, headers=valid_headers)
    assert response.status_code == 200
    assert response.json().get("event") == "user_send_sticker"


@pytest.mark.asyncio
async def test_user_send_location(client: AsyncClient, base_payload: dict, valid_headers: dict):
    """
    BEHAVIOR: user_send_location event must include attachments[0].type == 'location'
    with coordinates, and return 200.
    """
    # TODO: implement routing/handling for user_send_location
    payload = {
        **base_payload,
        "event_name": "user_send_location",
        "message": {"msg_id": "abc008"},
        "attachments": [
            {"type": "location", "payload": {"coordinates": {"latitude": "10.7642473", "longitude": "106.6564314"}}}
        ],
    }
    response = await client.post(WEBHOOK_URL, json=payload, headers=valid_headers)
    assert response.status_code == 200
    assert response.json().get("event") == "user_send_location"


@pytest.mark.asyncio
async def test_user_send_file(client: AsyncClient, base_payload: dict, valid_headers: dict):
    """
    BEHAVIOR: user_send_file event must include attachments[0].type == 'file'
    with file metadata, and return 200.
    """
    # TODO: implement routing/handling for user_send_file
    payload = {
        **base_payload,
        "event_name": "user_send_file",
        "message": {"msg_id": "abc009"},
        "attachments": [
            {
                "type": "file",
                "payload": {
                    "size": "233947",
                    "name": "developer.docx",
                    "checksum": "db8f0a790d28e3d8658a0ff0846189",
                    "type": "docx",
                    "url": "https://example.com/developer.docx",
                }
            }
        ],
    }
    response = await client.post(WEBHOOK_URL, json=payload, headers=valid_headers)
    assert response.status_code == 200
    assert response.json().get("event") == "user_send_file"
