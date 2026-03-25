"""Health check routes."""

from fastapi import APIRouter

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
    return {
        "status": "healthy",
        "database": "MongoDB",
    }
