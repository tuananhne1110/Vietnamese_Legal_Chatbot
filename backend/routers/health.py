import logging
from fastapi import APIRouter, HTTPException
from backend.configs.settings import get_qdrant_client, get_supabase_client
from backend.configs.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check():
    """Enhanced health check endpoint."""
    settings = get_settings()
    
    health_status = {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "services": {}
    }
    
    # Check Qdrant
    try:
        client = get_qdrant_client()
        collections = client.get_collections()
        health_status["services"]["qdrant"] = {
            "status": "healthy",
            "collections": len(collections.collections)
        }
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        health_status["services"]["qdrant"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check Supabase
    try:
        supabase_client = get_supabase_client()
        if supabase_client:
            # Simple query to test connection
            response = supabase_client.table("chat_history").select("id").limit(1).execute()
            health_status["services"]["supabase"] = {
                "status": "healthy",
                "connected": True
            }
        else:
            health_status["services"]["supabase"] = {
                "status": "not_configured",
                "connected": False
            }
    except Exception as e:
        logger.error(f"Supabase health check failed: {e}")
        health_status["services"]["supabase"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    return health_status

@router.get("/health/ready")
async def readiness_check():
    """Readiness check for Kubernetes."""
    health_result = await health_check()
    if health_result["status"] != "healthy":
        raise HTTPException(status_code=503, detail="Service not ready")
    return {"status": "ready"}

@router.get("/health/live")
async def liveness_check():
    """Liveness check for Kubernetes."""
    return {"status": "alive"} 
