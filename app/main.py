from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(title="End-to-End Eatery", description="Mmmm...")
app.include_router(api_router, prefix="/api")