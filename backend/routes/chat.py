"""Chat routes for conversation management and messaging."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
from loguru import logger

from backend.models import ChatRequest, ChatResponse, ConversationResponse, ConversationCreateRequest
from backend.database import get_database, ConversationQueries, MessageQueries
from backend.core import ValidationException, ChatException
from backend.utils import generate_id, format_response, format_error

router = APIRouter()


# ==================== Conversation Management ====================


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(request: ConversationCreateRequest):
    """
    Create a new conversation.
    
    Args:
        request: ConversationCreateRequest with title and system_prompt
        
    Returns:
        New conversation with ID and metadata
    """
    try:
        system_prompt = request.system_prompt or "You are a helpful AI assistant"
        title = request.title or "New Chat"
        
        if not system_prompt or len(system_prompt.strip()) == 0:
            system_prompt = "You are a helpful AI assistant"
        
        if not title or len(title.strip()) == 0:
            title = "New Chat"
        
        db = get_database()
        conversation_id = await db.create_conversation(system_prompt, title)
        
        conversation = await db.get_conversation(conversation_id)
        
        if not conversation:
            raise ChatException("Failed to create conversation")
        
        return ConversationResponse(
            conversation_id=conversation["_id"],
            messages=[],
            created_at=conversation["created_at"],
            updated_at=conversation["updated_at"],
        )
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations", response_model=dict)
async def list_conversations(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100)):
    """
    Get all conversations with pagination.
    
    Args:
        skip: Number of conversations to skip
        limit: Maximum number of conversations to return
        
    Returns:
        List of conversations with pagination info
    """
    try:
        db = get_database()
        conversations = await ConversationQueries.get_user_conversations(db, limit=limit, skip=skip)
        
        return format_response(
            {
                "conversations": conversations,
                "skip": skip,
                "limit": limit,
                "count": len(conversations),
            },
            "Conversations retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str):
    """
    Get a specific conversation.
    
    Args:
        conversation_id: Conversation ID
        
    Returns:
        Conversation with messages
    """
    try:
        db = get_database()
        conversation = await db.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = await db.get_conversation_history(conversation_id)
        
        return ConversationResponse(
            conversation_id=conversation["_id"],
            messages=[
                {
                    "content": msg["content"],
                    "role": msg["role"],
                    "timestamp": msg.get("timestamp"),
                }
                for msg in messages
            ],
            created_at=conversation["created_at"],
            updated_at=conversation["updated_at"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/conversations/{conversation_id}")
async def update_conversation(conversation_id: str, title: str):
    """
    Update conversation title.
    
    Args:
        conversation_id: Conversation ID
        title: New conversation title
        
    Returns:
        Updated conversation
    """
    try:
        if not title or len(title.strip()) == 0:
            raise ValidationException("Title cannot be empty")
        
        db = get_database()
        
        # Verify conversation exists
        conversation = await db.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        success = await db.update_conversation_title(conversation_id, title)
        
        if not success:
            raise ChatException("Failed to update conversation")
        
        updated_conv = await db.get_conversation(conversation_id)
        
        return format_response(
            {
                "conversation_id": updated_conv["_id"],
                "title": updated_conv["title"],
                "updated_at": updated_conv["updated_at"],
            },
            "Conversation updated successfully"
        )
    except Exception as e:
        logger.error(f"Error updating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Delete a conversation and all its messages.
    
    Args:
        conversation_id: Conversation ID
        
    Returns:
        Success message
    """
    try:
        db = get_database()
        
        # Verify conversation exists
        conversation = await db.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        success = await db.delete_conversation(conversation_id)
        
        if not success:
            raise ChatException("Failed to delete conversation")
        
        return format_response(
            {"conversation_id": conversation_id},
            "Conversation deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Conversation Statistics ====================


@router.get("/conversations/{conversation_id}/stats")
async def get_conversation_stats(conversation_id: str):
    """
    Get conversation statistics.
    
    Args:
        conversation_id: Conversation ID
        
    Returns:
        Conversation statistics
    """
    try:
        db = get_database()
        
        # Verify conversation exists
        conversation = await db.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        stats = await ConversationQueries.get_conversation_stats(db, conversation_id)
        total_tokens = await MessageQueries.get_total_tokens(db, conversation_id)
        
        return format_response(
            {
                **stats,
                "total_tokens": total_tokens,
            },
            "Statistics retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Message History ====================


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_history(
    conversation_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """
    Get conversation message history with pagination.
    
    Args:
        conversation_id: Conversation ID
        skip: Number of messages to skip
        limit: Maximum messages to return
        
    Returns:
        List of messages
    """
    try:
        db = get_database()
        
        # Verify conversation exists
        conversation = await db.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = await db.get_conversation_history(conversation_id, limit=limit)
        message_count = await MessageQueries.get_message_count(db, conversation_id)
        
        return format_response(
            {
                "conversation_id": conversation_id,
                "messages": messages,
                "skip": skip,
                "limit": limit,
                "total_count": message_count,
            },
            "Messages retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}/recent")
async def get_recent_messages(conversation_id: str, count: int = Query(10, ge=1, le=100)):
    """
    Get the most recent messages from a conversation.
    
    Args:
        conversation_id: Conversation ID
        count: Number of recent messages
        
    Returns:
        Recent messages
    """
    try:
        db = get_database()
        
        # Verify conversation exists
        conversation = await db.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = await db.get_recent_messages(conversation_id, count=count)
        
        return format_response(
            {
                "conversation_id": conversation_id,
                "messages": messages,
                "count": len(messages),
            },
            "Recent messages retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recent messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}/search")
async def search_conversation(
    conversation_id: str,
    query: str = Query(..., min_length=1, max_length=500),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Search messages within a conversation.
    
    Args:
        conversation_id: Conversation ID
        query: Search query
        limit: Maximum results
        
    Returns:
        Matching messages
    """
    try:
        if not query or len(query.strip()) == 0:
            raise ValidationException("Search query cannot be empty")
        
        db = get_database()
        
        # Verify conversation exists
        conversation = await db.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = await db.search_messages(conversation_id, query, limit=limit)
        
        return format_response(
            {
                "conversation_id": conversation_id,
                "query": query,
                "messages": messages,
                "count": len(messages),
            },
            "Search completed successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Export ====================


@router.get("/conversations/{conversation_id}/export")
async def export_conversation(conversation_id: str):
    """
    Export entire conversation as JSON.
    
    Args:
        conversation_id: Conversation ID
        
    Returns:
        Conversation data with all messages
    """
    try:
        db = get_database()
        
        # Verify conversation exists
        conversation = await db.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        export_data = await MessageQueries.export_conversation(db, conversation_id)
        
        return format_response(
            export_data,
            "Conversation exported successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
