"""Message sending and response endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
from loguru import logger

from backend.models import ChatRequest, ChatResponse
from backend.database import get_database
from backend.core import ValidationException
from backend.utils import format_response

router = APIRouter()


def get_placeholder_response(user_message: str) -> str:
    """
    Generate a placeholder response.
    This will be replaced with real LLM in Checkpoint 4.
    """
    return (
        f"Thank you for your message: '{user_message}'. "
        f"AI responses will be enabled in Checkpoint 4 with LangChain integration. "
        f"For now, this is a placeholder response."
    )


@router.post("/message/send", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message and store it in the database.
    
    In Checkpoint 3, this stores the message.
    In Checkpoint 4, this will integrate with OpenAI and LangChain.
    
    Args:
        request: Chat request with message and optional conversation_id
        
    Returns:
        Chat response with AI response
    """
    try:
        # Validate message
        if not request.message or len(request.message.strip()) == 0:
            raise ValidationException("Message cannot be empty")
        
        if len(request.message) > 10000:
            raise ValidationException("Message exceeds maximum length of 10000 characters")
        
        db = get_database()
        conversation_id = request.conversation_id
        
        # Create new conversation if needed
        if not conversation_id:
            conversation_id = await db.create_conversation()
            logger.info(f"Created new conversation: {conversation_id}")
        else:
            # Verify conversation exists
            conversation = await db.get_conversation(conversation_id)
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Save user message
        user_saved = await db.save_message(
            conversation_id=conversation_id,
            role="user",
            content=request.message,
            tokens_used=0
        )
        
        if not user_saved:
            raise HTTPException(status_code=500, detail="Failed to save user message")
        
        logger.debug(f"Saved user message to conversation: {conversation_id}")
        
        # For Checkpoint 3: Send a placeholder response
        # In Checkpoint 4, this will be replaced with OpenAI/LangChain integration
        response_message = get_placeholder_response(request.message)
        
        # Save assistant response
        response_saved = await db.save_message(
            conversation_id=conversation_id,
            role="assistant",
            content=response_message,
            tokens_used=0
        )
        
        if not response_saved:
            logger.warning("Failed to save assistant response")
        
        logger.debug(f"Saved assistant response to conversation: {conversation_id}")
        
        return ChatResponse(
            message=response_message,
            conversation_id=conversation_id,
            timestamp=datetime.utcnow(),
            model=request.model or "placeholder",
            tokens_used=0,
        )
    
    except ValidationException as e:
        logger.error(f"Validation error: {e.detail}")
        raise HTTPException(status_code=422, detail=e.detail)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/message/stream-placeholder")
async def placeholder_streaming_endpoint(conversation_id: str):
    """
    Placeholder for streaming endpoint.
    Will be replaced in Checkpoint 4 with actual streaming.
    
    Args:
        conversation_id: Conversation ID
        
    Returns:
        Placeholder message
    """
    return format_response(
        {
            "message": "Streaming will be implemented in Checkpoint 4",
            "conversation_id": conversation_id,
        },
        "Placeholder response"
    )