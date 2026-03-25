"""Health check routes."""

from fastapi import APIRouter
from backend.database import get_database
from loguru import logger

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running.
    
    Returns:
        dict: Status information
    """
    return {
        "status": "healthy",
        "service": "AI Chatbot API",
        "version": "1.0.0",
    }


@router.get("/health/db")
async def health_check_db():
    """
    Database health check.
    
    Returns:
        dict: Database status
    """
    try:
        db = get_database()
        is_healthy = await db.health_check()
        
        if is_healthy:
            return {
                "status": "healthy",
                "database": "MongoDB",
                "message": "Database connection is active",
            }
        else:
            return {
                "status": "unhealthy",
                "database": "MongoDB",
                "message": "Database connection failed",
            }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "database": "MongoDB",
            "message": str(e),
        }
