"""Chat Service for message handling and conversation management."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from backend.database.mongodb import get_database
from backend.services.llm_service import get_llm_service, LLMService
from backend.services.rag_service import get_rag_service, RAGService
from backend.models.schemas import ChatMessage, ChatResponse
from backend.utils.helpers import generate_id, get_current_timestamp


class ChatService:
    """
    Service for chat operations.
    Handles message sending, conversation management, and RAG integration.
    """

    def __init__(self):
        """Initialize chat service."""
        self.db = None
        self.llm_service = None
        self.rag_service = None
        logger.info("Initialized chat service")

    async def initialize(self):
        """Initialize chat service (called on startup)."""
        try:
            self.db = await get_database()
            self.llm_service = get_llm_service()
            self.rag_service = await get_rag_service()
            logger.info("Chat service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize chat service: {e}")

    async def send_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        use_rag: bool = False,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send message and get AI response.

        Args:
            message: User message
            conversation_id: Optional conversation ID (creates new if None)
            use_rag: Whether to use RAG for context
            system_prompt: Optional system prompt override

        Returns:
            Chat response with model output
        """
        try:
            # Create or retrieve conversation
            if not conversation_id:
                conversation_id = await self.create_new_conversation()
                if not conversation_id:
                    return {"error": "Failed to create conversation"}

            logger.info(f"Processing message for conversation: {conversation_id}")

            # Prepare user message
            user_message = ChatMessage(
                role="user",
                content=message,
                timestamp=get_current_timestamp(),
            )

            # Save user message to database
            if self.db:
                await self.db.save_message(
                    conversation_id=conversation_id,
                    message=user_message.dict(),
                )

            # Get conversation history (for context)
            history = []
            if self.db:
                history_docs = await self.db.get_message_history(
                    conversation_id, limit=10
                )
                history = [
                    ChatMessage(**msg) for msg in history_docs
                ]

            # Add user message to memory
            self.llm_service.memory.add_message(
                role="user",
                content=message,
            )

            # Augment prompt with RAG if requested
            query = message
            if use_rag and self.rag_service:
                try:
                    query = await self.rag_service.augment_prompt(
                        query=message,
                        conversation_id=conversation_id,
                        top_k=5,
                    )
                    logger.debug("Augmented query with RAG context")
                except Exception as e:
                    logger.warning(f"RAG augmentation failed: {e}")

            # Generate LLM response
            try:
                response_text = await self.llm_service.generate_response(
                    query=query,
                    system_prompt=system_prompt,
                )
            except Exception as e:
                logger.error(f"LLM generation failed: {e}")
                response_text = "I apologize, but I encountered an error processing your request."

            # Create assistant message
            assistant_message = ChatMessage(
                role="assistant",
                content=response_text,
                timestamp=get_current_timestamp(),
            )

            # Save assistant message to database
            if self.db:
                await self.db.save_message(
                    conversation_id=conversation_id,
                    message=assistant_message.dict(),
                )

            # Add assistant message to memory
            self.llm_service.memory.add_message(
                role="assistant",
                content=response_text,
            )

            # Get token counts
            input_tokens = self.llm_service.count_tokens(message)
            output_tokens = self.llm_service.count_tokens(response_text)

            # Build response
            chat_response = ChatResponse(
                conversation_id=conversation_id,
                message=message,
                response=response_text,
                model=self.llm_service.model_info.get("model_name", "unknown"),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                timestamp=get_current_timestamp(),
                rag_used=use_rag,
            )

            logger.info(
                f"Message processed {input_tokens} input tokens, "
                f"{output_tokens} output tokens"
            )

            return chat_response.dict()

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {"error": str(e)}

    async def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history.

        Args:
            conversation_id: Conversation ID
            limit: Number of messages to retrieve
            offset: Offset for pagination

        Returns:
            List of messages
        """
        try:
            if not self.db:
                return []

            messages = await self.db.get_message_history(
                conversation_id=conversation_id,
                limit=limit,
                offset=offset,
            )

            return messages

        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []

    async def create_new_conversation(
        self,
        title: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> Optional[str]:
        """
        Create new conversation.

        Args:
            title: Optional conversation title
            system_prompt: Optional system prompt

        Returns:
            Conversation ID or None on error
        """
        try:
            conversation_id = generate_id()

            conversation_data = {
                "conversation_id": conversation_id,
                "title": title or "New Conversation",
                "system_prompt": system_prompt or "You are a helpful AI assistant.",
                "created_at": get_current_timestamp(),
                "updated_at": get_current_timestamp(),
                "message_count": 0,
            }

            if self.db:
                await self.db.create_conversation(conversation_data)

            # Initialize memory for this conversation
            if system_prompt:
                self.llm_service.memory.system_prompt = system_prompt

            logger.info(f"Created conversation: {conversation_id}")
            return conversation_id

        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            return None

    async def clear_conversation(self, conversation_id: str) -> bool:
        """
        Clear conversation history.

        Args:
            conversation_id: Conversation ID

        Returns:
            True if successful
        """
        try:
            if self.db:
                # Clear all messages for this conversation
                await self.db.delete_messages_for_conversation(conversation_id)

            # Reset LLM memory
            self.llm_service.memory.clear()

            logger.info(f"Cleared conversation: {conversation_id}")
            return True

        except Exception as e:
            logger.error(f"Error clearing conversation: {e}")
            return False

    async def set_system_prompt(
        self,
        conversation_id: str,
        system_prompt: str,
    ) -> bool:
        """
        Set system prompt for conversation.

        Args:
            conversation_id: Conversation ID
            system_prompt: New system prompt

        Returns:
            True if successful
        """
        try:
            if self.db:
                await self.db.update_conversation(
                    conversation_id=conversation_id,
                    updates={"system_prompt": system_prompt},
                )

            # Update memory
            self.llm_service.memory.system_prompt = system_prompt

            logger.info(f"Updated system prompt for conversation: {conversation_id}")
            return True

        except Exception as e:
            logger.error(f"Error setting system prompt: {e}")
            return False

    async def get_conversation_stats(
        self,
        conversation_id: str,
    ) -> Dict[str, Any]:
        """
        Get conversation statistics.

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation statistics
        """
        try:
            if not self.db:
                return {}

            # Get conversation data
            conversation = await self.db.get_conversation(conversation_id)
            if not conversation:
                return {}

            # Get message count
            messages = await self.db.get_message_history(
                conversation_id=conversation_id,
                limit=1000,
            )

            # Calculate stats
            total_input_tokens = 0
            total_output_tokens = 0

            for msg in messages:
                if msg.get("role") == "user":
                    total_input_tokens += self.llm_service.count_tokens(msg.get("content", ""))
                else:
                    total_output_tokens += self.llm_service.count_tokens(msg.get("content", ""))

            stats = {
                "conversation_id": conversation_id,
                "title": conversation.get("title", ""),
                "message_count": len(messages),
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "created_at": conversation.get("created_at"),
                "updated_at": conversation.get("updated_at"),
            }

            return stats

        except Exception as e:
            logger.error(f"Error getting conversation stats: {e}")
            return {}


# Global chat service instance
_chat_service_instance: Optional[ChatService] = None


async def get_chat_service() -> ChatService:
    """
    Get global chat service instance.

    Returns:
        ChatService instance
    """
    global _chat_service_instance
    if _chat_service_instance is None:
        _chat_service_instance = ChatService()
        await _chat_service_instance.initialize()
    return _chat_service_instance
