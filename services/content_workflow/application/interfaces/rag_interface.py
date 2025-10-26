"""RAG (Retrieval-Augmented Generation) interface."""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class RAGDocument:
    """Document in RAG system."""

    id: str
    content: str
    metadata: Dict[str, Any]
    score: Optional[float] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


@dataclass
class RAGQuery:
    """Query for RAG system."""

    query: str
    client_profile: Optional[str] = None
    document_types: List[str] = None
    max_results: int = 5
    min_score: float = 0.0
    metadata_filters: Dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.document_types is None:
            self.document_types = []
        if self.metadata_filters is None:
            self.metadata_filters = {}


@dataclass
class RAGResponse:
    """Response from RAG system."""

    documents: List[RAGDocument]
    query: str
    total_results: int
    processing_time_ms: float
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}

    def get_combined_content(self, separator: str = "\n\n") -> str:
        """Get all document content combined."""
        return separator.join(doc.content for doc in self.documents)

    def get_top_documents(self, n: int) -> List[RAGDocument]:
        """Get top N documents by score."""
        sorted_docs = sorted(self.documents, key=lambda x: x.score or 0.0, reverse=True)
        return sorted_docs[:n]


class RAGInterface(ABC):
    """
    Abstract interface for RAG (Retrieval-Augmented Generation) systems.

    This interface defines the contract for retrieving relevant information
    from knowledge bases to augment content generation.
    """

    @abstractmethod
    async def query(self, rag_query: RAGQuery) -> RAGResponse:
        """
        Query the RAG system for relevant documents.

        Args:
            rag_query: The RAG query with parameters

        Returns:
            RAG response with relevant documents
        """
        pass

    @abstractmethod
    async def add_document(
        self,
        content: str,
        metadata: Dict[str, Any],
        client_profile: Optional[str] = None,
    ) -> str:
        """
        Add a document to the RAG system.

        Args:
            content: Document content
            metadata: Document metadata
            client_profile: Client profile for organization

        Returns:
            Document ID
        """
        pass

    @abstractmethod
    async def update_document(
        self,
        document_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update an existing document.

        Args:
            document_id: Document ID to update
            content: New content (if provided)
            metadata: New metadata (if provided)

        Returns:
            True if updated successfully
        """
        pass

    @abstractmethod
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the RAG system.

        Args:
            document_id: Document ID to delete

        Returns:
            True if deleted successfully
        """
        pass

    @abstractmethod
    async def get_document(self, document_id: str) -> Optional[RAGDocument]:
        """
        Get a specific document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document if found, None otherwise
        """
        pass

    @abstractmethod
    async def list_documents(
        self, client_profile: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[RAGDocument]:
        """
        List documents in the RAG system.

        Args:
            client_profile: Filter by client profile
            limit: Maximum number of documents to return
            offset: Number of documents to skip

        Returns:
            List of documents
        """
        pass

    @abstractmethod
    async def get_client_knowledge(self, client_profile: str) -> RAGResponse:
        """
        Get all knowledge for a specific client profile.

        Args:
            client_profile: Client profile name

        Returns:
            RAG response with all client documents
        """
        pass

    @abstractmethod
    async def search_similar(
        self, content: str, client_profile: Optional[str] = None, max_results: int = 5
    ) -> RAGResponse:
        """
        Search for documents similar to given content.

        Args:
            content: Content to find similar documents for
            client_profile: Filter by client profile
            max_results: Maximum number of results

        Returns:
            RAG response with similar documents
        """
        pass

    @abstractmethod
    async def create_client_collection(self, client_profile: str) -> bool:
        """
        Create a new collection for a client profile.

        Args:
            client_profile: Client profile name

        Returns:
            True if created successfully
        """
        pass

    @abstractmethod
    async def delete_client_collection(self, client_profile: str) -> bool:
        """
        Delete a client collection and all its documents.

        Args:
            client_profile: Client profile name

        Returns:
            True if deleted successfully
        """
        pass

    @abstractmethod
    async def get_collection_stats(self, client_profile: str) -> Dict[str, Any]:
        """
        Get statistics for a client collection.

        Args:
            client_profile: Client profile name

        Returns:
            Collection statistics
        """
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Check RAG system health.

        Returns:
            Health status information
        """
        pass
