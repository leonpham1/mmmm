from fastapi import APIRouter
from app.api.endpoints.system import monitor

api_router = APIRouter()
api_router.include_router(monitor.router, prefix="/system", tags=["System"])