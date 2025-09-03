"""Knowledge base endpoints for RAG content management."""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from core.infrastructure.database.supabase_tracker import SupabaseTracker


def get_supabase_client():
    try:
        tracker = SupabaseTracker()
        return tracker.client
    except Exception as e:  # pragma: no cover
        logger.error(f"Supabase not configured: {e}")
        raise HTTPException(status_code=500, detail="Supabase not configured")

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge-base", tags=["knowledge-base"])


class DocumentInfo(BaseModel):
    """Document information model."""
    id: str
    title: str
    filename: str
    description: str
    content_preview: str
    tags: List[str]
    last_modified: str
    size_bytes: int
    content_type: str = "markdown"


class ClientDocumentsResponse(BaseModel):
    """Response model for client documents."""
    client_name: str
    total_documents: int
    documents: List[DocumentInfo]


class DocumentContentResponse(BaseModel):
    """Response model for document content."""
    document_id: str
    title: str
    content: str
    metadata: Dict[str, Any]


@router.get("/clients/{client_name}/documents", response_model=ClientDocumentsResponse)
async def get_client_documents(
    client_name: str,
    search: Optional[str] = Query(None, description="Search query to filter documents"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    supabase=Depends(get_supabase_client)
) -> ClientDocumentsResponse:
    """
    Get all documents for a specific client.
    
    Args:
        client_name: Name of the client
        search: Optional search query
        tags: Optional list of tags to filter by
        rag_tool: RAG tool instance
        
    Returns:
        List of documents with metadata
    """
    logger.info(f"📚 Getting documents for client: {client_name}")

    try:
        client_res = (
            supabase.table("clients").select("id").eq("name", client_name).single().execute()
        )
        client_data = client_res.data
        if not client_data:
            logger.warning(f"Client not found: {client_name}")
            return ClientDocumentsResponse(client_name=client_name, total_documents=0, documents=[])

        docs_res = (
            supabase.table("documents")
            .select("id,title,description,content,tags,updated_at,file_path,file_size,file_type")
            .eq("client_id", client_data["id"])
            .execute()
        )
        docs = docs_res.data or []

        documents: List[DocumentInfo] = []
        for doc in docs:
            content = doc.get("content", "")
            if search and search.lower() not in doc.get("title", "").lower() and search.lower() not in content.lower():
                continue
            if tags and not any(tag in (doc.get("tags") or []) for tag in tags):
                continue
            preview = content[:300] + ("..." if len(content) > 300 else "")
            documents.append(
                DocumentInfo(
                    id=str(doc.get("id")),
                    title=doc.get("title", ""),
                    filename=doc.get("file_path") or doc.get("title", ""),
                    description=doc.get("description") or preview,
                    content_preview=preview,
                    tags=doc.get("tags") or [],
                    last_modified=doc.get("updated_at") or "",
                    size_bytes=doc.get("file_size") or len(content),
                    content_type=doc.get("file_type") or "markdown",
                )
            )

        documents.sort(key=lambda x: x.last_modified, reverse=True)
        logger.info(f"✅ Found {len(documents)} documents for {client_name}")
        return ClientDocumentsResponse(client_name=client_name, total_documents=len(documents), documents=documents)

    except Exception as e:
        logger.error(f"Error getting documents for {client_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {e}")


@router.get("/clients/{client_name}/documents/{document_id}", response_model=DocumentContentResponse)
async def get_document_content(
    client_name: str,
    document_id: str,
    supabase=Depends(get_supabase_client)
) -> DocumentContentResponse:
    """
    Get full content of a specific document.
    
    Args:
        client_name: Name of the client
        document_id: ID of the document (filename without extension)
        rag_tool: RAG tool instance
        
    Returns:
        Document content with metadata
    """
    logger.info(f"📄 Getting document content: {client_name}/{document_id}")

    try:
        client_res = (
            supabase.table("clients").select("id").eq("name", client_name).single().execute()
        )
        client_data = client_res.data
        if not client_data:
            raise HTTPException(status_code=404, detail=f"Client {client_name} not found")

        doc_res = (
            supabase.table("documents")
            .select("id,title,content,tags,updated_at,file_path,file_size,file_type,description")
            .eq("client_id", client_data["id"])
            .eq("id", document_id)
            .single()
            .execute()
        )
        doc = doc_res.data
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document {document_id} not found")

        content = doc.get("content", "")
        metadata = {
            "filename": doc.get("file_path") or doc.get("title", ""),
            "tags": doc.get("tags") or [],
            "last_modified": doc.get("updated_at") or "",
            "size_bytes": doc.get("file_size") or len(content),
            "content_type": doc.get("file_type") or "markdown",
        }
        return DocumentContentResponse(
            document_id=str(doc.get("id")),
            title=doc.get("title", ""),
            content=content,
            metadata=metadata,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document content {client_name}/{document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {e}")


@router.get("/clients", response_model=List[str])
async def get_available_clients(
    supabase=Depends(get_supabase_client)
) -> List[str]:
    """Get list of available clients with knowledge bases."""
    logger.info("📋 Getting available clients")

    try:
        res = supabase.table("clients").select("name").execute()
        clients = sorted([c["name"] for c in (res.data or [])])
        logger.info(f"✅ Found {len(clients)} clients: {clients}")
        return clients
    except Exception as e:
        logger.error(f"Error getting available clients: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving clients: {e}")


class FrontendDocument(BaseModel):
    """Frontend-compatible document model."""
    id: str
    title: str
    description: str
    date: str
    category: str
    tags: List[str]
    selected: bool = False


@router.get("/frontend/clients/{client_name}/documents", response_model=List[FrontendDocument])
async def get_frontend_documents(
    client_name: str,
    search: Optional[str] = Query(None, description="Search query to filter documents"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    supabase=Depends(get_supabase_client)
) -> List[FrontendDocument]:
    """Get documents in frontend-compatible format."""
    logger.info(f"🎨 Getting frontend documents for client: {client_name}")

    try:
        client_res = (
            supabase.table("clients").select("id").eq("name", client_name).single().execute()
        )
        client_data = client_res.data
        if not client_data:
            logger.warning(f"Client not found: {client_name}")
            return []

        docs_res = (
            supabase.table("documents")
            .select("id,title,description,content,tags,updated_at")
            .eq("client_id", client_data["id"])
            .execute()
        )
        docs = docs_res.data or []

        documents: List[FrontendDocument] = []
        for doc in docs:
            content = doc.get("content", "")
            if search and search.lower() not in doc.get("title", "").lower() and search.lower() not in content.lower():
                continue
            if tags and not any(tag in (doc.get("tags") or []) for tag in tags):
                continue
            description = doc.get("description") or content[:200]
            documents.append(
                FrontendDocument(
                    id=str(doc.get("id")),
                    title=doc.get("title", ""),
                    description=description,
                    date=(doc.get("updated_at") or "")[:10],
                    category=(doc.get("tags") or ["general"])[0],
                    tags=doc.get("tags") or [],
                    selected=False,
                )
            )

        documents.sort(key=lambda x: x.date, reverse=True)
        logger.info(f"✅ Returning {len(documents)} frontend documents for {client_name}")
        return documents

    except Exception as e:
        logger.error(f"Error getting frontend documents for {client_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {e}")


