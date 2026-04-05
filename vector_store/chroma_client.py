#!/usr/bin/env python3
"""
ChromaDB Vector Store Client for MindLink.
Manages vector embeddings for conversation history and semantic search.
"""

import os
import logging
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime

import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)


class ChromaDBClient:
    """
    Client for ChromaDB vector database.
    Manages collections per user for conversation embeddings.
    """

    def __init__(self, persist_path: Optional[str] = None, host: Optional[str] = None,
                 port: Optional[int] = None):
        """
        Initialize ChromaDB client.

        Args:
            persist_path: Path to persist data (for persistent client)
            host: Remote host (if using client-server mode)
            port: Remote port (if using client-server mode)
        """
        self.persist_path = persist_path or os.getenv('CHROMA_DB_PATH', './chroma_db')
        self.host = host or os.getenv('CHROMA_DB_HOST')
        self.port = port or int(os.getenv('CHROMA_DB_PORT', 8000))

        try:
            if self.host:
                # Client-server mode
                self.client = chromadb.Client(Settings(
                    chroma_api_impl="rest",
                    chroma_server_host=self.host,
                    chroma_server_http_port=str(self.port)
                ))
                logger.info(f"Connected to remote ChromaDB at {self.host}:{self.port}")
            else:
                # Persistent local mode
                self.client = chromadb.PersistentClient(path=self.persist_path)
                logger.info(f"Using local ChromaDB at {self.persist_path}")

            self.collections: Dict[str, chromadb.Collection] = {}
            self.logger = logging.getLogger(__name__)

        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def get_or_create_collection(self, collection_name: str,
                                 metadata: Optional[Dict] = None) -> chromadb.Collection:
        """
        Get or create a collection.

        Args:
            collection_name: Name of the collection
            metadata: Optional metadata for the collection

        Returns:
            ChromaDB Collection object
        """
        if collection_name in self.collections:
            return self.collections[collection_name]

        try:
            # Check if collection exists
            existing = self.client.get_collection(name=collection_name)
            self.collections[collection_name] = existing
            return existing
        except Exception:
            # Collection doesn't exist, create it
            collection = self.client.create_collection(
                name=collection_name,
                metadata=metadata or {}
            )
            self.collections[collection_name] = collection
            self.logger.info(f"Created new collection: {collection_name}")
            return collection

    def get_collection(self, collection_name: str) -> Optional[chromadb.Collection]:
        """
        Get an existing collection.

        Args:
            collection_name: Name of the collection

        Returns:
            Collection object or None if not found
        """
        if collection_name in self.collections:
            return self.collections[collection_name]

        try:
            collection = self.client.get_collection(name=collection_name)
            self.collections[collection_name] = collection
            return collection
        except Exception as e:
            self.logger.warning(f"Collection not found: {collection_name} - {e}")
            return None

    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection.

        Args:
            collection_name: Name of collection to delete

        Returns:
            True if successful
        """
        try:
            self.client.delete_collection(name=collection_name)
            if collection_name in self.collections:
                del self.collections[collection_name]
            self.logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete collection {collection_name}: {e}")
            return False

    def add_to_collection(self, collection: chromadb.Collection,
                          embeddings: List[List[float]],
                          metadatas: List[Dict[str, Any]],
                          ids: Optional[List[str]] = None) -> bool:
        """
        Add embeddings to a collection.

        Args:
            collection: Target collection
            embeddings: List of embedding vectors
            metadatas: List of metadata dicts
            ids: Optional IDs (generated if not provided)

        Returns:
            True if successful
        """
        try:
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in embeddings]

            collection.add(
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            self.logger.debug(f"Added {len(embeddings)} embeddings to collection")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add embeddings: {e}")
            return False

    def search_collection(self, collection: chromadb.Collection,
                          query_embedding: List[float],
                          n_results: int = 5,
                          filter_metadata: Optional[Dict] = None) -> Dict:
        """
        Search a collection with a query embedding.

        Args:
            collection: Target collection
            query_embedding: Query vector
            n_results: Number of results to return
            filter_metadata: Optional metadata filter

        Returns:
            Search results dict
        """
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_metadata
            )
            return results

        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return {"ids": [], "distances": [], "metadatas": []}

    def get_collection_stats(self, collection_name: str) -> Dict:
        """
        Get statistics for a collection.

        Args:
            collection_name: Name of collection

        Returns:
            Dict with collection stats
        """
        collection = self.get_collection(collection_name)
        if not collection:
            return {"error": "Collection not found"}

        try:
            # Get count
            count = collection.count()

            return {
                "name": collection_name,
                "count": count,
                "metadata": collection.metadata
            }
        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}

    def list_collections(self) -> List[str]:
        """
        List all collections.

        Returns:
            List of collection names
        """
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            self.logger.error(f"Failed to list collections: {e}")
            return []

    def delete_user_data(self, user_id: str) -> bool:
        """
        Delete all data for a user (for GDPR compliance).

        Args:
            user_id: User's UUID

        Returns:
            True if successful
        """
        collection_name = f"user_{user_id}_conversations"
        return self.delete_collection(collection_name)


# Global client instance
_chroma_client: Optional[ChromaDBClient] = None


def get_chroma_client() -> ChromaDBClient:
    """Get or create the global ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = ChromaDBClient()
    return _chroma_client


def reset_chroma_client():
    """Reset the global client (for testing)."""
    global _chroma_client
    _chroma_client = None
