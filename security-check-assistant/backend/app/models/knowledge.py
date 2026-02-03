"""Knowledge model for approved answers storage."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class Knowledge(BaseModel):
    """Knowledge item - approved Q&A pair."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_text: str
    answer_text: str
    vendor_name: Optional[str] = None
    source_type: str = "user_approved"  # "user_approved", "imported"
    session_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}


class KnowledgeCreate(BaseModel):
    """Schema for creating a knowledge item."""

    question_text: str
    answer_text: str
    vendor_name: Optional[str] = None
    source_type: str = "user_approved"
    session_id: Optional[str] = None


class KnowledgeResponse(BaseModel):
    """Response schema for knowledge item."""

    id: str
    question_text: str
    answer_text: str
    vendor_name: Optional[str]
    source_type: str
    session_id: Optional[str]
    created_at: datetime


class KnowledgeSearchResult(BaseModel):
    """Search result with similarity score."""

    knowledge: KnowledgeResponse
    similarity_score: float
