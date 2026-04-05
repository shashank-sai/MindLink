#!/usr/bin/env python3
"""
Vector-Aware Context Engine for MindLink.
Extends the base ContextEngine with vector database integration for long-term memory.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID

from core.context_engine import ContextEngine
from vector_store.embedding_service import EmbeddingService, get_embedding_service
from vector_store.chroma_client import get_chroma_client

logger = logging.getLogger(__name__)


class VectorAwareContextEngine(ContextEngine):
    """
    Enhanced ContextEngine with vector database integration.
    Provides:
    - Short-term memory: In-memory conversation history (last 10 exchanges)
    - Long-term memory: Vector-stored conversation history with semantic search
    - Contextual retrieval: Find relevant past conversations based on current input
    """

    def __init__(self, user_id: str, conversation_id: Optional[str] = None,
                 embedding_service: Optional[EmbeddingService] = None,
                 max_history: int = 10):
        """
        Initialize vector-aware context engine.

        Args:
            user_id: User's UUID
            conversation_id: Current conversation UUID
            embedding_service: Embedding service instance
            max_history: Max in-memory history size
        """
        super().__init__(max_history=max_history)

        self.user_id = user_id
        self.conversation_id = conversation_id
        self.embedding_service = embedding_service or get_embedding_service()
        self.logger = logger

        # Track if we've initialized the collection
        self._collection_initialized = False

        self.logger.info(
            f"VectorAwareContextEngine initialized for user {user_id} "
            f"(conversation: {conversation_id})"
        )

    def _ensure_collection(self):
        """Ensure the user's vector collection exists."""
        if not self._collection_initialized:
            try:
                collection_name = f"user_{self.user_id}_conversations"
                self.collection = self.embedding_service.chroma_client.get_or_create_collection(
                    collection_name,
                    metadata={"user_id": self.user_id}
                )
                self._collection_initialized = True
                self.logger.debug(f"Vector collection ready: {collection_name}")
            except Exception as e:
                self.logger.error(f"Failed to initialize vector collection: {e}")
                self.collection = None

    def add_exchange(self, user_input: str, mindlink_response: str):
        """
        Add a conversation exchange to both short-term and long-term memory.

        Args:
            user_input: User's message
            mindlink_response: System's response
        """
        # Add to short-term memory (in-memory)
        super().add_exchange(user_input, mindlink_response)

        # Add to long-term memory (vector store)
        if self.conversation_id:
            self._store_in_vector_db(user_input, mindlink_response)

    def _store_in_vector_db(self, user_input: str, mindlink_response: str):
        """
        Store conversation in vector database.

        Args:
            user_input: User's message
            mindlink_response: System's response
        """
        try:
            self._ensure_collection()

            metadata = {
                "conversation_id": str(self.conversation_id),
                "timestamp": datetime.now().isoformat(),
                "user_id": str(self.user_id)
            }

            self.embedding_service.add_conversation_to_vector_store(
                user_id=str(self.user_id),
                conversation_id=str(self.conversation_id),
                user_message=user_input,
                assistant_response=mindlink_response,
                metadata=metadata
            )

        except Exception as e:
            self.logger.error(f"Failed to store in vector DB: {e}")

    def get_relevant_history(self, query: str, n_results: int = 3) -> List[Dict]:
        """
        Get semantically relevant past conversations.

        Args:
            query: Search query (usually current user input)
            n_results: Number of results to return

        Returns:
            List of relevant conversation exchanges
        """
        try:
            results = self.embedding_service.search_relevant_conversations(
                user_id=str(self.user_id),
                query=query,
                n_results=n_results
            )
            return results
        except Exception as e:
            self.logger.error(f"Failed to search vector DB: {e}")
            return []

    def get_contextual_response(self, current_input: str) -> Dict[str, Any]:
        """
        Get response context combining recent history and relevant past conversations.

        Args:
            current_input: Current user input

        Returns:
            Dict with:
            - recent: Recent in-memory exchanges
            - relevant: Semantically relevant past conversations
            - combined_context: Formatted context string for LLM
        """
        # Get recent in-memory history
        recent_history = self.get_recent_history(count=3)

        # Get semantically relevant history
        relevant_results = self.get_relevant_history(current_input, n_results=2)

        # Format for LLM
        context_parts = []

        # Add recent context
        if recent_history:
            context_parts.append("Recent conversation:")
            for exchange in recent_history:
                context_parts.append(f"  User: {exchange.get('user', '')}")
                context_parts.append(f"  Assistant: {exchange.get('mindlink', '')}")

        # Add relevant historical context
        if relevant_results:
            context_parts.append("\nRelevant past conversations:")
            for result in relevant_results:
                meta = result.get('metadata', {})
                if meta:
                    context_parts.append(f"  [{meta.get('timestamp', '')}]")
                    context_parts.append(f"  User: {meta.get('content', '')}")
                    # Get assistant response from same conversation if available
                    if 'response' in meta:
                        context_parts.append(f"  Assistant: {meta.get('response', '')}")

        combined_context = "\n".join(context_parts)

        return {
            "recent": recent_history,
            "relevant": relevant_results,
            "combined_context": combined_context,
            "has_long_term_memory": len(relevant_results) > 0
        }

    def get_conversation_history_for_llm(self, current_input: str) -> str:
        """
        Get formatted conversation history for LLM prompt.

        Args:
            current_input: Current user input

        Returns:
            Formatted history string
        """
        context = self.get_contextual_response(current_input)
        return context["combined_context"]

    def set_conversation_id(self, conversation_id: str):
        """
        Set the current conversation ID.

        Args:
            conversation_id: New conversation UUID
        """
        self.conversation_id = conversation_id
        self.logger.info(f"Conversation ID set to: {conversation_id}")

    def get_session_info(self) -> Dict:
        """
        Get extended session information including vector store stats.

        Returns:
            Dict with session information
        """
        base_info = super().get_session_info()

        # Add vector store stats
        try:
            stats = self.embedding_service.get_user_conversation_stats(
                str(self.user_id)
            )
            base_info["vector_store"] = stats
        except Exception as e:
            self.logger.error(f"Failed to get vector stats: {e}")
            base_info["vector_store"] = {"error": str(e)}

        return base_info

    def clear_history(self):
        """Clear short-term memory (in-memory history)."""
        super().clear_history()
        self.logger.info("Short-term memory cleared")

    def clear_long_term_memory(self):
        """Clear long-term memory (vector store)."""
        try:
            self.embedding_service.delete_user_vectors(str(self.user_id))
            self._collection_initialized = False
            self.logger.info("Long-term memory cleared")
        except Exception as e:
            self.logger.error(f"Failed to clear long-term memory: {e}")

    def __del__(self):
        """Cleanup."""
        try:
            self.embedding_service = None
        except:
            pass


