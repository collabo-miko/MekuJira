"""Review and approval API routes."""
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db.repositories.session_repository import SessionRepository
from app.db.repositories.question_repository import QuestionRepository
from app.db.repositories.answer_repository import AnswerRepository
from app.db.repositories.knowledge_repository import KnowledgeRepository
from app.models.session import SessionStatus
from app.models.answer import AnswerStatus, AnswerResponse
from app.models.knowledge import Knowledge

router = APIRouter()


class ReviewItem(BaseModel):
    """A question with its answer for review."""

    question_id: str
    row_number: int
    question_text: str
    remarks: Optional[str]
    answer_id: Optional[str]
    answer_text: str
    confidence_score: float
    confidence_level: str  # "high", "medium", "low"
    status: str
    sources: list[dict]


class ReviewResponse(BaseModel):
    """Response containing all items for review."""

    session_id: str
    filename: str
    vendor_name: Optional[str]
    total_questions: int
    items: list[ReviewItem]


class ModifyRequest(BaseModel):
    """Request to modify an answer."""

    answer_text: str


@router.get("/{session_id}", response_model=ReviewResponse)
async def get_review_items(session_id: str):
    """Get all questions and answers for review."""
    session = await SessionRepository.get_by_id(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    questions = await QuestionRepository.get_by_session(session_id)
    answers = await AnswerRepository.get_by_session(session_id)

    # Create answer lookup
    answer_map = {a.question_id: a for a in answers}

    items = []
    for q in questions:
        answer = answer_map.get(q.id)

        # Determine confidence level
        confidence_score = answer.confidence_score if answer else 0.0
        if confidence_score >= 0.85:
            confidence_level = "high"
        elif confidence_score >= 0.70:
            confidence_level = "medium"
        else:
            confidence_level = "low"

        items.append(
            ReviewItem(
                question_id=q.id,
                row_number=q.row_number,
                question_text=q.question_text,
                remarks=q.remarks,
                answer_id=answer.id if answer else None,
                answer_text=answer.answer_text if answer else "",
                confidence_score=confidence_score,
                confidence_level=confidence_level,
                status=answer.status.value if answer else "pending",
                sources=[s.model_dump() for s in answer.sources] if answer else [],
            )
        )

    return ReviewResponse(
        session_id=session_id,
        filename=session.filename,
        vendor_name=session.vendor_name,
        total_questions=len(questions),
        items=items,
    )


@router.put("/{answer_id}/approve", response_model=AnswerResponse)
async def approve_answer(answer_id: str):
    """Approve an answer."""
    answer = await AnswerRepository.get_by_id(answer_id)
    if answer is None:
        raise HTTPException(status_code=404, detail="Answer not found")

    updated = await AnswerRepository.update(
        answer_id,
        status=AnswerStatus.APPROVED,
    )

    return AnswerResponse(
        id=updated.id,
        question_id=updated.question_id,
        answer_text=updated.answer_text,
        confidence_score=updated.confidence_score,
        status=updated.status,
        sources=updated.sources,
        original_answer=updated.original_answer,
        modified_by_user=updated.modified_by_user,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )


@router.put("/{answer_id}/modify", response_model=AnswerResponse)
async def modify_answer(answer_id: str, request: ModifyRequest):
    """Modify an answer."""
    answer = await AnswerRepository.get_by_id(answer_id)
    if answer is None:
        raise HTTPException(status_code=404, detail="Answer not found")

    # Store original answer if not already stored
    original = answer.original_answer or answer.answer_text

    updated = await AnswerRepository.update(
        answer_id,
        answer_text=request.answer_text,
        original_answer=original,
        status=AnswerStatus.MODIFIED,
        modified_by_user=True,
    )

    return AnswerResponse(
        id=updated.id,
        question_id=updated.question_id,
        answer_text=updated.answer_text,
        confidence_score=updated.confidence_score,
        status=updated.status,
        sources=updated.sources,
        original_answer=updated.original_answer,
        modified_by_user=updated.modified_by_user,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )


@router.post("/{session_id}/finalize")
async def finalize_session(session_id: str):
    """Finalize a session, saving approved answers to knowledge base."""
    session = await SessionRepository.get_by_id(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get all approved/modified answers
    answers = await AnswerRepository.get_by_session(session_id)
    approved_answers = [
        a for a in answers
        if a.status in [AnswerStatus.APPROVED, AnswerStatus.MODIFIED]
    ]

    if not approved_answers:
        raise HTTPException(
            status_code=400,
            detail="No approved answers to finalize",
        )

    # Get questions for the approved answers
    questions = await QuestionRepository.get_by_session(session_id)
    question_map = {q.id: q for q in questions}

    # Create knowledge items
    knowledge_items = []
    for answer in approved_answers:
        question = question_map.get(answer.question_id)
        if question:
            knowledge_items.append(
                Knowledge(
                    question_text=question.question_text,
                    answer_text=answer.answer_text,
                    vendor_name=session.vendor_name,
                    source_type="user_approved",
                    session_id=session_id,
                )
            )

    # Save to knowledge base
    if knowledge_items:
        await KnowledgeRepository.create_many(knowledge_items)

    # Update session status
    await SessionRepository.update(
        session_id,
        status=SessionStatus.FINALIZED,
    )

    return {
        "message": "Session finalized",
        "knowledge_items_created": len(knowledge_items),
    }
