"""RAG (Retrieval-Augmented Generation) tool implementation."""

import logging
import time
from typing import Dict, Any, List, Optional

from ..database.supabase_tracker import SupabaseTracker
from core.infrastructure.config.settings import get_settings

try:  # Optional dependency for embeddings
    import openai  # type: ignore
except Exception:  # pragma: no cover
    openai = None

logger = logging.getLogger(__name__)


class RAGTool:
    """RAG tool for retrieving and processing knowledge base content using Supabase."""

    def __init__(self, tracker: Optional[SupabaseTracker] = None, run_id: Optional[str] = None):
        self.tracker = tracker
        self.run_id = run_id
        if tracker:
            self.supabase = tracker.client
        else:
            self.supabase = self._init_supabase_client()

    def _init_supabase_client(self):
        """Create a Supabase client if configuration is available."""
        try:
            settings = get_settings()
            if settings.supabase_url and settings.supabase_anon_key:
                tracker = SupabaseTracker()
                return tracker.client
        except Exception as e:  # pragma: no cover
            logger.warning(f"Supabase client not initialized: {e}")
        return None

    def set_run(self, run_id: str, tracker: SupabaseTracker) -> None:
        self.run_id = run_id
        self.tracker = tracker
        self.supabase = tracker.client
    
    async def get_client_content(
        self,
        client_name: str,
        document_name: Optional[str] = None,
        agent_name: Optional[str] = None,
    ) -> str:
        """
        Retrieve content from client's knowledge base.

        Args:
            client_name: Name of the client
            document_name: Specific document name (optional)

        Returns:
            Retrieved content as formatted string
        """
        start_time = time.time()

        logger.info(f"🔍 RAG RETRIEVAL: Accessing knowledge base for client '{client_name}'")

        if not client_name:
            error_msg = "No client specified for RAG content retrieval"
            logger.warning(f"⚠️ RAG WARNING: {error_msg}")
            return error_msg

        if self.supabase is None:
            error_msg = "Supabase client not configured"
            logger.warning(f"⚠️ RAG WARNING: {error_msg}")
            return error_msg

        try:
            client_res = (
                self.supabase.table("clients")
                .select("id")
                .eq("name", client_name)
                .single()
                .execute()
            )
            client_data = client_res.data
            if not client_data:
                error_msg = f"Client '{client_name}' not found"
                logger.warning(f"⚠️ RAG WARNING: {error_msg}")
                return error_msg

            client_id = client_data["id"]

            if document_name:
                logger.info(f"📄 RAG: Retrieving specific document '{document_name}' for {client_name}")
                result = await self._get_specific_document(client_id, client_name, document_name, agent_name)
            else:
                logger.info(f"📚 RAG: Retrieving all content for {client_name}")
                result = await self._get_all_client_content(client_id, client_name, agent_name)

            duration_ms = (time.time() - start_time) * 1000
            content_length = len(result)
            logger.info(f"✅ RAG SUCCESS: Retrieved {content_length} characters in {duration_ms:.2f}ms")
            return result

        except Exception as e:  # pragma: no cover
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"❌ RAG ERROR: Failed to retrieve content for {client_name}: {str(e)} ({duration_ms:.2f}ms)")
            return f"Error retrieving content: {str(e)}"
    
    async def _get_specific_document(self, client_id: str, client_name: str, document_name: str, agent_name: Optional[str] = None) -> str:
        """Retrieve a specific document from Supabase."""

        if self.supabase is None:
            return "Supabase client not configured"

        try:
            doc_res = (
                self.supabase.table("documents")
                .select("id,title,content,file_path")
                .eq("client_id", client_id)
                .eq("title", document_name)
                .single()
                .execute()
            )
            doc = doc_res.data
            if not doc:
                return f"Document '{document_name}' not found"

            if self.tracker and self.run_id:
                self.tracker.log_rag_document(
                    self.run_id,
                    client_name,
                    doc.get("file_path") or doc.get("title"),
                    agent_name=agent_name,
                )
            return doc.get("content", "")
        except Exception as e:  # pragma: no cover
            logger.error(f"Error retrieving document {document_name}: {e}")
            return f"Error retrieving document: {e}"
    
    async def _get_all_client_content(self, client_id: str, client_name: str, agent_name: Optional[str] = None) -> str:
        """Retrieve and categorize all documents for a client from Supabase."""

        if self.supabase is None:
            return "Supabase client not configured"

        try:
            docs_res = (
                self.supabase.table("documents")
                .select("id,title,content,file_path")
                .eq("client_id", client_id)
                .execute()
            )
            docs = docs_res.data or []
        except Exception as e:  # pragma: no cover
            logger.error(f"Error retrieving documents for {client_name}: {e}")
            return f"Error retrieving documents: {e}"

        if self.tracker and self.run_id:
            for doc in docs:
                self.tracker.log_rag_document(
                    self.run_id,
                    client_name,
                    doc.get("file_path") or doc.get("title"),
                    agent_name=agent_name,
                )

        company_info: List[tuple[str, str]] = []
        guidelines: List[tuple[str, str]] = []
        knowledge_base: List[tuple[str, str]] = []
        other_docs: List[tuple[str, str]] = []

        for doc in docs:
            doc_name = str(doc.get("title", "")).lower()
            content = doc.get("content", "")

            if any(term in doc_name for term in [
                "company", "about", "profile", "overview", "brand"
            ]):
                company_info.append((doc_name, content))
            elif any(term in doc_name for term in [
                "guideline", "guide", "best_practice", "best-practice",
                "rule", "instruction", "style"
            ]):
                guidelines.append((doc_name, content))
            elif any(term in doc_name for term in [
                "knowledge", "kb", "reference", "detail", "info"
            ]):
                knowledge_base.append((doc_name, content))
            else:
                other_docs.append((doc_name, content))

        formatted_output: List[str] = []

        if company_info:
            formatted_output.append(
                """## COMPANY INFORMATION

The following documents contain essential information about the company, its brand, and positioning.
This information should be reflected in all content creation.
"""
            )
            for doc_name, content in company_info:
                formatted_output.append(f"### {doc_name}\n\n{content}\n\n")

        if guidelines:
            formatted_output.append(
                """\n## CONTENT GUIDELINES

The following documents contain guidelines and best practices for content creation.
These should be strictly followed when generating content.
"""
            )
            for doc_name, content in guidelines:
                formatted_output.append(f"### {doc_name}\n\n{content}\n\n")

        if knowledge_base:
            formatted_output.append(
                """\n## KNOWLEDGE BASE

The following documents contain detailed knowledge that can be referenced and incorporated into content.
Use this information as needed to enhance content accuracy and depth.
"""
            )
            for doc_name, content in knowledge_base:
                formatted_output.append(f"### {doc_name}\n\n{content}\n\n")

        if other_docs:
            formatted_output.append(
                """\n## OTHER DOCUMENTS

The following documents contain additional information that may be relevant to content creation.
"""
            )
            for doc_name, content in other_docs:
                formatted_output.append(f"### {doc_name}\n\n{content}\n\n")

        if not formatted_output:
            return f"No documents found for client '{client_name}'"

        return "\n\n".join(formatted_output)
    
    async def get_available_documents(self, client_name: str) -> List[str]:
        """
        Get list of available documents for a client.
        
        Args:
            client_name: Name of the client
            
        Returns:
            List of available document names
        """
        if not client_name or self.supabase is None:
            return []

        try:
            client_res = (
                self.supabase.table("clients")
                .select("id")
                .eq("name", client_name)
                .single()
                .execute()
            )
            client_data = client_res.data
            if not client_data:
                return []

            docs_res = (
                self.supabase.table("documents")
                .select("title")
                .eq("client_id", client_data["id"])
                .execute()
            )
            docs = docs_res.data or []
            return [d["title"] for d in docs]
        except Exception as e:  # pragma: no cover
            logger.warning(f"Error getting documents for {client_name}: {e}")
            return []
    
    async def search_content(
        self,
        client_name: str,
        query: str,
        max_results: int = 5,
        agent_name: Optional[str] = None,
    ) -> str:
        """
        Search for content within client's knowledge base.
        
        Args:
            client_name: Name of the client
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            Search results as formatted string
        """
        if not client_name or not query:
            return "Client name and search query are required"

        if self.supabase is None:
            return "Supabase client not configured"

        try:
            embedding = self._embed_text(query)
            response = self.supabase.rpc(
                "match_documents",
                {
                    "query_embedding": embedding,
                    "match_count": max_results,
                    "client_name": client_name,
                },
            ).execute()
            matches = response.data or []
            if not matches:
                return f"No results found for query '{query}' in {client_name}'s knowledge base"

            formatted_results = [f"# Search Results for '{query}'\n"]
            for match in matches:
                title = match.get("title") or match.get("file_path") or "document"
                content = match.get("content", "")
                formatted_results.append(f"## {title}\n\n{content}\n")
                if self.tracker and self.run_id:
                    self.tracker.log_rag_document(
                        self.run_id,
                        client_name,
                        title,
                        agent_name=agent_name,
                    )
                    self.tracker.log_rag_chunk(
                        self.run_id,
                        agent_name or "",
                        match.get("id"),
                        content,
                        match.get("similarity"),
                    )
            return "\n".join(formatted_results)
        except Exception as e:  # pragma: no cover
            logger.warning(f"Supabase similarity search failed: {e}")
            return f"Error searching documents: {e}"

    def _embed_text(self, text: str) -> List[float]:
        """Generate embedding for given text using OpenAI if available."""
        if openai is None:  # pragma: no cover - optional dependency
            return [0.0] * 1536
        try:
            response = openai.Embeddings.create(model="text-embedding-3-small", input=text)
            return response.data[0].embedding  # type: ignore
        except Exception as e:  # pragma: no cover
            logger.warning(f"Embedding generation failed: {e}")
            return [0.0] * 1536

    def upload_document(self, client_name: str, path: str, content: str) -> str:
        """Upload a document to Supabase Storage and index it."""
        if self.supabase is None:
            raise ValueError("Supabase client not configured")

        storage_path = f"{client_name}/{path}"
        try:
            self.supabase.storage.from_("knowledge-base").upload(
                storage_path, content.encode("utf-8"), {"content-type": "text/markdown"}
            )
            embedding = self._embed_text(content)
            self.supabase.table("documents").insert(
                {
                    "title": path,
                    "content": content,
                    "file_path": storage_path,
                    "metadata": {"client_name": client_name},
                    "embedding": embedding,
                }
            ).execute()
        except Exception as e:  # pragma: no cover
            logger.warning(f"Error uploading document to Supabase: {e}")
        return storage_path

    def download_document(self, client_name: str, path: str) -> Optional[str]:
        """Download a document from Supabase Storage."""
        if self.supabase is None:
            return None

        storage_path = f"{client_name}/{path}"
        try:
            res = self.supabase.storage.from_("knowledge-base").download(storage_path)
            return res.decode("utf-8") if isinstance(res, bytes) else res
        except Exception as e:  # pragma: no cover
            logger.warning(f"Error downloading document from Supabase: {e}")
            return None
    
    async def add_content(
        self, 
        client_name: str, 
        document_name: str, 
        content: str
    ) -> str:
        """
        Add new content to client's knowledge base.
        
        Args:
            client_name: Name of the client
            document_name: Name of the document
            content: Content to add
            
        Returns:
            Success message or error
        """
        if not client_name or not document_name or not content:
            return "Client name, document name, and content are required"

        if self.supabase is None:
            return "Supabase client not configured"

        # Add .md extension if not present
        if "." not in document_name:
            document_name = f"{document_name}.md"

        try:
            self.upload_document(client_name, document_name, content)
            return f"Successfully added content to {document_name} for client {client_name}"
        except Exception as e:
            logger.error(f"Error adding content to Supabase: {e}")
            return f"Error adding content: {e}"
