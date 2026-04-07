#!/usr/bin/env python3
"""
Embedding Service for MindLink.
Generates embeddings using Ollama models for vector storage and semantic search.
"""

import os
import logging
from typing import List, Optional, Dict, Any
import numpy as np

import ollama
from chromadb import Collection

from vector_store.chroma_client import get_chroma_client, ChromaDBClient

logger = logging.getLogger(__name__)

# Configuration
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'nomic-embed-text')


class EmbeddingService:
    """
    Service for generating and managing text embeddings.
    Uses Ollama for local embedding generation.
    """

    def __init__(self, chroma_client: Optional[ChromaDBClient] = None,
                 model: str = EMBEDDING_MODEL,
                 ollama_host: str = OLLAMA_HOST):
        """
        Initialize embedding service.

        Args:
            chroma_client: ChromaDB client instance
            model: Embedding model name
            ollama_host: Ollama server host
        """
        self.model = model
        self.ollama_host = ollama_host
        self.chroma_client = chroma_client or get_chroma_client()
        self.logger = logger

        # Initialize Ollama client
        self.client = ollama.Client(host=ollama_host)

        # Test connection
        try:
            self.client.list()
            self.logger.info(f"EmbeddingService connected to Ollama at {ollama_host}")
        except Exception as e:
            self.logger.warning(f"Ollama connection test failed: {e}")

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector or None if failed
        """
        try:
            response = self.client.embeddings(
                model=self.model,
                prompt=text
            )
            embedding = response.get('embedding')

            if embedding:
                return embedding
            else:
                self.logger.error("Empty embedding response from Ollama")
                return None

        except Exception as e:
            self.logger.error(f"Failed to generate embedding: {e}")
            return None

    def generate_embeddings_batch(self, texts: List[str],
                                  batch_size: int = 32) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing

        Returns:
            List of embeddings (None for failed)
        """
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            for text in batch:
                emb = self.generate_embedding(text)
                embeddings.append(emb)

        return embeddings

    def add_conversation_to_vector_store(self, user_id: str, conversation_id: str,
                                         user_message: str, assistant_response: str,
                                         metadata: Optional[Dict] = None) -> bool:
        """
        Add a conversation exchange to the vector store.

        Args:
            user_id: User's UUID
            conversation_id: Conversation UUID
            user_message: User's message text
            assistant_response: Assistant's response text
            metadata: Additional metadata

        Returns:
            True if successful
        """
        try:
            # Generate collection name
            collection_name = f"user_{user_id}_conversations"

            # Get or create collection
            collection = self.chroma_client.get_or_create_collection(
                collection_name,
                metadata={"user_id": user_id}
            )

            # Generate embeddings for both messages
            user_embedding = self.generate_embedding(user_message)
            assistant_embedding = self.generate_embedding(assistant_response)

            if not user_embedding or not assistant_embedding:
                self.logger.error("Failed to generate embeddings")
                return False

            # Prepare metadata
            base_metadata = {
                "conversation_id": conversation_id,
                "timestamp": str(np.datetime64('now')),
            }
            if metadata:
                base_metadata.update(metadata)

            # Add to collection
            import uuid
            ids = [
                f"{conversation_id}_user_{uuid.uuid4()}",
                f"{conversation_id}_assistant_{uuid.uuid4()}"
            ]

            metadatas = [
                {**base_metadata, "role": "user", "content": user_message},
                {**base_metadata, "role": "assistant", "content": assistant_response}
            ]

            self.chroma_client.add_to_collection(
                collection=collection,
                embeddings=[user_embedding, assistant_embedding],
                metadatas=metadatas,
                ids=ids
            )

            self.logger.info(f"Added conversation to vector store: {conversation_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add conversation to vector store: {e}")
            return False

    def search_relevant_conversations(self, user_id: str, query: str,
                                      n_results: int = 3) -> List[Dict]:
        """
        Search for relevant past conversations.

        Args:
            user_id: User's UUID
            query: Search query
            n_results: Number of results

        Returns:
            List of relevant conversation snippets
        """
        try:
            collection_name = f"user_{user_id}_conversations"
            collection = self.chroma_client.get_collection(collection_name)

            if not collection:
                self.logger.warning(f"Collection not found: {collection_name}")
                return []

            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            if not query_embedding:
                return []

            # Search
            results = self.chroma_client.search_collection(
                collection=collection,
                query_embedding=query_embedding,
                n_results=n_results
            )

            # Format results
            formatted_results = []
            if results.get('ids'):
                for i, id in enumerate(results['ids'][0]):
                    formatted_results.append({
                        'id': id,
                        'distance': results.get('distances', [[]])[0][i] if results.get('distances') else None,
                        'metadata': results.get('metadatas', [[]])[0][i] if results.get('metadatas') else None
                    })

            return formatted_results

        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []

    def get_user_conversation_stats(self, user_id: str) -> Dict:
        """
        Get statistics about a user's conversation history.

        Args:
            user_id: User's UUID

        Returns:
            Stats dict
        """
        try:
            collection_name = f"user_{user_id}_conversations"
            return self.chroma_client.get_collection_stats(collection_name)
        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}

    def delete_user_vectors(self, user_id: str) -> bool:
        """
        Delete all vectors for a user (GDPR compliance).

        Args:
            user_id: User's UUID

        Returns:
            True if successful
        """
        return self.chroma_client.delete_user_data(user_id)


# Global service instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get or create the global embedding service."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


def reset_embedding_service():
    """Reset the global service (for testing)."""
    global _embedding_service
    _embedding_service = None
