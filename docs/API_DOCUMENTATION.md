# API Documentation - Checkpoint 3

## Overview

This document describes all API endpoints implemented in Checkpoint 3 of the AI Chatbot application.

**Base URL:** `http://localhost:8000/api`

**Interactive Docs:** `http://localhost:8000/docs` (Swagger UI)

---

## Table of Contents

1. [Health Check Endpoints](#health-check-endpoints)
2. [Conversation Endpoints](#conversation-endpoints)
3. [Message Endpoints](#message-endpoints)
4. [Document Endpoints](#document-endpoints)
5. [Error Handling](#error-handling)
6. [Examples](#examples)

---

## Health Check Endpoints

### GET /api/health

Check if the API service is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "AI Chatbot API",
  "version": "1.0.0"
}
```

**Status Code:** 200 OK

---

### GET /api/health/db

Check database connectivity and health.

**Response:**
```json
{
  "status": "healthy",
  "database": "MongoDB",
  "message": "Database connection is active"
}
```

**Status Code:** 200 OK

---

## Conversation Endpoints

### POST /api/conversations

Create a new conversation.

**Parameters:**
- `system_prompt` (string, optional): System prompt for the conversation. Default: "You are a helpful AI assistant"

**Request:**
```bash
curl -X POST "http://localhost:8000/api/conversations?system_prompt=You%20are%20helpful"
```

**Response:**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [],
  "created_at": "2024-03-25T10:30:00",
  "updated_at": "2024-03-25T10:30:00"
}
```

**Status Code:** 200 OK

---

### GET /api/conversations

List all conversations with pagination.

**Query Parameters:**
- `skip` (integer, default: 0): Number of conversations to skip
- `limit` (integer, default: 50, max: 100): Number of conversations to return

**Request:**
```bash
curl "http://localhost:8000/api/conversations?skip=0&limit=10"
```

**Response:**
```json
{
  "status": "success",
  "message": "Conversations retrieved successfully",
  "data": {
    "conversations": [...],
    "skip": 0,
    "limit": 10,
    "count": 5
  }
}
```

**Status Code:** 200 OK

---

### GET /api/conversations/{conversation_id}

Get a specific conversation with all its messages.

**Path Parameters:**
- `conversation_id` (string): Unique conversation ID

**Request:**
```bash
curl "http://localhost:8000/api/conversations/550e8400-e29b-41d4-a716-446655440000"
```

**Response:**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [
    {
      "content": "Hello!",
      "role": "user",
      "timestamp": "2024-03-25T10:30:00"
    }
  ],
  "created_at": "2024-03-25T10:30:00",
  "updated_at": "2024-03-25T10:30:00"
}
```

**Status Code:** 200 OK
**Error Code:** 404 (Conversation not found)

---

### PATCH /api/conversations/{conversation_id}

Update conversation title.

**Path Parameters:**
- `conversation_id` (string): Conversation ID

**Query Parameters:**
- `title` (string, required): New conversation title

**Request:**
```bash
curl -X PATCH "http://localhost:8000/api/conversations/550e8400-e29b-41d4-a716-446655440000?title=My%20Chat"
```

**Response:**
```json
{
  "status": "success",
  "message": "Conversation updated successfully",
  "data": {
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "My Chat",
    "updated_at": "2024-03-25T10:35:00"
  }
}
```

**Status Code:** 200 OK

---

### DELETE /api/conversations/{conversation_id}

Delete a conversation and all its messages.

**Path Parameters:**
- `conversation_id` (string): Conversation ID to delete

**Request:**
```bash
curl -X DELETE "http://localhost:8000/api/conversations/550e8400-e29b-41d4-a716-446655440000"
```

**Response:**
```json
{
  "status": "success",
  "message": "Conversation deleted successfully",
  "data": {
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Status Code:** 200 OK

---

### GET /api/conversations/{conversation_id}/stats

Get conversation statistics.

**Path Parameters:**
- `conversation_id` (string): Conversation ID

**Request:**
```bash
curl "http://localhost:8000/api/conversations/550e8400-e29b-41d4-a716-446655440000/stats"
```

**Response:**
```json
{
  "status": "success",
  "message": "Statistics retrieved successfully",
  "data": {
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "My Chat",
    "created_at": "2024-03-25T10:30:00",
    "updated_at": "2024-03-25T10:35:00",
    "message_count": 5,
    "total_tokens": 250
  }
}
```

**Status Code:** 200 OK

---

## Message Endpoints

### POST /api/message/send

Send a message and get a response.

**Request Body (JSON):**
```json
{
  "message": "What is Python?",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "model": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 2048
}
```

**Body Parameters:**
- `message` (string, required): User message (1-10000 chars)
- `conversation_id` (string, optional): Existing conversation ID. If omitted, new conversation is created
- `model` (string, optional): Model name
- `temperature` (float, optional): Temperature (0-2), higher = more creative
- `max_tokens` (integer, optional): Maximum tokens in response

**Request:**
```bash
curl -X POST "http://localhost:8000/api/message/send" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is Python?",
    "temperature": 0.7
  }'
```

**Response:**
```json
{
  "message": "Thank you for your message: 'What is Python?'. AI responses will be enabled in Checkpoint 4...",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-03-25T10:35:00",
  "model": "gpt-3.5-turbo",
  "tokens_used": 45
}
```

**Status Code:** 200 OK
**Error Code:** 422 (Validation error), 404 (Conversation not found)

---

### GET /api/conversations/{conversation_id}/messages

Get paginated message history.

**Path Parameters:**
- `conversation_id` (string): Conversation ID

**Query Parameters:**
- `skip` (integer, default: 0): Messages to skip
- `limit` (integer, default: 50, max: 100): Messages to return

**Request:**
```bash
curl "http://localhost:8000/api/conversations/550e8400-e29b-41d4-a716-446655440000/messages?skip=0&limit=10"
```

**Response:**
```json
{
  "status": "success",
  "message": "Messages retrieved successfully",
  "data": {
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
    "messages": [...],
    "skip": 0,
    "limit": 10,
    "total_count": 5
  }
}
```

**Status Code:** 200 OK

---

### GET /api/conversations/{conversation_id}/recent

Get the most recent messages.

**Path Parameters:**
- `conversation_id` (string): Conversation ID

**Query Parameters:**
- `count` (integer, default: 10, max: 100): Number of recent messages

**Request:**
```bash
curl "http://localhost:8000/api/conversations/550e8400-e29b-41d4-a716-446655440000/recent?count=5"
```

**Response:**
```json
{
  "status": "success",
  "message": "Recent messages retrieved successfully",
  "data": {
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
    "messages": [...],
    "count": 5
  }
}
```

**Status Code:** 200 OK

---

### GET /api/conversations/{conversation_id}/search

Search messages in a conversation.

**Path Parameters:**
- `conversation_id` (string): Conversation ID

**Query Parameters:**
- `query` (string, required): Search query (1-500 chars)
- `limit` (integer, default: 20, max: 100): Maximum results

**Request:**
```bash
curl "http://localhost:8000/api/conversations/550e8400-e29b-41d4-a716-446655440000/search?query=Python&limit=10"
```

**Response:**
```json
{
  "status": "success",
  "message": "Search completed successfully",
  "data": {
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
    "query": "Python",
    "messages": [...],
    "count": 3
  }
}
```

**Status Code:** 200 OK

---

### GET /api/conversations/{conversation_id}/export

Export entire conversation as JSON.

**Path Parameters:**
- `conversation_id` (string): Conversation ID

**Request:**
```bash
curl "http://localhost:8000/api/conversations/550e8400-e29b-41d4-a716-446655440000/export" \
  -o conversation_export.json
```

**Response:**
```json
{
  "status": "success",
  "message": "Conversation exported successfully",
  "data": {
    "conversation": {
      "_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "My Chat",
      "created_at": "2024-03-25T10:30:00",
      ...
    },
    "messages": [...]
  }
}
```

**Status Code:** 200 OK

---

## Document Endpoints

### GET /api/documents

List all uploaded documents.

**Query Parameters:**
- `skip` (integer, default: 0): Documents to skip
- `limit` (integer, default: 50, max: 100): Documents to return

**Request:**
```bash
curl "http://localhost:8000/api/documents?skip=0&limit=10"
```

**Response:**
```json
{
  "status": "success",
  "message": "Documents retrieved successfully",
  "data": {
    "documents": [...],
    "skip": 0,
    "limit": 10,
    "count": 2
  }
}
```

**Status Code:** 200 OK

---

### GET /api/documents/{document_id}

Get document metadata.

**Path Parameters:**
- `document_id` (string): Document ID

**Request:**
```bash
curl "http://localhost:8000/api/documents/doc_abc123"
```

**Response:**
```json
{
  "status": "success",
  "message": "Document retrieved successfully",
  "data": {
    "_id": "doc_abc123",
    "document_id": "doc_abc123",
    "filename": "document.pdf",
    "uploaded_at": "2024-03-25T10:30:00",
    "status": "completed",
    "chunks_count": 10
  }
}
```

**Status Code:** 200 OK
**Error Code:** 404 (Document not found)

---

### POST /api/documents/upload

Upload a document for RAG processing.

**Supported Formats:** PDF, TXT, MD  
**Max File Size:** 50 MB

**Request (Multipart Form):**
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "status": "success",
  "message": "Document uploaded successfully",
  "data": {
    "document_id": "doc_abc123",
    "filename": "document.pdf",
    "size": 102400,
    "status": "processing",
    "message": "Document uploaded successfully. Processing will start soon."
  }
}
```

**Status Code:** 200 OK
**Error Code:** 422 (Validation error - invalid file type, empty file, file too large)

---

### DELETE /api/documents/{document_id}

Delete a document.

**Path Parameters:**
- `document_id` (string): Document ID to delete

**Request:**
```bash
curl -X DELETE "http://localhost:8000/api/documents/doc_abc123"
```

**Response:**
```json
{
  "status": "success",
  "message": "Document deleted successfully",
  "data": {
    "document_id": "doc_abc123"
  }
}
```

**Status Code:** 200 OK

---

### PATCH /api/documents/{document_id}/status

Update document processing status.

**Path Parameters:**
- `document_id` (string): Document ID

**Query Parameters:**
- `status` (string, required): New status - "processing", "completed", or "failed"

**Request:**
```bash
curl -X PATCH "http://localhost:8000/api/documents/doc_abc123/status?status=completed"
```

**Response:**
```json
{
  "status": "success",
  "message": "Document status updated successfully",
  "data": {
    "document_id": "doc_abc123",
    "status": "completed",
    ...
  }
}
```

**Status Code:** 200 OK

---

## Error Handling

### Error Response Format

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Codes

| Status Code | Meaning |
|---|---|
| 200 | Success |
| 400 | Bad Request |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

### Example Error Response

**400 Bad Request:**
```json
{
  "detail": "File type not allowed. Allowed types: .pdf, .txt, .md"
}
```

**404 Not Found:**
```json
{
  "detail": "Conversation not found"
}
```

**422 Validation Error:**
```json
{
  "detail": "Message cannot be empty"
}
```

---

## Examples

### Example 1: Create Conversation and Send Message

```bash
# 1. Create conversation
CONV_ID=$(curl -s -X POST "http://localhost:8000/api/conversations" \
  -H "Content-Type: application/json" \
  | jq -r '.conversation_id')

echo "Created conversation: $CONV_ID"

# 2. Send message
curl -X POST "http://localhost:8000/api/message/send" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"What is Python?\",
    \"conversation_id\": \"$CONV_ID\"
  }"

# 3. Get conversation history
curl "http://localhost:8000/api/conversations/$CONV_ID/messages"

# 4. Delete conversation
curl -X DELETE "http://localhost:8000/api/conversations/$CONV_ID"
```

### Example 2: Upload Document

```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@guide.pdf"

# List documents
curl "http://localhost:8000/api/documents"
```

---

## Testing

Run the automated test script:

```bash
python scripts/test_api.py
```

This will test all endpoints and display results.

---

## Notes for Checkpoint 4

- **AI Integration:** Message responses are currently placeholders. Real LLM integration comes in Checkpoint 4.
- **Streaming:** Real-time response streaming will be added in Checkpoint 4.
- **RAG Processing:** Document chunking and embedding will be implemented in Checkpoint 4.
- **Token Counting:** Accurate token counting will be added with LLM integration.

---

## Rate Limiting

Rate limiting will be implemented in future checkpoints. Currently, no limits are applied.

---

## CORS

The API accepts requests from:
- http://localhost:5173 (Vite frontend dev server)
- http://localhost:3000 (Alternative frontend)

Customize in `.env` file with `CORS_ORIGINS` variable.
