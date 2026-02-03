"""Document management API routes."""
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks

from app.config import get_settings
from app.core.pageindex_client import get_pageindex_client
from app.db.repositories.document_repository import DocumentRepository
from app.models.document import Document, DocumentStatus, DocumentResponse

router = APIRouter()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """Upload a PDF document and start indexing.

    The document will be indexed by PageIndex in the background.
    Note: The document will be sent to PageIndex for processing.
    """
    settings = get_settings()

    # Validate file type
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF files are supported.",
        )

    # Save the file
    docs_dir = Path(settings.documents_dir)
    docs_dir.mkdir(parents=True, exist_ok=True)

    file_path = docs_dir / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create document record
    document = Document(
        filename=file.filename,
        file_path=str(file_path),
        status=DocumentStatus.UPLOADING,
    )
    document = await DocumentRepository.create(document)

    # Index document in background
    background_tasks.add_task(
        index_document,
        document_id=document.id,
        file_path=str(file_path),
    )

    return DocumentResponse(
        id=document.id,
        pageindex_doc_id=document.pageindex_doc_id,
        filename=document.filename,
        page_count=document.page_count,
        status=document.status,
        error_message=document.error_message,
        indexed_at=document.indexed_at,
        created_at=document.created_at,
    )


async def index_document(document_id: str, file_path: str) -> None:
    """Index a document using PageIndex in the background."""
    try:
        # Update status
        await DocumentRepository.update(document_id, status=DocumentStatus.INDEXING)

        # Index with PageIndex
        client = get_pageindex_client()
        doc_id = await client.index_document(file_path)

        # Get document status (page count, etc.)
        status = await client.get_document_status(doc_id)

        # Update document record
        await DocumentRepository.update(
            document_id,
            pageindex_doc_id=doc_id,
            page_count=status.get("page_count"),
            status=DocumentStatus.INDEXED,
            indexed_at=datetime.utcnow(),
        )

    except Exception as e:
        await DocumentRepository.update(
            document_id,
            status=DocumentStatus.ERROR,
            error_message=str(e),
        )


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    status: Optional[str] = None,
):
    """Get list of all documents."""
    doc_status = None
    if status:
        try:
            doc_status = DocumentStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {[s.value for s in DocumentStatus]}",
            )

    documents = await DocumentRepository.get_all(status=doc_status)
    return [
        DocumentResponse(
            id=d.id,
            pageindex_doc_id=d.pageindex_doc_id,
            filename=d.filename,
            page_count=d.page_count,
            status=d.status,
            error_message=d.error_message,
            indexed_at=d.indexed_at,
            created_at=d.created_at,
        )
        for d in documents
    ]


@router.get("/{document_id}/status", response_model=DocumentResponse)
async def get_document_status(document_id: str):
    """Get the status of a document."""
    document = await DocumentRepository.get_by_id(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentResponse(
        id=document.id,
        pageindex_doc_id=document.pageindex_doc_id,
        filename=document.filename,
        page_count=document.page_count,
        status=document.status,
        error_message=document.error_message,
        indexed_at=document.indexed_at,
        created_at=document.created_at,
    )


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document."""
    document = await DocumentRepository.get_by_id(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete the file
    file_path = Path(document.file_path)
    if file_path.exists():
        file_path.unlink()

    # Delete from database
    await DocumentRepository.delete(document_id)

    return {"message": "Document deleted"}
