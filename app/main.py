from fastapi import APIRouter, FastAPI
from app.api.endpoints.system.monitor import system_router
from app.api.endpoints.webhooks import webhook_router

app = FastAPI(
    title="End-to-End Eatery", 
    description="Project for Mom", 
    version="0.1.0"
)

api_router = APIRouter(prefix="/api")
api_router.include_router(router=system_router)
api_router.include_router(router=webhook_router)

app.include_router(router=api_router)