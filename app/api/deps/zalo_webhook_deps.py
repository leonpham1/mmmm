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
    
    **Example 1 — key order and nested object**

        data = {
            "timestamp": "99",
            "app_id": "111",
            "nested": {"k": 1},
        }
        # Sorted keys: app_id, nested, timestamp
        # Values joined: "111" + '{"k":1}' + "99"  →  '111{"k":1}99'

    **Example 2 — string, bool, number**

        {"z": 3, "a": "hi", "b": True}
        # Sorted keys: a, b, z  →  "hi" + "true" + "3"  →  "hitrue3"
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
    except json.JSONDecodeError:
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
