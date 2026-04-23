from fastapi import APIRouter, Depends
from app.api.deps import verify_zalo_webhook_signature

zalo_router = APIRouter(prefix="/zalo")

@zalo_router.post(
    dependencies=[Depends(verify_zalo_webhook_signature)],
    status_code=200
)
async def handle_zalo_webhook():
    pass