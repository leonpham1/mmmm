from fastapi import APIRouter

router = APIRouter()

@router.post("/")
async def create_order():
    return {"msg": "Order received!"}