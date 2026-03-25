"""API routes module."""

from .chat import router as chat_router
from .health import router as health_router
from .documents import router as documents_router
from .messages import router as messages_router

__all__ = ["chat_router", "health_router", "documents_router", "messages_router"]
