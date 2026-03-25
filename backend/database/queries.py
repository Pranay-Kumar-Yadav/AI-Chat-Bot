"""Extended database operations for conversations."""

from motor.motor_asyncio import AsyncDatabase
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger


class ConversationQueries:
    """Conversation-related database queries."""

    @staticmethod
    async def get_user_conversations(
        db: AsyncDatabase, limit: int = 50, skip: int = 0
    ) -> List[Dict]:
        """Get all user conversations with pagination."""
        try:
            conversations = db["conversations"]
            cursor = (
                conversations.find()
                .sort("updated_at", -1)
                .skip(skip)
                .limit(limit)
            )
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"Error getting user conversations: {e}")
            return []

    @staticmethod
    async def get_conversation_stats(db: AsyncDatabase, conversation_id: str) -> Dict:
        """Get conversation statistics."""
        try:
            conversations = db["conversations"]
            conv = await conversations.find_one({"_id": conversation_id})
            if not conv:
                return {}

            messages = db["messages"]
            message_stats = await messages.aggregate(
                [
                    {"$match": {"conversation_id": conversation_id}},
                    {
                        "$group": {
                            "_id": "$role",
                            "count": {"$sum": 1},
                            "total_tokens": {"$sum": "$tokens_used"},
                        }
                    },
                ]
            ).to_list(None)

            return {
                "conversation_id": conversation_id,
                "title": conv.get("title"),
                "created_at": conv.get("created_at"),
                "updated_at": conv.get("updated_at"),
                "message_count": conv.get("message_count", 0),
                "message_stats": message_stats,
            }
        except Exception as e:
            logger.error(f"Error getting conversation stats: {e}")
            return {}

    @staticmethod
    async def clear_old_conversations(db: AsyncDatabase, days: int = 30) -> int:
        """Clear conversations older than specified days."""
        try:
            conversations = db["conversations"]
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            result = await conversations.delete_many(
                {"updated_at": {"$lt": cutoff_date}}
            )

            logger.info(f"Deleted {result.deleted_count} old conversations")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error clearing old conversations: {e}")
            return 0


class MessageQueries:
    """Message-related database queries."""

    @staticmethod
    async def get_message_count(db: AsyncDatabase, conversation_id: str) -> int:
        """Get total message count for a conversation."""
        try:
            messages = db["messages"]
            return await messages.count_documents(
                {"conversation_id": conversation_id}
            )
        except Exception as e:
            logger.error(f"Error getting message count: {e}")
            return 0

    @staticmethod
    async def get_total_tokens(db: AsyncDatabase, conversation_id: str) -> int:
        """Get total tokens used in a conversation."""
        try:
            messages = db["messages"]
            result = await messages.aggregate(
                [
                    {"$match": {"conversation_id": conversation_id}},
                    {"$group": {"_id": None, "total": {"$sum": "$tokens_used"}}},
                ]
            ).to_list(1)

            return result[0]["total"] if result else 0
        except Exception as e:
            logger.error(f"Error getting total tokens: {e}")
            return 0

    @staticmethod
    async def export_conversation(
        db: AsyncDatabase, conversation_id: str
    ) -> Dict[str, Any]:
        """Export entire conversation as JSON."""
        try:
            conversations = db["conversations"]
            conv = await conversations.find_one({"_id": conversation_id})

            if not conv:
                return {}

            messages = db["messages"]
            msgs = await messages.find(
                {"conversation_id": conversation_id}
            ).sort("timestamp", 1).to_list(None)

            return {
                "conversation": conv,
                "messages": msgs,
            }
        except Exception as e:
            logger.error(f"Error exporting conversation: {e}")
            return {}
