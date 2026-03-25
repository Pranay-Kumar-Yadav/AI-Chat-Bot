"""Vector store for RAG using ChromaDB."""

from typing import List, Optional, Dict, Any
import chromadb
from chromadb.config import Settings
from pathlib import Path
from loguru import logger

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning("sentence-transformers not installed, embeddings disabled")

from backend.config import settings


class VectorStore:
    """
    Vector store for embeddings using ChromaDB.
    Handles document storage, retrieval, and similarity search.
    """

    def __init__(self, db_path: str = None, model_name: str = None):
        """
        Initialize vector store.

        Args:
            db_path: Path to ChromaDB database
            model_name: Name of embedding model to use
        """
        self.db_path = db_path or settings.chroma_db_path
        self.model_name = model_name or settings.embedding_model

        # Create database directory if needed
        Path(self.db_path).mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        chroma_settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=self.db_path,
            anonymized_telemetry=False,
        )

        self.client = chromadb.Client(chroma_settings)
        logger.info(f"Initialized ChromaDB at {self.db_path}")

        # Initialize embedding model
        if EMBEDDINGS_AVAILABLE:
            try:
                self.embedder = SentenceTransformer(self.model_name)
                logger.info(f"Loaded embedding model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to load embedding model: {e}")
                self.embedder = None
        else:
            self.embedder = None
            logger.warning("Embeddings not available - install sentence-transformers")

        # Get or create collections
        self.collection = None

    async def create_collection(self, collection_name: str) -> bool:
        """
        Create or get a collection.

        Args:
            collection_name: Name of the collection

        Returns:
            True if successful
        """
        try:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Created/retrieved collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            return False

    async def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        ids: Optional[List[str]] = None,
        metadatas: Optional[List[Dict]] = None,
    ) -> bool:
        """
        Add documents to vector store.

        Args:
            collection_name: Collection name
            documents: List of document texts
            ids: Optional list of document IDs
            metadatas: Optional metadata for each document

        Returns:
            True if successful
        """
        try:
            if not self.embedder:
                logger.warning("Embedder not available, skipping embedding")
                return False

            if not ids:
                ids = [f"doc_{i}" for i in range(len(documents))]

            if not metadatas:
                metadatas = [{"source": "uploaded"} for _ in documents]

            # Get collection
            collection = self.client.get_or_create_collection(name=collection_name)

            # Generate embeddings
            embeddings = self.embedder.encode(documents).tolist()

            # Add to collection
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )

            logger.info(f"Added {len(documents)} documents to {collection_name}")
            return True

        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False

    async def search(
        self,
        collection_name: str,
        query: str,
        top_k: int = 5,
        min_distance: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            collection_name: Collection name
            query: Search query
            top_k: Number of results to return
            min_distance: Minimum similarity distance

        Returns:
            List of matching documents
        """
        try:
            if not self.embedder:
                logger.warning("Embedder not available")
                return []

            # Get collection
            collection = self.client.get_collection(name=collection_name)

            # Generate query embedding
            query_embedding = self.embedder.encode(query).tolist()

            # Search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
            )

            # Format results
            documents = results.get("documents", [[]])[0]
            distances = results.get("distances", [[]])[0]
            ids = results.get("ids", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]

            formatted_results = []
            for doc, distance, doc_id, metadata in zip(documents, distances, ids, metadatas):
                # Calculate similarity from distance
                similarity = 1 - distance if distance else 0
                
                if similarity >= min_distance:
                    formatted_results.append({
                        "id": doc_id,
                        "document": doc,
                        "similarity": similarity,
                        "distance": distance,
                        "metadata": metadata,
                    })

            logger.debug(f"Found {len(formatted_results)} results for query")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []

    async def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection.

        Args:
            collection_name: Collection name

        Returns:
            True if successful
        """
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            return False

    async def delete_document(self, collection_name: str, document_id: str) -> bool:
        """
        Delete a specific document from collection.

        Args:
            collection_name: Collection name
            document_id: Document ID to delete

        Returns:
            True if successful
        """
        try:
            collection = self.client.get_collection(name=collection_name)
            collection.delete(ids=[document_id])
            logger.info(f"Deleted document {document_id} from {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False

    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Get collection statistics.

        Args:
            collection_name: Collection name

        Returns:
            Collection statistics
        """
        try:
            collection = self.client.get_collection(name=collection_name)
            count = collection.count()

            return {
                "collection_name": collection_name,
                "document_count": count,
                "embedding_model": self.model_name,
                "embedding_dimension": 384 if "minilm" in self.model_name.lower() else 768,
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}

    def persist(self):
        """Persist vector store to disk."""
        try:
            self.client.persist()
            logger.info("Vector store persisted to disk")
        except Exception as e:
            logger.warning(f"Could not persist vector store: {e}")


# Global vector store instance
_vector_store_instance: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """
    Get global vector store instance.

    Returns:
        VectorStore instance
    """
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance
