"""RAG Service for document management and retrieval."""

from typing import List, Optional, Dict, Any
import asyncio
from pathlib import Path
from loguru import logger

from backend.rag.document_processor import DocumentProcessor
from backend.rag.vector_store import get_vector_store
from backend.database.mongodb import get_database
from backend.config import settings
from backend.utils.helpers import generate_id, get_current_timestamp


class RAGService:
    """
    Retrieval-Augmented Generation service.
    Handles document uploading, processing, and retrieval.
    """

    def __init__(self):
        """Initialize RAG service."""
        self.processor = DocumentProcessor(
            chunk_size=settings.rag_chunk_size,
            chunk_overlap=settings.rag_chunk_overlap,
        )
        self.vector_store = get_vector_store()
        self.db = None
        logger.info("Initialized RAG service")

    async def initialize(self):
        """Initialize RAG service (called on startup)."""
        try:
            self.db = await get_database()
            logger.info("RAG service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")

    async def upload_document(
        self,
        file_path: str,
        document_id: str,
        conversation_id: str,
        filename: str,
    ) -> Dict[str, Any]:
        """
        Upload and process a document.

        Args:
            file_path: Path to uploaded file
            document_id: Document ID
            conversation_id: Associated conversation ID
            filename: Original filename

        Returns:
            Document metadata
        """
        try:
            logger.info(f"Processing document: {filename}")

            # Process document into text + chunks
            full_text, chunks = await self.processor.process_file(file_path)
            if not chunks:
                logger.warning(f"No chunks extracted from {filename}")
                return {"error": "Could not extract text from document"}

            # Get document statistics
            stats = self.processor.get_statistics(full_text, chunks)

            # Create collection name from conversation ID
            collection_name = f"conv_{conversation_id}"

            # Create document IDs and metadata
            doc_ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [
                {
                    "document_id": document_id,
                    "conversation_id": conversation_id,
                    "filename": filename,
                    "chunk_index": i,
                    "timestamp": get_current_timestamp(),
                }
                for i in range(len(chunks))
            ]

            # Add to vector store
            success = await self.vector_store.add_documents(
                collection_name=collection_name,
                documents=chunks,
                ids=doc_ids,
                metadatas=metadatas,
            )

            if not success:
                logger.warning("Failed to add documents to vector store")
                return {"error": "Failed to add to vector store"}

            # Save document metadata to database
            doc_meta = {
                "document_id": document_id,
                "conversation_id": conversation_id,
                "filename": filename,
                "file_type": Path(filename).suffix.lower(),
                "chunk_count": len(chunks),
                "char_count": stats.get("char_count", 0),
                "word_count": stats.get("word_count", 0),
                "status": "processed",
                "created_at": get_current_timestamp(),
                "updated_at": get_current_timestamp(),
            }

            if self.db:
                await self.db.save_document(doc_meta)

            logger.info(f"Document {document_id} processed with {len(chunks)} chunks")

            return {
                "document_id": document_id,
                "filename": filename,
                "chunk_count": len(chunks),
                "char_count": stats.get("char_count", 0),
                "word_count": stats.get("word_count", 0),
                "status": "processed",
            }

        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            return {"error": str(e)}

    async def retrieve_context(
        self,
        query: str,
        conversation_id: str,
        top_k: int = 5,
        min_similarity: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for a query.

        Args:
            query: Search query
            conversation_id: Conversation ID
            top_k: Number of results
            min_similarity: Minimum similarity threshold

        Returns:
            List of relevant documents
        """
        try:
            collection_name = f"conv_{conversation_id}"

            # Search vector store
            results = await self.vector_store.search(
                collection_name=collection_name,
                query=query,
                top_k=top_k,
                min_distance=1 - min_similarity,
            )

            # Format results
            formatted_results = [
                {
                    "content": result["document"],
                    "similarity": result["similarity"],
                    "metadata": result["metadata"],
                }
                for result in results
            ]

            logger.debug(f"Retrieved {len(formatted_results)} context chunks")
            return formatted_results

        except Exception as e:
            logger.warning(f"Error retrieving context: {e}")
            return []

    async def augment_prompt(
        self,
        query: str,
        conversation_id: str,
        top_k: int = 5,
    ) -> str:
        """
        Augment user query with retrieved context.

        Args:
            query: User query
            conversation_id: Conversation ID
            top_k: Number of context chunks to retrieve

        Returns:
            Augmented prompt with context
        """
        try:
            # Retrieve relevant documents
            context_docs = await self.retrieve_context(
                query=query,
                conversation_id=conversation_id,
                top_k=top_k,
            )

            if not context_docs:
                logger.debug("No context documents found for augmentation")
                return query

            # Build augmented prompt
            context_text = "\n\n".join(
                [f"[Context {i+1}]:\n{doc['content']}" 
                 for i, doc in enumerate(context_docs)]
            )

            augmented = f"""Based on the following context:

{context_text}

User Question: {query}

Provide a helpful response based on the context above."""

            return augmented

        except Exception as e:
            logger.warning(f"Error augmenting prompt: {e}")
            return query

    async def get_conversation_documents(
        self,
        conversation_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Get all documents for a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            List of documents
        """
        try:
            if not self.db:
                return []

            documents = await self.db.get_documents(conversation_id)
            return documents

        except Exception as e:
            logger.error(f"Error getting conversation documents: {e}")
            return []

    async def delete_document_from_rag(
        self,
        document_id: str,
        conversation_id: str,
    ) -> bool:
        """
        Delete document from RAG system.

        Args:
            document_id: Document ID
            conversation_id: Conversation ID

        Returns:
            True if successful
        """
        try:
            collection_name = f"conv_{conversation_id}"

            # Delete from vector store
            chunk_ids = [f"{document_id}_chunk_{i}" for i in range(100)]
            for chunk_id in chunk_ids:
                await self.vector_store.delete_document(
                    collection_name=collection_name,
                    document_id=chunk_id,
                )

            logger.info(f"Deleted document {document_id} from RAG")
            return True

        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False

    async def get_rag_stats(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get RAG statistics for a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            RAG statistics
        """
        try:
            collection_name = f"conv_{conversation_id}"

            stats = await self.vector_store.get_collection_stats(collection_name)

            if self.db:
                documents = await self.get_conversation_documents(conversation_id)
                stats["total_documents"] = len(documents)
                stats["total_size_bytes"] = sum(
                    d.get("char_count", 0) for d in documents
                )

            return stats

        except Exception as e:
            logger.warning(f"Error getting RAG stats: {e}")
            return {}


# Global RAG service instance
_rag_service_instance: Optional[RAGService] = None


async def get_rag_service() -> RAGService:
    """
    Get global RAG service instance.

    Returns:
        RAGService instance
    """
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
        await _rag_service_instance.initialize()
    return _rag_service_instance
