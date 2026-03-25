"""MongoDB database operations - placeholder for implementation."""

from typing import Optional, List
from datetime import datetime


class Database:
    """
    Database class for MongoDB operations.
    To be implemented in Checkpoint 2.
    """

    def __init__(self, mongo_uri: str, db_name: str):
        """Initialize database connection."""
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        # Connection will be initialized in Checkpoint 2

    async def connect(self):
        """Connect to MongoDB."""
        pass

    async def disconnect(self):
        """Disconnect from MongoDB."""
        pass

    async def save_message(self, conversation_id: str, role: str, content: str):
        """Save message to database."""
        pass

    async def get_conversation(self, conversation_id: str):
        """Get conversation from database."""
        pass

    async def create_conversation(self):
        """Create new conversation."""
        pass

    async def save_document(self, filename: str, document_id: str):
        """Save document metadata."""
        pass


# Global database instance
_db_instance: Optional[Database] = None


def get_database() -> Database:
    """Get database instance."""
    global _db_instance
    if _db_instance is None:
        from backend.config import settings

        _db_instance = Database(settings.mongo_uri, settings.mongo_db_name)
    return _db_instance
