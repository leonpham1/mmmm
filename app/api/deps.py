import json
from fastapi import Header, Request, HTTPException
import hmac
import hashlib

from app.core.config import settings


async def verify_zalo_webhook_signature(
    request: Request,
    x_zevent_signature: str = Header(
        ...,
        alias="x-zevent-signature",
        description=(
            "Security header used by the Zalo Platform to authenticate and "
            "verify the integrity of webhook notifications. Ensures the data "
            "comes from Zalo and has not been tampered with."
            "Formula: sha256(app_id + data + timestamp + oa_secret_key)"
        ),
    ),
) -> None:
    """
    Verify Zalo OA webhook signature.
    """
    # 1. read raw body → parse to dict
    # raw_body retains the original bytes to ensure integrity during hashing.
    raw_body: bytes = await request.body()
    body: dict = json.loads(raw_body)

    # 2. sha256(x_zevent_signature = app_id + raw_body + timestamp + secret_key)
    # in cryptography, Input is message
    message = (
        f"{body['app_id']}"
        f"{raw_body.decode("utf-8")}"
        f"{body['timestamp']}"
        f"{settings.ZALO_OA_SECRET_KEY}"
    )
    # output is digest
    digest = hashlib.sha256(message.encode()).hexdigest()

    # reject if signature mismatch
    # use compare_digest instead of == to prevent timing attack
    if not hmac.compare_digest(x_zevent_signature, digest):
        raise HTTPException(
            status_code=403, detail="Zalo webhook signature verification failed"
        )
