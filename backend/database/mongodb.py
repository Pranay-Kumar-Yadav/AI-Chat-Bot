"""MongoDB database operations with async support using motor."""

import motor.motor_asyncio
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger
import uuid


class Database:
    """
    Async MongoDB database class for handling all database operations.
    Uses Motor for async/await compatibility with PyMongo.
    """

    def __init__(self, mongo_uri: str, db_name: str):
        """
        Initialize database connection parameters.

        Args:
            mongo_uri: MongoDB connection URI
            db_name: Database name
        """
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.client: Optional[object] = None
        self.db: Optional[object] = None
        logger.info(f"Database initialized with URI: {mongo_uri}")

    async def connect(self):
        """
        Connect to MongoDB.

        Raises:
            ConnectionFailure: If unable to connect to MongoDB
        """
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            
            # Test connection
            await self.client.admin.command("ping")
            logger.info(f"Successfully connected to MongoDB database: {self.db_name}")
            
            # Create indexes
            await self._create_indexes()
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    async def _create_indexes(self):
        """Create database indexes for optimized queries."""
        try:
            # Conversations collection indexes
            conversations = self.db["conversations"]
            await conversations.create_index("created_at")
            await conversations.create_index("updated_at")
            
            # Messages collection indexes
            messages = self.db["messages"]
            await messages.create_index("conversation_id")
            await messages.create_index("timestamp")
            await messages.create_index([("conversation_id", 1), ("timestamp", 1)])
            
            # Documents collection indexes
            documents = self.db["documents"]
            await documents.create_index("document_id", unique=True)
            await documents.create_index("uploaded_at")
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")

    # ==================== Conversation Operations ====================

    async def create_conversation(self, system_prompt: str = "", title: str = "New Chat") -> str:
        """
        Create a new conversation.

        Args:
            system_prompt: Optional system prompt for the conversation
            title: Optional title for the conversation

        Returns:
            Conversation ID
        """
        conversation_id = str(uuid.uuid4())
        now = datetime.utcnow()

        conversation = {
            "_id": conversation_id,
            "created_at": now,
            "updated_at": now,
            "system_prompt": system_prompt,
            "title": title,
            "message_count": 0,
        }

        try:
            conversations = self.db["conversations"]
            await conversations.insert_one(conversation)
            logger.info(f"Created conversation: {conversation_id}")
            return conversation_id
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            raise

    async def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """
        Get conversation by ID.

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation document or None
        """
        try:
            conversations = self.db["conversations"]
            return await conversations.find_one({"_id": conversation_id})
        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            return None

    async def get_all_conversations(self, limit: int = 50) -> List[Dict]:
        """
        Get all conversations ordered by most recent.

        Args:
            limit: Maximum number of conversations to return

        Returns:
            List of conversation documents
        """
        try:
            conversations = self.db["conversations"]
            cursor = conversations.find().sort("updated_at", -1).limit(limit)
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"Error getting conversations: {e}")
            return []

    async def update_conversation_title(
        self, conversation_id: str, title: str
    ) -> bool:
        """
        Update conversation title.

        Args:
            conversation_id: Conversation ID
            title: New title

        Returns:
            True if updated, False otherwise
        """
        try:
            conversations = self.db["conversations"]
            result = await conversations.update_one(
                {"_id": conversation_id},
                {"$set": {"title": title, "updated_at": datetime.utcnow()}},
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating conversation title: {e}")
            return False

    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete conversation and its messages.

        Args:
            conversation_id: Conversation ID

        Returns:
            True if deleted, False otherwise
        """
        try:
            # Delete conversation
            conversations = self.db["conversations"]
            conv_result = await conversations.delete_one({"_id": conversation_id})

            # Delete all messages in conversation
            messages = self.db["messages"]
            await messages.delete_many({"conversation_id": conversation_id})

            logger.info(f"Deleted conversation: {conversation_id}")
            return conv_result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            return False

    # ==================== Message Operations ====================

    async def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        tokens_used: int = 0,
    ) -> bool:
        """
        Save a message to the database.

        Args:
            conversation_id: Conversation ID
            role: Message role (user, assistant, system)
            content: Message content
            tokens_used: Number of tokens used (for assistant messages)

        Returns:
            True if saved, False otherwise
        """
        try:
            message_id = str(uuid.uuid4())
            now = datetime.utcnow()

            message = {
                "_id": message_id,
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "timestamp": now,
                "tokens_used": tokens_used,
            }

            messages = self.db["messages"]
            await messages.insert_one(message)

            # Update conversation updated_at and message_count
            conversations = self.db["conversations"]
            await conversations.update_one(
                {"_id": conversation_id},
                {
                    "$set": {"updated_at": now},
                    "$inc": {"message_count": 1},
                },
            )

            logger.debug(f"Saved message: {message_id} to conversation: {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return False

    async def get_conversation_history(
        self, conversation_id: str, limit: int = 50
    ) -> List[Dict]:
        """
        Get message history for a conversation.

        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages to return

        Returns:
            List of message documents ordered by timestamp
        """
        try:
            messages = self.db["messages"]
            cursor = (
                messages.find({"conversation_id": conversation_id})
                .sort("timestamp", 1)
                .limit(limit)
            )
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []

    async def get_recent_messages(
        self, conversation_id: str, count: int = 10
    ) -> List[Dict]:
        """
        Get the most recent messages from a conversation.

        Args:
            conversation_id: Conversation ID
            count: Number of recent messages to return

        Returns:
            List of recent message documents
        """
        try:
            messages = self.db["messages"]
            cursor = (
                messages.find({"conversation_id": conversation_id})
                .sort("timestamp", -1)
                .limit(count)
            )
            docs = await cursor.to_list(length=count)
            # Reverse to get chronological order
            return list(reversed(docs))
        except Exception as e:
            logger.error(f"Error getting recent messages: {e}")
            return []

    async def search_messages(
        self, conversation_id: str, query: str, limit: int = 20
    ) -> List[Dict]:
        """
        Search messages in a conversation.

        Args:
            conversation_id: Conversation ID
            query: Search query string
            limit: Maximum number of results

        Returns:
            List of matching message documents
        """
        try:
            messages = self.db["messages"]
            cursor = (
                messages.find(
                    {
                        "conversation_id": conversation_id,
                        "content": {"$regex": query, "$options": "i"},
                    }
                )
                .sort("timestamp", -1)
                .limit(limit)
            )
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"Error searching messages: {e}")
            return []

    # ==================== Document Operations ====================

    async def save_document(
        self, document_id: str, filename: str, status: str = "processing"
    ) -> bool:
        """
        Save document metadata.

        Args:
            document_id: Document ID
            filename: Original filename
            status: Processing status (processing, completed, failed)

        Returns:
            True if saved, False otherwise
        """
        try:
            document = {
                "_id": document_id,
                "document_id": document_id,
                "filename": filename,
                "uploaded_at": datetime.utcnow(),
                "status": status,
                "chunks_count": 0,
            }

            documents = self.db["documents"]
            await documents.insert_one(document)
            logger.info(f"Saved document: {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving document: {e}")
            return False

    async def get_document(self, document_id: str) -> Optional[Dict]:
        """Get document by ID."""
        try:
            documents = self.db["documents"]
            return await documents.find_one({"_id": document_id})
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return None

    async def get_all_documents(self, limit: int = 50) -> List[Dict]:
        """Get all documents."""
        try:
            documents = self.db["documents"]
            cursor = documents.find().sort("uploaded_at", -1).limit(limit)
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"Error getting documents: {e}")
            return []

    async def update_document_status(self, document_id: str, status: str) -> bool:
        """Update document processing status."""
        try:
            documents = self.db["documents"]
            result = await documents.update_one(
                {"_id": document_id},
                {"$set": {"status": status}},
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating document status: {e}")
            return False

    async def update_document_chunks_count(
        self, document_id: str, chunks_count: int
    ) -> bool:
        """Update document chunks count."""
        try:
            documents = self.db["documents"]
            result = await documents.update_one(
                {"_id": document_id},
                {"$set": {"chunks_count": chunks_count}},
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating document chunks count: {e}")
            return False

    async def delete_document(self, document_id: str) -> bool:
        """Delete document metadata."""
        try:
            documents = self.db["documents"]
            result = await documents.delete_one({"_id": document_id})
            logger.info(f"Deleted document: {document_id}")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False

    # ==================== Health Check ====================

    async def health_check(self) -> bool:
        """Check database connection health."""
        try:
            if self.client:
                await self.client.admin.command("ping")
                return True
            return False
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database instance
_db_instance: Optional[Database] = None


def get_database() -> Database:
    """Get global database instance."""
    global _db_instance
    if _db_instance is None:
        from backend.config import settings

        _db_instance = Database(settings.mongo_uri, settings.mongo_db_name)
    return _db_instance


async def init_database():
    """Initialize database connection (called on app startup)."""
    db = get_database()
    await db.connect()
    return db


async def close_database():
    """Close database connection (called on app shutdown)."""
    db = get_database()
    await db.disconnect()
