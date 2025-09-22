"""RAG (Retrieval-Augmented Generation) tool implementation."""

import logging
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

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

        # Fallback to filesystem if Supabase not available
        settings = get_settings()
        self.rag_base_dir = Path(settings.knowledge_base_dir)
        self.use_filesystem_fallback = self.supabase is None

        # Optional selection of documents (ids) to restrict retrieval during a run
        self.selected_document_ids: Optional[set[str]] = None

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

    def set_selected_documents(self, ids: Optional[list[str]]) -> None:
        """Restrict retrieval to a set of document IDs (strings). Pass None to clear."""
        if ids:
            self.selected_document_ids = set(ids)
            logger.info(f"📌 RAG: Selection filter active for {len(self.selected_document_ids)} document(s)")
        else:
            self.selected_document_ids = None
            logger.info("📌 RAG: Selection filter cleared (all documents allowed)")

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

        if self.use_filesystem_fallback:
            logger.info("🔄 RAG: Using filesystem fallback (Supabase not available)")
            return await self._get_content_from_filesystem(client_name, document_name, agent_name)

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
            query = (
                self.supabase.table("documents")
                .select("id,title,content,file_path")
                .eq("client_id", client_id)
            )
            if self.selected_document_ids:
                ids_list = list(self.selected_document_ids)
                logger.info(f"📌 RAG: Applying selection filter to documents (ids={ids_list})")
                query = query.in_("id", ids_list)
            docs_res = query.execute()
            docs = docs_res.data or []
            logger.info(f"📚 RAG: Retrieved {len(docs)} document(s) for client '{client_name}'")
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
            # Apply selection filter if active
            if self.selected_document_ids:
                before = len(matches)
                matches = [m for m in matches if m.get("id") in self.selected_document_ids]
                logger.info(f"[36mRAG: Filtered semantic matches by selection: {before} [0m[90m->[0m {len(matches)}")

            if not matches:
                return await self._fallback_keyword_search_supabase(client_name, query, max_results, agent_name)

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
            logger.warning(f"Supabase similarity search failed (falling back to keyword search): {e}")
            return await self._fallback_keyword_search_supabase(client_name, query, max_results, agent_name)


    async def _fallback_keyword_search_supabase(
        self,
        client_name: str,
        query: str,
        max_results: int = 5,
        agent_name: Optional[str] = None,
    ) -> str:
        """Fallback keyword search using ILIKE on documents when RPC is unavailable.

        Tries content match first, then title match. Applies selection filter if present.
        """
        if self.supabase is None:
            return "Supabase client not configured"

        try:
            # Resolve client_id
            client_res = (
                self.supabase.table("clients")
                .select("id")
                .eq("name", client_name)
                .single()
                .execute()
            )
            client_data = client_res.data
            if not client_data:
                return f"Client '{client_name}' not found"
            client_id = client_data["id"]

            # Content ILIKE
            query_builder = (
                self.supabase.table("documents")
                .select("id,title,content,file_path")
                .eq("client_id", client_id)
            )
            if self.selected_document_ids:
                query_builder = query_builder.in_("id", list(self.selected_document_ids))
            docs_res = (
                query_builder
                .ilike("content", f"%{query}%")
                .limit(max_results)
                .execute()
            )
            matches = docs_res.data or []

            # If no content match, try title ILIKE
            if not matches:
                query_builder = (
                    self.supabase.table("documents")
                    .select("id,title,content,file_path")
                    .eq("client_id", client_id)
                )
                if self.selected_document_ids:
                    query_builder = query_builder.in_("id", list(self.selected_document_ids))
                docs_res2 = (
                    query_builder
                    .ilike("title", f"%{query}%")
                    .limit(max_results)
                    .execute()
                )
                matches = docs_res2.data or []

            if not matches:
                return (
                    f"No results found for query '{query}' in {client_name}'s knowledge base "
                    f"(keyword fallback)"
                )

            formatted_results = [f"# Search Results for '{query}' (keyword match)\n"]
            for match in matches:
                title = match.get("title") or match.get("file_path") or "document"
                content = match.get("content", "")
                formatted_results.append(f"## {title}\n\n{content}\n")
                if self.tracker and self.run_id:
                    self.tracker.log_rag_document(
                        self.run_id, client_name, title, agent_name=agent_name
                    )
                    self.tracker.log_rag_chunk(
                        self.run_id, agent_name or "", match.get("id"), content, None
                    )

            logger.info("RAG: Used keyword fallback for search (RPC `match_documents` unavailable or empty)")
            return "\n".join(formatted_results)
        except Exception as e:  # pragma: no cover
            logger.warning(f"Keyword fallback search failed: {e}")
            return f"Error searching documents (fallback): {e}"

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
        """Upload a document to Supabase Storage and index it.
        Always insert the DB record even if Storage upload fails (due to RLS),
        so the document is immediately usable by the app and agents.
        """
        if self.supabase is None:
            raise ValueError("Supabase client not configured")

        storage_path = f"{client_name}/{path}"

        # 1) Try to upload to Storage (best-effort)
        try:
            self.supabase.storage.from_("knowledge-base").upload(
                storage_path, content.encode("utf-8"), {"content-type": "text/markdown"}
            )
        except Exception as e:  # pragma: no cover
            logger.warning(f"Error uploading document to Supabase Storage (continuo con DB insert): {e}")

        # 2) Resolve client_id
        client_res = (
            self.supabase.table("clients")
            .select("id")
            .eq("name", client_name)
            .single()
            .execute()
        )
        client_data = client_res.data
        if not client_data:
            raise ValueError(f"Client '{client_name}' not found")
        client_id = client_data["id"]

        # 3) Insert document record (try with embedding, then fallback without)
        embedding = self._embed_text(content)
        try:
            self.supabase.table("documents").insert(
                {
                    "client_id": client_id,
                    "title": path,
                    "content": content,
                    "file_path": storage_path,
                    "metadata": {"client_name": client_name},
                    "embedding": embedding,
                }
            ).execute()
        except Exception as e1:  # pragma: no cover
            logger.warning(f"Error inserting document record (with embedding): {e1}")
            try:
                self.supabase.table("documents").insert(
                    {
                        "client_id": client_id,
                        "title": path,
                        "content": content,
                        "file_path": storage_path,
                        "metadata": {"client_name": client_name},
                    }
                ).execute()
                logger.info("Inserted document record without embedding (fallback)")
            except Exception as e2:  # pragma: no cover
                logger.warning(f"Error inserting document record (fallback): {e2}")

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

    # ============= FILESYSTEM FALLBACK METHODS =============

    async def _get_content_from_filesystem(self, client_name: str, document_name: Optional[str] = None, agent_name: Optional[str] = None) -> str:
        """Fallback method to get content from filesystem when Supabase is not available."""
        client_dir = self.rag_base_dir / client_name

        if not client_dir.exists():
            # Fallback: allow knowledge bases stored inside profile directories
            settings = get_settings()
            profiles_dir = Path(settings.profiles_dir) / client_name / "knowledge_base"
            if profiles_dir.exists():
                logger.info(
                    "📂 RAG FILESYSTEM: Using profile-scoped knowledge base for %s",
                    client_name,
                )
                client_dir = profiles_dir
            else:
                error_msg = f"Knowledge base not found for client '{client_name}'"
                logger.warning(f"⚠️ RAG WARNING: {error_msg}")
                return error_msg

        try:
            if document_name:
                logger.info(f"📄 RAG FILESYSTEM: Retrieving specific document '{document_name}' for {client_name}")
                return await self._get_specific_document_filesystem(client_dir, document_name, agent_name)
            else:
                logger.info(f"📚 RAG FILESYSTEM: Retrieving all content for {client_name}")
                available_docs = [
                    str(f.relative_to(client_dir))
                    for f in client_dir.rglob('*.md')
                    if f.is_file()
                ]
                logger.info(f"📚 RAG FILESYSTEM: Found {len(available_docs)} documents: {available_docs}")
                result = await self._get_all_client_content_filesystem(client_dir, client_name, agent_name)
                if self.tracker and self.run_id:
                    for doc in available_docs:
                        self.tracker.log_rag_document(self.run_id, client_name, doc, agent_name=agent_name)
                return result

        except Exception as e:
            logger.error(f"❌ RAG FILESYSTEM ERROR: Failed to retrieve content for {client_name}: {str(e)}")
            return f"Error retrieving content: {str(e)}"

    async def _get_specific_document_filesystem(self, client_dir: Path, document_name: str, agent_name: Optional[str] = None) -> str:
        """Retrieve a specific document from filesystem."""
        original_name = document_name
        doc_path = client_dir / document_name

        if not doc_path.exists() or not doc_path.is_file():
            if not Path(document_name).suffix:
                document_name = f"{document_name}.md"
            doc_path = client_dir / document_name

        if not doc_path.exists() or not doc_path.is_file():
            # Try fuzzy matching across nested directories
            available_docs = [
                str(f.relative_to(client_dir))
                for f in client_dir.rglob('*.md')
                if f.is_file()
            ]

            import difflib
            best_match = difflib.get_close_matches(
                document_name,
                available_docs,
                n=1,
                cutoff=0.6,
            )

            if best_match:
                doc_path = client_dir / best_match[0]
                with open(str(doc_path), "r", encoding="utf-8") as f:
                    content = f.read()
                return (
                    f"[FUZZY MATCH] Document '{original_name}' not found. "
                    f"Showing closest match: '{best_match[0]}'\\n\\n{content}"
                )
            else:
                return (
                    f"Document '{original_name}' not found. Available documents: {available_docs}"
                )

        try:
            with open(str(doc_path), "r", encoding="utf-8") as f:
                content = f.read()
            if self.tracker and self.run_id:
                self.tracker.log_rag_document(self.run_id, client_dir.name, doc_path.name, agent_name=agent_name)
            return content
        except Exception as e:
            logger.error(f"Error reading document {doc_path}: {str(e)}")
            return f"Error reading document: {str(e)}"

    async def _get_all_client_content_filesystem(self, client_dir: Path, client_name: str, agent_name: Optional[str] = None) -> str:
        """Retrieve and categorize all content for a client from filesystem."""
        # Categorize documents by type
        company_info = []
        guidelines = []
        knowledge_base = []
        other_docs = []

        for doc_path in client_dir.rglob("*.md"):
            if not doc_path.is_file():
                continue

            doc_name = str(doc_path.relative_to(client_dir)).lower()

            try:
                with open(str(doc_path), "r", encoding="utf-8") as f:
                    content = f.read()

                # Categorize based on filename patterns
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

            except Exception as e:
                logger.warning(f"Error reading {doc_path}: {str(e)}")
                continue

        # Format output
        formatted_output = []

        if company_info:
            formatted_output.append("""## COMPANY INFORMATION

The following documents contain essential information about the company, its brand, and positioning.
This information should be reflected in all content creation.
""")
            for doc_name, content in company_info:
                formatted_output.append(f"### {doc_name}\\n\\n{content}\\n\\n")

        if guidelines:
            formatted_output.append("""\\n## CONTENT GUIDELINES

The following documents contain guidelines and best practices for content creation.
These should be strictly followed when generating content.
""")
            for doc_name, content in guidelines:
                formatted_output.append(f"### {doc_name}\\n\\n{content}\\n\\n")

        if knowledge_base:
            formatted_output.append("""\\n## KNOWLEDGE BASE

The following documents contain detailed knowledge that can be referenced and incorporated into content.
Use this information as needed to enhance content accuracy and depth.
""")
            for doc_name, content in knowledge_base:
                formatted_output.append(f"### {doc_name}\\n\\n{content}\\n\\n")

        if other_docs:
            formatted_output.append("""\\n## OTHER DOCUMENTS

The following documents contain additional information that may be relevant to content creation.
""")
            for doc_name, content in other_docs:
                formatted_output.append(f"### {doc_name}\\n\\n{content}\\n\\n")

        if not formatted_output:
            return f"No markdown documents found for client '{client_name}'"

        return "\\n\\n".join(formatted_output)
