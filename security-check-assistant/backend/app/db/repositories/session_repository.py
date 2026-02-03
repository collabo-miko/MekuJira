"""Repository for Session operations."""
import json
from datetime import datetime
from typing import Optional
from app.db.database import get_db
from app.models.session import Session, SessionStatus


class SessionRepository:
    """Repository for Session CRUD operations."""

    @staticmethod
    async def create(session: Session) -> Session:
        """Create a new session."""
        async with get_db() as db:
            await db.execute(
                """
                INSERT INTO sessions (
                    id, filename, vendor_name, status, error_message,
                    total_questions, answered_questions, confidence_threshold,
                    question_column, answer_column, remarks_column, header_row,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.id,
                    session.filename,
                    session.vendor_name,
                    session.status.value,
                    session.error_message,
                    session.total_questions,
                    session.answered_questions,
                    session.confidence_threshold,
                    session.question_column,
                    session.answer_column,
                    session.remarks_column,
                    session.header_row,
                    session.created_at.isoformat(),
                    session.updated_at.isoformat(),
                ),
            )
            await db.commit()
        return session

    @staticmethod
    async def get_by_id(session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        async with get_db() as db:
            row = await db.execute(
                "SELECT * FROM sessions WHERE id = ?", (session_id,)
            )
            row = await row.fetchone()
            if row is None:
                return None
            return SessionRepository._row_to_session(row)

    @staticmethod
    async def get_all(limit: int = 100, offset: int = 0) -> list[Session]:
        """Get all sessions with pagination."""
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM sessions ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            )
            rows = await cursor.fetchall()
            return [SessionRepository._row_to_session(row) for row in rows]

    @staticmethod
    async def update(session_id: str, **kwargs) -> Optional[Session]:
        """Update a session."""
        if not kwargs:
            return await SessionRepository.get_by_id(session_id)

        kwargs["updated_at"] = datetime.utcnow().isoformat()

        # Handle status enum
        if "status" in kwargs and isinstance(kwargs["status"], SessionStatus):
            kwargs["status"] = kwargs["status"].value

        set_clause = ", ".join(f"{key} = ?" for key in kwargs.keys())
        values = list(kwargs.values()) + [session_id]

        async with get_db() as db:
            await db.execute(
                f"UPDATE sessions SET {set_clause} WHERE id = ?",
                tuple(values),
            )
            await db.commit()
        return await SessionRepository.get_by_id(session_id)

    @staticmethod
    async def delete(session_id: str) -> bool:
        """Delete a session."""
        async with get_db() as db:
            cursor = await db.execute(
                "DELETE FROM sessions WHERE id = ?", (session_id,)
            )
            await db.commit()
            return cursor.rowcount > 0

    @staticmethod
    def _row_to_session(row) -> Session:
        """Convert a database row to Session model."""
        return Session(
            id=row["id"],
            filename=row["filename"],
            vendor_name=row["vendor_name"],
            status=SessionStatus(row["status"]),
            error_message=row["error_message"],
            total_questions=row["total_questions"],
            answered_questions=row["answered_questions"],
            confidence_threshold=row["confidence_threshold"],
            question_column=row["question_column"],
            answer_column=row["answer_column"],
            remarks_column=row["remarks_column"],
            header_row=row["header_row"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
