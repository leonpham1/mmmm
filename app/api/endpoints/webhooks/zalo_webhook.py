import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import ValidationError

from app.api.deps.webhooks.zalo_webhook_deps import verify_zalo_webhook_signature
from app.schemas.webhooks.zalo_schema import ZaloWebhookPayload, parse_zalo_webhook_payload

logger = logging.getLogger(__name__)

__all__ = ["ZaloWebhookPayload", "handle_zalo_webhook", "zalo_webhook_router"]

zalo_webhook_router = APIRouter(prefix="/zalo")

@zalo_webhook_router.post(
    path="/",
    dependencies=[Depends(verify_zalo_webhook_signature)],
    status_code=200,
)
async def handle_zalo_webhook(request: Request) -> dict[str, str]:
    """Handle POST /api/webhooks/zalo after signature verification.

    Body is validated with ``parse_zalo_webhook_payload`` against the
    ``ZaloWebhookPayload`` discriminated union in ``app.schemas.webhooks.zalo_schema``.
    """
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid JSON body") from None

    try:
        payload = parse_zalo_webhook_payload(data)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc

    logger.info("zalo webhook event_name=%s app_id=%s", payload.event_name, payload.app_id)
    return {"status": "ok"}
