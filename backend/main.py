"""Backend main application file."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from backend.config import settings
from backend.routes import chat_router, health_router, documents_router, messages_router
from backend.database import init_database, close_database
from backend.services.chat_service import get_chat_service
from backend.services.rag_service import get_rag_service


# Configure logging
logger.add(
    "logs/app.log",
    rotation="500 MB",
    retention="10 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for app startup and shutdown.
    
    Handles:
    - Database connection initialization
    - RAG service initialization
    - Chat service initialization
    - Database connection cleanup
    """
    # Startup
    logger.info("Starting application...")
    try:
        await init_database()
        logger.info("Database initialized successfully")
        
        # Initialize RAG service
        rag_service = await get_rag_service()
        logger.info("RAG service initialized successfully")
        
        # Initialize chat service
        chat_service = await get_chat_service()
        logger.info("Chat service initialized successfully")
        
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")
    try:
        await close_database()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")


# Create FastAPI app
app = FastAPI(
    title="AI Chatbot API",
    description="A full-stack AI chatbot application with RAG support",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1"],
)

# Include routers
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(documents_router, prefix="/api", tags=["documents"])
app.include_router(messages_router, prefix="/api", tags=["messages"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
    )
