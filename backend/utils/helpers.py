"""Helper utilities."""

import uuid
from datetime import datetime
from typing import Dict, Any, List


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


def get_current_timestamp() -> datetime:
    """Get current UTC timestamp."""
    return datetime.utcnow()


def serialize_datetime(obj: Any) -> Any:
    """Serialize datetime objects for JSON."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def pagination_params(skip: int = 0, limit: int = 50) -> Dict[str, int]:
    """
    Validate and return pagination parameters.
    
    Args:
        skip: Number of items to skip
        limit: Maximum number of items to return
        
    Returns:
        Dictionary with validated skip and limit
    """
    skip = max(0, skip)
    limit = max(1, min(limit, 100))  # Max 100 items per request
    return {"skip": skip, "limit": limit}


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    return " ".join(text.split())


def format_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """
    Format response with standard structure.
    
    Args:
        data: Response data
        message: Response message
        
    Returns:
        Formatted response dictionary
    """
    return {
        "status": "success",
        "message": message,
        "data": data,
    }


def format_error(error: str, code: str = "ERROR") -> Dict[str, Any]:
    """
    Format error response.
    
    Args:
        error: Error message
        code: Error code
        
    Returns:
        Formatted error dictionary
    """
    return {
        "status": "error",
        "error": error,
        "code": code,
    }
