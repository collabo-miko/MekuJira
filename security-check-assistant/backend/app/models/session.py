"""Session model for Excel upload sessions."""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class SessionStatus(str, Enum):
    """Session processing status."""

    UPLOADED = "uploaded"
    DETECTING = "detecting"
    DETECTED = "detected"
    GENERATING = "generating"
    GENERATED = "generated"
    REVIEWING = "reviewing"
    FINALIZED = "finalized"
    ERROR = "error"


class Session(BaseModel):
    """Excel upload session."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    vendor_name: Optional[str] = None
    status: SessionStatus = SessionStatus.UPLOADED
    error_message: Optional[str] = None
    total_questions: int = 0
    answered_questions: int = 0
    confidence_threshold: float = 0.70
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Format detection results
    question_column: Optional[str] = None
    answer_column: Optional[str] = None
    remarks_column: Optional[str] = None
    header_row: Optional[int] = None

    model_config = {"from_attributes": True}


class SessionCreate(BaseModel):
    """Schema for creating a session."""

    filename: str
    vendor_name: Optional[str] = None
    confidence_threshold: float = 0.70


class SessionUpdate(BaseModel):
    """Schema for updating a session."""

    status: Optional[SessionStatus] = None
    error_message: Optional[str] = None
    total_questions: Optional[int] = None
    answered_questions: Optional[int] = None
    question_column: Optional[str] = None
    answer_column: Optional[str] = None
    remarks_column: Optional[str] = None
    header_row: Optional[int] = None


class SessionResponse(BaseModel):
    """Response schema for session."""

    id: str
    filename: str
    vendor_name: Optional[str]
    status: SessionStatus
    error_message: Optional[str]
    total_questions: int
    answered_questions: int
    confidence_threshold: float
    created_at: datetime
    updated_at: datetime
    question_column: Optional[str]
    answer_column: Optional[str]
    remarks_column: Optional[str]
    header_row: Optional[int]
