
from fastapi import APIRouter
from app.api.endpoints.webhooks.zalo import zalo_router

webhook_router = APIRouter(prefix= "/webhooks")
webhook_router.include_router(router=zalo_router) 