"""Question model for extracted questions from Excel."""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class QuestionType(str, Enum):
    """Type of question/answer format."""

    FREE_TEXT = "free_text"
    YES_NO = "yes_no"
    MULTIPLE_CHOICE = "multiple_choice"
    UNKNOWN = "unknown"


class Question(BaseModel):
    """Question extracted from Excel sheet."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    row_number: int
    question_text: str
    remarks: Optional[str] = None
    answer_column: str
    question_type: QuestionType = QuestionType.UNKNOWN
    choices: Optional[list[str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}


class QuestionCreate(BaseModel):
    """Schema for creating a question."""

    session_id: str
    row_number: int
    question_text: str
    remarks: Optional[str] = None
    answer_column: str
    question_type: QuestionType = QuestionType.UNKNOWN
    choices: Optional[list[str]] = None


class QuestionResponse(BaseModel):
    """Response schema for question."""

    id: str
    session_id: str
    row_number: int
    question_text: str
    remarks: Optional[str]
    answer_column: str
    question_type: QuestionType
    choices: Optional[list[str]]
    created_at: datetime
