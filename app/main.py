from sys import prefix
from fastapi import FastAPI

from app.api.endpoints.system.monitor import system_router
from app.api.endpoints.webhooks import webhook_router

app = FastAPI(title="End-to-End Eatery", 
            description="Mmmm...", prefix="/api")

app.include_router(router=system_router)
app.include_router(router=webhook_router)