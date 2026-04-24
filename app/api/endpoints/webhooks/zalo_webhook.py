import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError

from app.api.deps.webhooks.zalo_webhook_deps import verify_zalo_webhook_signature
from app.schemas.webhooks.zalo_schema import ZaloWebhookPayload, parse_zalo_webhook_payload

logger = logging.getLogger(__name__)

__all__ = ["ZaloWebhookPayload", "handle_zalo_webhook", "zalo_webhook_router"]

zalo_webhook_router = APIRouter(prefix="/zalo")


@zalo_webhook_router.post(
    path="/",
    status_code=200,
)
async def handle_zalo_webhook(
    data: Annotated[dict, Depends(verify_zalo_webhook_signature)],
) -> dict[str, str]:
    """Handle POST /api/webhooks/zalo after signature verification.

    ``data`` is the JSON object returned by ``verify_zalo_webhook_signature`` (same
    bytes used for the signature). It is validated with ``parse_zalo_webhook_payload``
    against the ``ZaloWebhookPayload`` discriminated union in ``app.schemas.webhooks.zalo_schema``.
    """
    try:
        payload = parse_zalo_webhook_payload(data)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc

    logger.info("zalo webhook event_name=%s app_id=%s", payload.event_name, payload.app_id)
    return {"status": "ok"}
