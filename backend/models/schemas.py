"""Database schemas and models."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ChatMessage(BaseModel):
    """Chat message schema."""

    content: str = Field(..., min_length=1, max_length=10000)
    role: str = Field(..., pattern="^(user|assistant|system)$")
    timestamp: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Hello, how are you?",
                "role": "user",
                "timestamp": "2024-01-01T12:00:00",
            }
        }


class ChatRequest(BaseModel):
    """Chat request schema."""

    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[str] = None
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0, le=2)
    max_tokens: Optional[int] = Field(None, ge=1)

    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is Python?",
                "conversation_id": "conv_123",
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 2048,
            }
        }


class ConversationCreateRequest(BaseModel):
    """Request schema for creating a new conversation."""

    title: Optional[str] = Field("New Chat", min_length=1, max_length=200)
    system_prompt: Optional[str] = Field("You are a helpful AI assistant", max_length=5000)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Python Discussion",
                "system_prompt": "You are a helpful Python expert.",
            }
        }


class ChatResponse(BaseModel):
    """Chat response schema."""

    message: str
    conversation_id: str
    timestamp: datetime
    model: str
    tokens_used: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Python is a programming language.",
                "conversation_id": "conv_123",
                "timestamp": "2024-01-01T12:00:00",
                "model": "gpt-3.5-turbo",
                "tokens_used": 45,
            }
        }


class ConversationResponse(BaseModel):
    """Conversation response schema."""

    conversation_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_123",
                "messages": [],
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00",
            }
        }


class DocumentUploadResponse(BaseModel):
    """Document upload response schema."""

    document_id: str
    filename: str
    uploaded_at: datetime
    status: str = "processing"

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_123",
                "filename": "document.pdf",
                "uploaded_at": "2024-01-01T12:00:00",
                "status": "processing",
            }
        }
