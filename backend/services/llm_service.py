"""LLM service for OpenAI integration with LangChain."""

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ChatMessageHistory
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import List, Optional, Tuple
from loguru import logger

from backend.config import settings


class ConversationMemory:
    """
    Manages conversation memory for each conversation.
    Stores recent messages from database for context.
    """

    def __init__(self, conversation_id: str, system_prompt: str = ""):
        """
        Initialize conversation memory.

        Args:
            conversation_id: Unique conversation ID
            system_prompt: System prompt for the conversation
        """
        self.conversation_id = conversation_id
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        self.messages: List[dict] = []

    def add_message(self, role: str, content: str):
        """
        Add a message to memory.

        Args:
            role: Message role (user, assistant)
            content: Message content
        """
        self.messages.append({"role": role, "content": content})

    def add_messages_from_history(self, history: List[dict]):
        """
        Load messages from database history.

        Args:
            history: List of message documents from database
        """
        for msg in history:
            self.messages.append({
                "role": msg.get("role"),
                "content": msg.get("content")
            })

    def get_messages_for_api(self) -> List[dict]:
        """
        Get messages formatted for OpenAI API.

        Returns:
            List of messages with system prompt
        """
        # Start with system prompt
        api_messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add all messages from memory
        api_messages.extend(self.messages)
        
        return api_messages

    def get_context_string(self) -> str:
        """
        Get conversation context as a string.

        Returns:
            Formatted conversation history
        """
        context = f"System: {self.system_prompt}\n\n"
        for msg in self.messages:
            context += f"{msg['role'].upper()}: {msg['content']}\n\n"
        return context

    def clear(self):
        """Clear all messages from memory."""
        self.messages = []


class LLMService:
    """
    Service for Large Language Model operations.
    Handles OpenAI API calls with LangChain.
    """

    def __init__(self):
        """Initialize LLM service."""
        try:
            self.llm = ChatOpenAI(
                model_name=settings.model_name,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                openai_api_key=settings.openai_api_key,
                streaming=False,
            )
            logger.info(f"Initialized LLM: {settings.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise

    async def generate_response(
        self,
        user_message: str,
        memory: ConversationMemory,
        use_rag_context: Optional[str] = None,
    ) -> Tuple[str, int]:
        """
        Generate AI response using OpenAI.

        Args:
            user_message: User's message
            memory: Conversation memory with history
            use_rag_context: Optional RAG context to augment prompt

        Returns:
            Tuple of (response_message, tokens_used)
        """
        try:
            # Add user message to memory
            memory.add_message("user", user_message)

            # Build messages for API
            messages = memory.get_messages_for_api()

            # If RAG context provided, augment the system prompt
            if use_rag_context:
                messages[0] = {
                    "role": "system",
                    "content": (
                        f"{messages[0]['content']}\n\n"
                        f"Use the following document context to answer the question:\n"
                        f"{use_rag_context}"
                    )
                }
                logger.debug("Using RAG context for response generation")

            # Call OpenAI API
            response = await self._call_openai_async(messages)

            # Extract response text and tokens
            response_text = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            tokens_used = response.get("usage", {}).get("total_tokens", 0)

            if not response_text:
                raise ValueError("Empty response from OpenAI")

            # Add assistant response to memory
            memory.add_message("assistant", response_text)

            logger.debug(f"Generated response ({tokens_used} tokens) for conversation")

            return response_text, tokens_used

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    async def _call_openai_async(self, messages: List[dict]) -> dict:
        """
        Call OpenAI API asynchronously.

        Args:
            messages: List of messages in OpenAI format

        Returns:
            API response dictionary
        """
        import aiohttp
        import json

        try:
            headers = {
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": settings.model_name,
                "messages": messages,
                "temperature": settings.temperature,
                "max_tokens": settings.max_tokens,
                "top_p": settings.top_p,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise Exception(f"OpenAI API error: {error_data}")
                    
                    return await response.json()

        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            raise

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Args:
            text: Text to count tokens for

        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token
        return len(text) // 4

    async def stream_response(
        self,
        user_message: str,
        memory: ConversationMemory,
        use_rag_context: Optional[str] = None,
    ):
        """
        Generate response with streaming.

        Args:
            user_message: User's message
            memory: Conversation memory
            use_rag_context: Optional RAG context

        Yields:
            Response text chunks
        """
        try:
            # Note: Streaming will be fully implemented in Checkpoint 4+
            # For now, using regular non-streaming to maintain compatibility
            response, _ = await self.generate_response(
                user_message, memory, use_rag_context
            )
            yield response

        except Exception as e:
            logger.error(f"Error streaming response: {e}")
            raise

    def get_model_info(self) -> dict:
        """
        Get information about the configured LLM.

        Returns:
            Dictionary with model information
        """
        return {
            "model_name": settings.model_name,
            "temperature": settings.temperature,
            "max_tokens": settings.max_tokens,
            "top_p": settings.top_p,
            "embedding_model": settings.embedding_model,
        }


# Global LLM service instance
_llm_service_instance: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """
    Get global LLM service instance.

    Returns:
        LLMService instance
    """
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance
