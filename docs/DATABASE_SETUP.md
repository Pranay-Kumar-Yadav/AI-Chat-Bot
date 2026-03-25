# Database Setup Guide

## Overview

The AI Chatbot application uses MongoDB for persistent data storage. This guide explains how to set up and configure the database.

## Database Structure

### Collections

1. **conversations** - Stores conversation metadata
   - `_id` (String): Unique conversation ID
   - `created_at` (DateTime): Creation timestamp
   - `updated_at` (DateTime): Last update timestamp
   - `system_prompt` (String): System prompt for the conversation
   - `title` (String): Conversation title
   - `message_count` (Integer): Total messages in conversation

2. **messages** - Stores all messages
   - `_id` (String): Unique message ID
   - `conversation_id` (String): Reference to conversation
   - `role` (String): Message role (user, assistant, system)
   - `content` (String): Message content
   - `timestamp` (DateTime): Message timestamp
   - `tokens_used` (Integer): Tokens used (for assistant messages)

3. **documents** - Stores uploaded document metadata
   - `_id` (String): Unique document ID
   - `document_id` (String): Document identifier
   - `filename` (String): Original filename
   - `uploaded_at` (DateTime): Upload timestamp
   - `status` (String): Processing status (processing, completed, failed)
   - `chunks_count` (Integer): Number of text chunks

4. **document_chunks** - Stores RAG chunks (optional)
   - `_id` (String): Unique chunk ID
   - `document_id` (String): Parent document ID
   - `chunk_index` (Integer): Chunk number
   - `content` (String): Chunk text content
   - `embedding` (Array): Vector embedding (1536 dimensions for text-embedding-3-small)
   - `created_at` (DateTime): Creation timestamp

## Setup Instructions

### 1. Install MongoDB

**Option A: Using Docker (Recommended)**
```bash
docker run -d \
  --name ai_chatbot_mongodb \
  -e MONGO_INITDB_ROOT_USERNAME=root \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  mongo:7.0
```

**Option B: Local Installation**
- Download from: https://www.mongodb.com/try/download/community
- Follow installation guide for your OS
- Ensure MongoDB service is running

**Option C: MongoDB Atlas (Cloud)**
- Sign up at https://www.mongodb.com/cloud/atlas
- Create a free cluster
- Get connection string with your credentials

### 2. Configure Environment

Copy `.env.example` to `.env` and update MongoDB connection:

```env
# For local MongoDB
MONGO_URI=mongodb://localhost:27017/ai_chatbot
MONGO_DB_NAME=ai_chatbot

# For MongoDB with authentication
MONGO_URI=mongodb://root:password@localhost:27017/ai_chatbot
MONGO_DB_NAME=ai_chatbot

# For MongoDB Atlas
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/ai_chatbot?retryWrites=true&w=majority
MONGO_DB_NAME=ai_chatbot
```

### 3. Initialize Database

Run the initialization script:

```bash
# From project root
python scripts/init_db.py
```

This script will:
- Test connection to MongoDB
- Create necessary collections
- Create performance indexes
- Test basic CRUD operations
- Clean up test data

### 4. Verify Setup

Check database status:

```bash
python scripts/check_db_status.py
```

## Database Operations

### Using the Database Class

```python
from backend.database import get_database

# Get database instance
db = get_database()

# Ensure database is connected
await db.connect()

# Create new conversation
conversation_id = await db.create_conversation(system_prompt="You are helpful")

# Save message
await db.save_message(
    conversation_id,
    role="user",
    content="Hello!",
    tokens_used=5
)

# Get conversation history
messages = await db.get_conversation_history(conversation_id)

# Delete conversation
await db.delete_conversation(conversation_id)

# Health check
is_healthy = await db.health_check()

# Cleanup
await db.disconnect()
```

### Using Query Classes

```python
from backend.database import ConversationQueries, MessageQueries

# Get user conversations
conversations = await ConversationQueries.get_user_conversations(db, limit=10)

# Get conversation stats
stats = await ConversationQueries.get_conversation_stats(db, conversation_id)

# Get message count
count = await MessageQueries.get_message_count(db, conversation_id)

# Export conversation
export = await MessageQueries.export_conversation(db, conversation_id)
```

## Common Operations

### Create a Conversation

```python
conv_id = await db.create_conversation(
    system_prompt="You are a helpful AI assistant"
)
```

### Save Multiple Messages

```python
# User message
await db.save_message(conv_id, "user", "What is Python?")

# Assistant response
await db.save_message(
    conv_id,
    "assistant",
    "Python is a programming language...",
    tokens_used=125
)
```

### Retrieve Conversation History

```python
# Get all messages
messages = await db.get_conversation_history(conv_id)

# Get recent messages (last 10)
recent = await db.get_recent_messages(conv_id, count=10)

# Search messages
results = await db.search_messages(conv_id, "Python", limit=5)
```

### Update Conversation

```python
# Update title
await db.update_conversation_title(conv_id, "Python Questions")
```

### Document Operations

```python
# Save document
await db.save_document("doc_123", "document.pdf", status="processing")

# Update status
await db.update_document_status("doc_123", "completed")

# Get document
doc = await db.get_document("doc_123")

# Delete document
await db.delete_document("doc_123")
```

## Indexes

The application automatically creates the following indexes for performance:

**Conversations Collection:**
- `created_at` - For sorting by creation time
- `updated_at` - For sorting by update time

**Messages Collection:**
- `conversation_id` - For fast conversation lookups
- `timestamp` - For message ordering
- `(conversation_id, timestamp)` - Compound index for combined queries

**Documents Collection:**
- `document_id` - Unique index on document IDs
- `uploaded_at` - For chronological sorting

## Troubleshooting

### Connection Issues

**Error: "Can't connect to MongoDB"**
- Ensure MongoDB service is running
- Check connection string in `.env`
- Verify firewall allows port 27017
- For Docker, ensure container is running: `docker ps`

**Error: "Authentication failed"**
- Verify username and password in connection string
- Check MongoDB user exists with correct credentials
- For Atlas, ensure IP whitelist includes your IP

### Performance Issues

**Slow queries:**
- Check that indexes are created: `db.conversations.getIndexes()`
- Monitor MongoDB performance
- Consider adding more indexes for common queries

**Out of memory:**
- Implement message pagination (max queries with limits)
- Archive old conversations regularly
- Use `clear_old_conversations()` to clean up

## Backup and Recovery

### Backup MongoDB (Docker)

```bash
docker exec ai_chatbot_mongodb mongodump \
  --out /data/backup \
  --username root \
  --password password \
  --authenticationDatabase admin
```

### Restore MongoDB (Docker)

```bash
docker exec ai_chatbot_mongodb mongorestore \
  /data/backup \
  --username root \
  --password password \
  --authenticationDatabase admin
```

### MongoDB Atlas Backup

Automated daily backups are available in MongoDB Atlas dashboard.

## Monitoring

### View Database Logs

```bash
# Docker
docker logs ai_chatbot_mongodb

# Local MongoDB
# Check MongoDB log file location based on your installation
```

### Monitor Connections

```bash
# In MongoDB shell
db.currentOp()
db.serverStatus()
```

### Check Database Size

```bash
# In MongoDB shell
db.stats()
```

## Next Steps

1. Run `python scripts/init_db.py` to initialize the database
2. Configure your OpenAI API key and other settings
3. Start the backend application
4. The database will automatically handle conversation persistence

## Support

For MongoDB help:
- Official Docs: https://docs.mongodb.com/
- MongoDB Community: https://community.mongodb.com/
- Docker MongoDB: https://hub.docker.com/_/mongo
