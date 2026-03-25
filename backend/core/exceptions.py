"""Custom exceptions for the application."""

from fastapi import HTTPException
from typing import Any, Dict, Optional


class AppException(HTTPException):
    """Base application exception."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize exception.
        
        Args:
            status_code: HTTP status code
            detail: Error message
            error_code: Custom error code
            data: Additional error data
        """
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.data = data or {}


class DatabaseException(AppException):
    """Database operation exception."""

    def __init__(self, detail: str, error_code: str = "DB_ERROR"):
        super().__init__(status_code=500, detail=detail, error_code=error_code)


class ValidationException(AppException):
    """Validation exception."""

    def __init__(self, detail: str, error_code: str = "VALIDATION_ERROR"):
        super().__init__(status_code=422, detail=detail, error_code=error_code)


class ChatException(AppException):
    """Chat operation exception."""

    def __init__(self, detail: str, error_code: str = "CHAT_ERROR"):
        super().__init__(status_code=400, detail=detail, error_code=error_code)


class RAGException(AppException):
    """RAG operation exception."""

    def __init__(self, detail: str, error_code: str = "RAG_ERROR"):
        super().__init__(status_code=400, detail=detail, error_code=error_code)
