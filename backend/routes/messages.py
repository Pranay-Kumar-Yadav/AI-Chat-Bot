"""Message sending and response endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
from loguru import logger

from backend.models import ChatRequest, ChatResponse
from backend.services.chat_service import get_chat_service
from backend.core import ValidationException
from backend.utils import format_response

router = APIRouter()


@router.post("/message/send", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message and get an AI response.
    
    Uses LangChain + OpenAI for response generation.
    Optionally uses RAG for context augmentation.
    
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
        
        # Get chat service
        chat_service = await get_chat_service()
        
        # Send message through chat service
        response = await chat_service.send_message(
            message=request.message,
            conversation_id=request.conversation_id,
            use_rag=request.use_rag if hasattr(request, 'use_rag') else False,
            system_prompt=request.system_prompt if hasattr(request, 'system_prompt') else None,
            model=request.model if hasattr(request, 'model') else None,
        )
        
        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
        
        logger.debug(f"Message processed successfully for conversation: {response.get('conversation_id')}")
        
        return ChatResponse(**response)
    
    except ValidationException as e:
        logger.error(f"Validation error: {e.detail}")
        raise HTTPException(status_code=422, detail=e.detail)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/message/history")
async def get_message_history(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    Get message history for a conversation.
    
    Args:
        conversation_id: Conversation ID
        limit: Number of messages to return
        offset: Pagination offset
        
    Returns:
        List of messages
    """
    try:
        chat_service = await get_chat_service()
        
        messages = await chat_service.get_conversation_history(
            conversation_id=conversation_id,
            limit=limit,
            offset=offset,
        )
        
        return format_response(
            {
                "conversation_id": conversation_id,
                "messages": messages,
                "count": len(messages),
                "offset": offset,
                "limit": limit,
            },
            "Message history retrieved successfully"
        )
    
    except Exception as e:
        logger.error(f"Error getting message history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message/clear")
async def clear_conversation(conversation_id: str):
    """
    Clear conversation history.
    
    Args:
        conversation_id: Conversation ID
        
    Returns:
        Success message
    """
    try:
        chat_service = await get_chat_service()
        
        success = await chat_service.clear_conversation(conversation_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to clear conversation")
        
        return format_response(
            {
                "conversation_id": conversation_id,
                "cleared": True,
            },
            "Conversation cleared successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
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