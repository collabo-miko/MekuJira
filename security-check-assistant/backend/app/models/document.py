"""Document model for reference documents (PDFs)."""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class DocumentStatus(str, Enum):
    """Document indexing status."""

    UPLOADING = "uploading"
    INDEXING = "indexing"
    INDEXED = "indexed"
    ERROR = "error"


class Document(BaseModel):
    """Reference document (PDF)."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pageindex_doc_id: Optional[str] = None
    filename: str
    file_path: str
    page_count: Optional[int] = None
    status: DocumentStatus = DocumentStatus.UPLOADING
    error_message: Optional[str] = None
    indexed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}


class DocumentCreate(BaseModel):
    """Schema for creating a document."""

    filename: str
    file_path: str


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""

    pageindex_doc_id: Optional[str] = None
    page_count: Optional[int] = None
    status: Optional[DocumentStatus] = None
    error_message: Optional[str] = None
    indexed_at: Optional[datetime] = None


class DocumentResponse(BaseModel):
    """Response schema for document."""

    id: str
    pageindex_doc_id: Optional[str]
    filename: str
    page_count: Optional[int]
    status: DocumentStatus
    error_message: Optional[str]
    indexed_at: Optional[datetime]
    created_at: datetime
