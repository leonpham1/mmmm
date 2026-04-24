import hashlib
import hmac
import json

from fastapi import Header, HTTPException, Request

from app.core.config import settings


def build_zalo_webhook_signature_content(data: dict) -> str:
    """
    Build the string Zalo hashes for x-zevent-signature (before + secret key).

    Spec: sort top-level field names A–Z, append each field's value in that
    order; object/array/null values use compact JSON; primitives follow JS
    string coercion (booleans lower-case, numbers as JSON numbers).

    **Example (realistic Zalo ``user_send_text`` body)**

    Payload (order in JSON does not matter; only sorted keys matter for signing)::

        {
            "app_id": "360846524940903967",
            "sender": {"id": "246845883529197922"},
            "user_id_by_app": "552177279717587730",
            "recipient": {"id": "388613280878808645"},
            "event_name": "user_send_text",
            "message": {
                "text": "message",
                "msg_id": "96d3cdf3af150460909"
            },
            "timestamp": "154390853474"
        }

    Sorted top-level keys: ``app_id``, ``event_name``, ``message``, ``recipient``,
    ``sender``, ``timestamp``, ``user_id_by_app``.

    Joined ``content`` (then append OA secret and ``sha256`` hex)::

        360846524940903967user_send_text{"text":"message","msg_id":"96d3cdf3af150460909"}{"id":"388613280878808645"}{"id":"246845883529197922"}154390853474552177279717587730
    """
    parts: list[str] = []
    for key in sorted(data.keys()):
        value = data[key]
        if isinstance(value, bool):
            parts.append("true" if value else "false")
        elif isinstance(value, (dict, list)) or value is None:
            parts.append(
                json.dumps(value, separators=(",", ":"), ensure_ascii=False)
            )
        elif isinstance(value, (int, float)):
            parts.append(json.dumps(value))
        else:
            parts.append(str(value))
    return "".join(parts)


async def verify_zalo_webhook_signature(
    request: Request,
    x_zevent_signature: str = Header(
        ...,
        alias="x-zevent-signature",
        description=(
            "Security header used by the Zalo Platform to authenticate and "
            "verify the integrity of webhook notifications. Ensures the data "
            "comes from Zalo and has not been tampered with. "
            "Per Zalo docs: sort body keys A–Z, concatenate values "
            "(JSON.stringify for objects/arrays), then "
            "sha256hex(content + OA secret key)."
        ),
    ),
) -> None:
    """Verify Zalo OA webhook signature (x-zevent-signature)."""
    raw_body: bytes = await request.body()

    try:
        body = json.loads(raw_body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(status_code=422, detail="Invalid JSON body") from None

    try:
        _ = body["app_id"], body["timestamp"]
    except (KeyError, TypeError) as exc:
        if isinstance(exc, KeyError):
            raise HTTPException(
                status_code=422,
                detail=f"Missing required field: {exc.args[0]}",
            ) from None
        raise HTTPException(
            status_code=422, detail="JSON body must be an object"
        ) from None

    message = (
        build_zalo_webhook_signature_content(body) + settings.ZALO_OA_SECRET_KEY
    )
    digest = hashlib.sha256(message.encode("utf-8")).hexdigest()

    if not hmac.compare_digest(x_zevent_signature, digest):
        raise HTTPException(
            status_code=403, detail="Zalo webhook signature verification failed"
        )
