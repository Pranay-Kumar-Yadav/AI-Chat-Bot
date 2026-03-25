"""Chat routes - placeholder for implementation."""

from fastapi import APIRouter, HTTPException
from typing import Optional

router = APIRouter()


@router.post("/chat")
async def chat(message: str, conversation_id: Optional[str] = None):
    """
    Chat endpoint - to be implemented in Checkpoint 3.
    
    Args:
        message: User message
        conversation_id: Optional conversation ID
        
    Returns:
        Chat response
    """
    raise HTTPException(status_code=501, detail="Chat endpoint not yet implemented")


@router.get("/history/{conversation_id}")
async def get_history(conversation_id: str):
    """
    Get conversation history - to be implemented in Checkpoint 3.
    
    Args:
        conversation_id: Conversation ID
        
    Returns:
        Conversation history
    """
    raise HTTPException(status_code=501, detail="History endpoint not yet implemented")
