from fastapi import APIRouter
# from starlette.status import HTTP_503_SERVICE_UNAVAILABLE
from app.core.config import system_settings

router = APIRouter()

@router.get("/health")
async def liveness_probe():
    """
    Liveness Check:
    Used to determine if the application is running. 
    If this fails, the orchestrator (e.g., Load Balancer, Kubernetes) will restart the container.
    """
    return {
        "status": "healthy",
        "app_name": system_settings.PROJECT_NAME
    }

@router.get("/ready")
async def readiness_probe():
    """
    Readiness Check:
    Used to determine if the application is ready to handle requests.
    Checks external dependencies like Database, AI Services, or Cache.
    If this fails, traffic will be diverted away from this instance.
    """
    # try:
    #     #await db.execute("SELECT 1")
    #     return {"status": "ready"}
    # catch Exception as ex:
    #     raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE, detail="")
