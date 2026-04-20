
from fastapi import APIRouter

router = APIRouter()

@router.post("/zalo")
async def handle_zalo_webhook():
    pass