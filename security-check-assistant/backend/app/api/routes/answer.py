"""Answer generation API routes."""
from typing import Optional, Annotated
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from app.core.answer_engine import AnswerEngine
from app.db.repositories.session_repository import SessionRepository
from app.db.repositories.question_repository import QuestionRepository
from app.db.repositories.answer_repository import AnswerRepository
from app.db.repositories.document_repository import DocumentRepository
from app.models.session import SessionStatus
from app.models.answer import AnswerResponse

router = APIRouter()


class GenerateRequest(BaseModel):
    """Request body for answer generation."""

    session_id: str
    confidence_threshold: Optional[Annotated[float, Field(ge=0.0, le=1.0)]] = None


class GenerateResponse(BaseModel):
    """Response for answer generation."""

    session_id: str
    status: str
    message: str


@router.post("/generate", response_model=GenerateResponse)
async def generate_answers(
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
):
    """Start batch answer generation for a session.

    This runs in the background and generates answers for all questions
    in the session.
    """
    session = await SessionRepository.get_by_id(request.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status not in [SessionStatus.DETECTED, SessionStatus.GENERATED]:
        raise HTTPException(
            status_code=400,
            detail=f"Session status must be 'detected' or 'generated', current: {session.status.value}",
        )

    # Update session status
    await SessionRepository.update(
        request.session_id,
        status=SessionStatus.GENERATING,
    )

    # Start background generation
    confidence_threshold = (
        request.confidence_threshold
        if request.confidence_threshold is not None
        else session.confidence_threshold
    )
    if confidence_threshold < 0.0 or confidence_threshold > 1.0:
        raise HTTPException(
            status_code=400,
            detail="confidence_threshold must be between 0.0 and 1.0",
        )
    background_tasks.add_task(
        generate_answers_task,
        session_id=request.session_id,
        confidence_threshold=confidence_threshold,
    )

    return GenerateResponse(
        session_id=request.session_id,
        status="generating",
        message="Answer generation started",
    )


async def generate_answers_task(session_id: str, confidence_threshold: float) -> None:
    """Background task to generate answers for all questions in a session."""
    try:
        # Get questions
        questions = await QuestionRepository.get_by_session(session_id)
        if not questions:
            await SessionRepository.update(
                session_id,
                status=SessionStatus.GENERATED,
                answered_questions=0,
            )
            return

        # Get indexed documents
        indexed_docs = await DocumentRepository.get_indexed()
        doc_ids = [d.pageindex_doc_id for d in indexed_docs if d.pageindex_doc_id]

        # Initialize answer engine
        engine = AnswerEngine(confidence_threshold=confidence_threshold)

        # Generate answers
        answers = await engine.generate_batch(questions, doc_ids)

        # Save answers
        await AnswerRepository.create_many(answers)

        # Count answers that meet threshold
        answered_count = sum(
            1 for a in answers
            if a.confidence_score >= confidence_threshold and a.answer_text
        )

        # Update session
        await SessionRepository.update(
            session_id,
            status=SessionStatus.GENERATED,
            answered_questions=answered_count,
        )

    except Exception as e:
        await SessionRepository.update(
            session_id,
            status=SessionStatus.ERROR,
            error_message=str(e),
        )


@router.get("/status/{session_id}")
async def get_generation_status(session_id: str):
    """Get the status of answer generation for a session."""
    session = await SessionRepository.get_by_id(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    answer_count = await AnswerRepository.count_by_session(session_id)

    return {
        "session_id": session_id,
        "status": session.status.value,
        "total_questions": session.total_questions,
        "generated_answers": answer_count,
        "answered_questions": session.answered_questions,
        "error_message": session.error_message,
    }


@router.post("/regenerate/{question_id}", response_model=AnswerResponse)
async def regenerate_answer(question_id: str):
    """Regenerate the answer for a specific question."""
    question = await QuestionRepository.get_by_id(question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    session = await SessionRepository.get_by_id(question.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get indexed documents
    indexed_docs = await DocumentRepository.get_indexed()
    doc_ids = [d.pageindex_doc_id for d in indexed_docs if d.pageindex_doc_id]

    # Initialize answer engine
    engine = AnswerEngine(confidence_threshold=session.confidence_threshold)

    # Generate new answer
    new_answer = await engine.regenerate_answer(question, doc_ids)

    # Update or create the answer
    existing = await AnswerRepository.get_by_question(question_id)
    if existing:
        new_answer = await AnswerRepository.update(
            existing.id,
            answer_text=new_answer.answer_text,
            confidence_score=new_answer.confidence_score,
            sources=new_answer.sources,
        )
    else:
        new_answer = await AnswerRepository.create(new_answer)

    return AnswerResponse(
        id=new_answer.id,
        question_id=new_answer.question_id,
        answer_text=new_answer.answer_text,
        confidence_score=new_answer.confidence_score,
        status=new_answer.status,
        sources=new_answer.sources,
        original_answer=new_answer.original_answer,
        modified_by_user=new_answer.modified_by_user,
        created_at=new_answer.created_at,
        updated_at=new_answer.updated_at,
    )