class ContextualConversationManager:
    """
    Manages conversations with context awareness.
    Handles conversation creation, switching, and context retrieval.
    """

    def __init__(self, user_id: str):
        """
        Initialize conversation manager.

        Args:
            user_id: User's UUID
        """
        self.user_id = user_id
        self.current_conversation_id: Optional[str] = None
        self.context_engine: Optional[VectorAwareContextEngine] = None
        self.logger = logger

    def start_new_conversation(self) -> str:
        """
        Start a new conversation.

        Returns:
            New conversation ID
        """
        import uuid
        self.current_conversation_id = str(uuid.uuid4())
        self.context_engine = VectorAwareContextEngine(
            user_id=str(self.user_id),
            conversation_id=self.current_conversation_id
        )
        self.logger.info(f"New conversation started: {self.current_conversation_id}")
        return self.current_conversation_id

    def get_context_engine(self) -> Optional[VectorAwareContextEngine]:
        """Get current context engine."""
        return self.context_engine

    def switch_conversation(self, conversation_id: str):
        """
        Switch to a different conversation.

        Args:
            conversation_id: Conversation UUID to switch to
        """
        self.current_conversation_id = conversation_id
        if self.context_engine:
            self.context_engine.set_conversation_id(conversation_id)
        self.logger.info(f"Switched to conversation: {conversation_id}")

    def get_context_for_response(self, user_input: str) -> Dict:
        """
        Get context for generating a response.

        Args:
            user_input: Current user input

        Returns:
            Context dict with recent and relevant history
        """
        if not self.context_engine:
            self.start_new_conversation()

        return self.context_engine.get_contextual_response(user_input)
