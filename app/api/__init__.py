from fastapi import APIRouter
from app.api.v1.endpoints import orders as orders_v1

api_v1_router = APIRouter()
api_v1_router.include_router(orders_v1.router, prefix="/orders", tags=["Orders"])

# from app.api.v2.endpoints import orders as orders_v2
# api_v2_router = APIRouter()
# api_v2_router.include_router(orders_v2.router, prefix="/orders", tags=["Orders"])