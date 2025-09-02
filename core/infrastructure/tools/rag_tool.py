"""RAG (Retrieval-Augmented Generation) tool implementation."""

import logging
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..logging.agent_logger import agent_logger
from ..database.supabase_tracker import SupabaseTracker

logger = logging.getLogger(__name__)


class RAGTool:
    """
    RAG tool for retrieving and processing knowledge base content.
    
    This tool provides access to client-specific knowledge bases
    and content retrieval capabilities.
    """
    
    def __init__(self, rag_base_dir: str = "data/knowledge_base", tracker: Optional[SupabaseTracker] = None, run_id: Optional[str] = None):
        self.rag_base_dir = Path(rag_base_dir)
        self.rag_base_dir.mkdir(parents=True, exist_ok=True)
        self.tracker = tracker
        self.run_id = run_id

    def set_run(self, run_id: str, tracker: SupabaseTracker) -> None:
        self.run_id = run_id
        self.tracker = tracker
    
    async def get_client_content(
        self,
        client_name: str,
        document_name: Optional[str] = None
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

        client_dir = self.rag_base_dir / client_name

        if not client_dir.exists():
            error_msg = f"Knowledge base not found for client '{client_name}'"
            logger.warning(f"⚠️ RAG WARNING: {error_msg}")
            return error_msg

        try:
            if document_name:
                logger.info(f"📄 RAG: Retrieving specific document '{document_name}' for {client_name}")
                result = await self._get_specific_document(client_dir, document_name)
            else:
                logger.info(f"📚 RAG: Retrieving all content for {client_name}")
                # List available documents
                available_docs = [f.name for f in client_dir.glob('*.md') if f.is_file()]
                logger.info(f"📚 RAG: Found {len(available_docs)} documents: {available_docs}")
                result = await self._get_all_client_content(client_dir, client_name)
                if self.tracker and self.run_id:
                    for doc in available_docs:
                        self.tracker.log_rag_document(self.run_id, client_name, doc)

            duration_ms = (time.time() - start_time) * 1000
            content_length = len(result)

            logger.info(f"✅ RAG SUCCESS: Retrieved {content_length} characters in {duration_ms:.2f}ms")

            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"❌ RAG ERROR: Failed to retrieve content for {client_name}: {str(e)} ({duration_ms:.2f}ms)")
            return f"Error retrieving content: {str(e)}"
    
    async def _get_specific_document(self, client_dir: Path, document_name: str) -> str:
        """Retrieve a specific document from client's knowledge base."""
        # Add .md extension if not present
        if not Path(document_name).suffix:
            document_name = f"{document_name}.md"
        
        doc_path = client_dir / document_name
        
        if not doc_path.exists() or not doc_path.is_file():
            # Try fuzzy matching
            available_docs = [f.name for f in client_dir.glob('*.md') if f.is_file()]
            
            import difflib
            best_match = difflib.get_close_matches(
                document_name, available_docs, n=1, cutoff=0.6
            )
            
            if best_match:
                doc_path = client_dir / best_match[0]
                with open(str(doc_path), "r", encoding="utf-8") as f:
                    content = f.read()
                return f"[FUZZY MATCH] Document '{document_name}' not found. Showing closest match: '{best_match[0]}'\n\n{content}"
            else:
                return f"Document '{document_name}' not found. Available documents: {available_docs}"
        
        try:
            with open(str(doc_path), "r", encoding="utf-8") as f:
                content = f.read()
            if self.tracker and self.run_id:
                self.tracker.log_rag_document(self.run_id, client_dir.name, doc_path.name)
            return content
        except Exception as e:
            logger.error(f"Error reading document {doc_path}: {str(e)}")
            return f"Error reading document: {str(e)}"
    
    async def _get_all_client_content(self, client_dir: Path, client_name: str) -> str:
        """Retrieve and categorize all content for a client."""
        # Categorize documents by type
        company_info = []
        guidelines = []
        knowledge_base = []
        other_docs = []
        
        for doc_path in client_dir.glob("*.md"):
            doc_name = doc_path.name.lower()
            
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
                formatted_output.append(f"### {doc_name}\n\n{content}\n\n")
        
        if guidelines:
            formatted_output.append("""\n## CONTENT GUIDELINES

The following documents contain guidelines and best practices for content creation.
These should be strictly followed when generating content.
""")
            for doc_name, content in guidelines:
                formatted_output.append(f"### {doc_name}\n\n{content}\n\n")
        
        if knowledge_base:
            formatted_output.append("""\n## KNOWLEDGE BASE

The following documents contain detailed knowledge that can be referenced and incorporated into content.
Use this information as needed to enhance content accuracy and depth.
""")
            for doc_name, content in knowledge_base:
                formatted_output.append(f"### {doc_name}\n\n{content}\n\n")
        
        if other_docs:
            formatted_output.append("""\n## OTHER DOCUMENTS

The following documents contain additional information that may be relevant to content creation.
""")
            for doc_name, content in other_docs:
                formatted_output.append(f"### {doc_name}\n\n{content}\n\n")
        
        if not formatted_output:
            return f"No markdown documents found for client '{client_name}'"
        
        return "\n\n".join(formatted_output)
    
    async def get_available_documents(self, client_name: str) -> List[str]:
        """
        Get list of available documents for a client.
        
        Args:
            client_name: Name of the client
            
        Returns:
            List of available document names
        """
        if not client_name:
            return []
        
        client_dir = self.rag_base_dir / client_name
        
        if not client_dir.exists():
            return []
        
        return [f.name for f in client_dir.glob('*.md') if f.is_file()]
    
    async def search_content(
        self, 
        client_name: str, 
        query: str, 
        max_results: int = 5
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
        
        client_dir = self.rag_base_dir / client_name
        
        if not client_dir.exists():
            return f"Knowledge base not found for client '{client_name}'"
        
        query_lower = query.lower()
        results = []
        
        for doc_path in client_dir.glob("*.md"):
            try:
                with open(str(doc_path), "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Simple text search
                if query_lower in content.lower():
                    # Extract relevant snippet
                    lines = content.split('\n')
                    relevant_lines = []
                    
                    for i, line in enumerate(lines):
                        if query_lower in line.lower():
                            # Include context lines
                            start = max(0, i - 2)
                            end = min(len(lines), i + 3)
                            context = '\n'.join(lines[start:end])
                            relevant_lines.append(context)
                    
                    if relevant_lines:
                        results.append({
                            'document': doc_path.name,
                            'snippets': relevant_lines[:3]  # Max 3 snippets per doc
                        })
                        
            except Exception as e:
                logger.warning(f"Error searching {doc_path}: {str(e)}")
                continue
        
        if not results:
            return f"No results found for query '{query}' in {client_name}'s knowledge base"
        
        # Format results
        formatted_results = [f"# Search Results for '{query}'\n"]
        
        for result in results[:max_results]:
            formatted_results.append(f"## {result['document']}\n")
            for snippet in result['snippets']:
                formatted_results.append(f"```\n{snippet}\n```\n")
            if self.tracker and self.run_id:
                self.tracker.log_rag_document(self.run_id, client_name, result['document'])

        return '\n'.join(formatted_results)
    
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
        
        client_dir = self.rag_base_dir / client_name
        client_dir.mkdir(parents=True, exist_ok=True)
        
        # Add .md extension if not present
        if not Path(document_name).suffix:
            document_name = f"{document_name}.md"
        
        doc_path = client_dir / document_name
        
        try:
            with open(str(doc_path), "w", encoding="utf-8") as f:
                f.write(content)
            
            return f"Successfully added content to {document_name} for client {client_name}"
            
        except Exception as e:
            logger.error(f"Error adding content to {doc_path}: {str(e)}")
            return f"Error adding content: {str(e)}"
