"""Excel upload and management API routes."""
import shutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, BackgroundTasks
from fastapi.responses import FileResponse

from app.config import get_settings
from app.core.file_utils import sanitize_filename
from app.core.excel_parser import ExcelParser
from app.core.format_detector import FormatDetector
from app.db.repositories.session_repository import SessionRepository
from app.db.repositories.question_repository import QuestionRepository
from app.models.session import Session, SessionStatus, SessionResponse
from app.models.question import Question, QuestionResponse

router = APIRouter()


@router.post("/upload", response_model=SessionResponse)
async def upload_excel(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    vendor_name: Optional[str] = Form(None),
    confidence_threshold: float = Form(0.70),
):
    """Upload an Excel file and create a new session.

    The file will be processed in the background to detect format
    and extract questions.
    """
    settings = get_settings()

    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .xlsx files are supported.",
        )

    if confidence_threshold < 0.0 or confidence_threshold > 1.0:
        raise HTTPException(
            status_code=400,
            detail="confidence_threshold must be between 0.0 and 1.0",
        )

    try:
        safe_filename = sanitize_filename(file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Save the file
    upload_dir = Path(settings.uploads_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / safe_filename
    if file_path.exists():
        raise HTTPException(
            status_code=409,
            detail="A file with the same name already exists.",
        )
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create session
    session = Session(
        filename=safe_filename,
        vendor_name=vendor_name,
        confidence_threshold=confidence_threshold,
        status=SessionStatus.UPLOADED,
    )
    session = await SessionRepository.create(session)

    # Process file in background
    background_tasks.add_task(
        process_excel_file,
        session_id=session.id,
        file_path=str(file_path),
    )

    return SessionResponse(
        id=session.id,
        filename=session.filename,
        vendor_name=session.vendor_name,
        status=session.status,
        error_message=session.error_message,
        total_questions=session.total_questions,
        answered_questions=session.answered_questions,
        confidence_threshold=session.confidence_threshold,
        created_at=session.created_at,
        updated_at=session.updated_at,
        question_column=session.question_column,
        answer_column=session.answer_column,
        remarks_column=session.remarks_column,
        header_row=session.header_row,
    )


async def process_excel_file(session_id: str, file_path: str) -> None:
    """Process an uploaded Excel file in the background."""
    try:
        # Update status
        await SessionRepository.update(session_id, status=SessionStatus.DETECTING)

        # Parse Excel and detect format
        parser = ExcelParser(file_path)
        parser.load()

        detector = FormatDetector()
        sample_data = parser.extract_sample_data()
        sheet_format = await detector.detect(sample_data)

        # Update session with detected format
        await SessionRepository.update(
            session_id,
            status=SessionStatus.DETECTED,
            question_column=sheet_format.question_column,
            answer_column=sheet_format.answer_column,
            remarks_column=sheet_format.remarks_column,
            header_row=sheet_format.header_row,
        )

        # Extract questions
        extracted = parser.extract_questions(sheet_format)

        # Create Question objects
        questions = [
            Question(
                session_id=session_id,
                row_number=eq.row_number,
                question_text=eq.question_text,
                remarks=eq.remarks,
                answer_column=eq.answer_column,
                question_type=eq.question_type,
                choices=eq.choices,
            )
            for eq in extracted
        ]

        # Save questions
        await QuestionRepository.create_many(questions)

        # Update session with question count
        await SessionRepository.update(
            session_id,
            total_questions=len(questions),
        )

        parser.close()

    except Exception as e:
        await SessionRepository.update(
            session_id,
            status=SessionStatus.ERROR,
            error_message=str(e),
        )


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(
    limit: int = 100,
    offset: int = 0,
):
    """Get list of all sessions."""
    sessions = await SessionRepository.get_all(limit=limit, offset=offset)
    return [
        SessionResponse(
            id=s.id,
            filename=s.filename,
            vendor_name=s.vendor_name,
            status=s.status,
            error_message=s.error_message,
            total_questions=s.total_questions,
            answered_questions=s.answered_questions,
            confidence_threshold=s.confidence_threshold,
            created_at=s.created_at,
            updated_at=s.updated_at,
            question_column=s.question_column,
            answer_column=s.answer_column,
            remarks_column=s.remarks_column,
            header_row=s.header_row,
        )
        for s in sessions
    ]


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get a session by ID."""
    session = await SessionRepository.get_by_id(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse(
        id=session.id,
        filename=session.filename,
        vendor_name=session.vendor_name,
        status=session.status,
        error_message=session.error_message,
        total_questions=session.total_questions,
        answered_questions=session.answered_questions,
        confidence_threshold=session.confidence_threshold,
        created_at=session.created_at,
        updated_at=session.updated_at,
        question_column=session.question_column,
        answer_column=session.answer_column,
        remarks_column=session.remarks_column,
        header_row=session.header_row,
    )


@router.get("/sessions/{session_id}/questions", response_model=list[QuestionResponse])
async def get_session_questions(session_id: str):
    """Get all questions for a session."""
    session = await SessionRepository.get_by_id(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    questions = await QuestionRepository.get_by_session(session_id)
    return [
        QuestionResponse(
            id=q.id,
            session_id=q.session_id,
            row_number=q.row_number,
            question_text=q.question_text,
            remarks=q.remarks,
            answer_column=q.answer_column,
            question_type=q.question_type,
            choices=q.choices,
            created_at=q.created_at,
        )
        for q in questions
    ]


@router.get("/sessions/{session_id}/file")
async def get_session_file(session_id: str):
    """Get the Excel file for a session (for preview purposes)."""
    session = await SessionRepository.get_by_id(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    settings = get_settings()
    file_path = Path(settings.uploads_dir) / session.filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=session.filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
