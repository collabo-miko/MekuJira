"""Answer model for generated answers."""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class AnswerStatus(str, Enum):
    """Answer approval status."""

    PENDING = "pending"
    APPROVED = "approved"
    MODIFIED = "modified"
    REJECTED = "rejected"


class AnswerSource(BaseModel):
    """Source reference for an answer."""

    type: str  # "pageindex", "knowledge", "manual"
    document_id: Optional[str] = None
    document_name: Optional[str] = None
    page_number: Optional[int] = None
    snippet: Optional[str] = None
    knowledge_id: Optional[str] = None


class Answer(BaseModel):
    """Generated answer for a question."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_id: str
    answer_text: str
    confidence_score: float
    status: AnswerStatus = AnswerStatus.PENDING
    sources: list[AnswerSource] = Field(default_factory=list)
    original_answer: Optional[str] = None  # Stores AI answer if manually modified
    modified_by_user: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}


class AnswerCreate(BaseModel):
    """Schema for creating an answer."""

    question_id: str
    answer_text: str
    confidence_score: float
    sources: list[AnswerSource] = Field(default_factory=list)


class AnswerUpdate(BaseModel):
    """Schema for updating an answer."""

    answer_text: Optional[str] = None
    status: Optional[AnswerStatus] = None
    modified_by_user: bool = False


class AnswerResponse(BaseModel):
    """Response schema for answer."""

    id: str
    question_id: str
    answer_text: str
    confidence_score: float
    status: AnswerStatus
    sources: list[AnswerSource]
    original_answer: Optional[str]
    modified_by_user: bool
    created_at: datetime
    updated_at: datetime
