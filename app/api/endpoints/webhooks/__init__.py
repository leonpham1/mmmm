from fastapi import APIRouter
from app.api.endpoints.webhooks.zalo_webhook import zalo_webhook_router

webhook_router = APIRouter(prefix="/webhooks")
webhook_router.include_router(router=zalo_webhook_router)