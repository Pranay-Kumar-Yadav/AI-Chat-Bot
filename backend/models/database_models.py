"""Database document models."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ConversationDB(BaseModel):
    """MongoDB conversation document model."""

    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
    system_prompt: str = ""
    title: str = "New Chat"
    message_count: int = 0

    class Config:
        populate_by_name = True


class MessageDB(BaseModel):
    """MongoDB message document model."""

    id: str = Field(alias="_id")
    conversation_id: str
    role: str  # user, assistant, system
    content: str
    timestamp: datetime
    tokens_used: int = 0

    class Config:
        populate_by_name = True


class DocumentDB(BaseModel):
    """MongoDB document metadata model."""

    id: str = Field(alias="_id")
    document_id: str
    filename: str
    uploaded_at: datetime
    status: str  # processing, completed, failed
    chunks_count: int = 0

    class Config:
        populate_by_name = True


class DocumentChunkDB(BaseModel):
    """MongoDB document chunk model for RAG."""

    id: str = Field(alias="_id")
    document_id: str
    chunk_index: int
    content: str
    embedding: Optional[List[float]] = None
    created_at: datetime

    class Config:
        populate_by_name = True
