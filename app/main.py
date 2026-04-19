from fastapi import FastAPI

from app.api import api_v1_router
from app.api.system import monitor

app = FastAPI(title="End-to-End Eatery", description="Mmmm...")
app.include_router(monitor.router)
app.include_router(api_v1_router, prefix="/api/v1")
# app.include_router(api_v2_router, prefix="/api/v2")