import json
from fastapi import Header, Request, HTTPException
import hmac
import hashlib

from app.core.config import settings


def build_zalo_webhook_signature_content(data: dict) -> str:
    """
    Build the string Zalo hashes for x-zevent-signature (before + secret key).

    Spec: sort top-level field names A–Z, append each field's value in that
    order; object/array/null values use compact JSON; primitives follow JS
    string coercion (booleans lower-case, numbers as JSON numbers).
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
    """
    Verify Zalo OA webhook signature.
    """
    # 1. read raw body → parse to dict
    # raw_body retains the original bytes to ensure integrity during hashing.
    raw_body: bytes = await request.body()

    if not raw_body.strip():
        raise HTTPException(status_code=422, detail="Request body is required")
    
    try:
        body: dict = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="Invalid JSON body") from None
    
    if not isinstance(body, dict):
        raise HTTPException(status_code=422, detail="JSON body must be an object")
    
    try:
        body["app_id"]
        body["timestamp"]
    except KeyError as exc:
        missing = exc.args[0]
        raise HTTPException(
            status_code=422, detail=f"Missing required field: {missing}"
        ) from None

    # 2. Zalo: sorted keys (A–Z) → concatenate values → + secret → sha256 hex
    message = (
        build_zalo_webhook_signature_content(body) + settings.ZALO_OA_SECRET_KEY
    )
    digest = hashlib.sha256(message.encode("utf-8")).hexdigest()

    # reject if signature mismatch
    # use compare_digest instead of == to prevent timing attack
    if not hmac.compare_digest(x_zevent_signature, digest):
        raise HTTPException(
            status_code=403, detail="Zalo webhook signature verification failed"
        )
