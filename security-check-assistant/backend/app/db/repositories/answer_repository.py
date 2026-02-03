"""Repository for Answer operations."""
import json
from datetime import datetime
from typing import Optional
from app.db.database import get_db
from app.models.answer import Answer, AnswerStatus, AnswerSource


class AnswerRepository:
    """Repository for Answer CRUD operations."""

    @staticmethod
    async def create(answer: Answer) -> Answer:
        """Create a new answer."""
        async with get_db() as db:
            await db.execute(
                """
                INSERT INTO answers (
                    id, question_id, answer_text, confidence_score, status,
                    sources, original_answer, modified_by_user, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    answer.id,
                    answer.question_id,
                    answer.answer_text,
                    answer.confidence_score,
                    answer.status.value,
                    json.dumps([s.model_dump() for s in answer.sources]),
                    answer.original_answer,
                    1 if answer.modified_by_user else 0,
                    answer.created_at.isoformat(),
                    answer.updated_at.isoformat(),
                ),
            )
            await db.commit()
        return answer

    @staticmethod
    async def create_many(answers: list[Answer]) -> list[Answer]:
        """Create multiple answers."""
        async with get_db() as db:
            await db.executemany(
                """
                INSERT INTO answers (
                    id, question_id, answer_text, confidence_score, status,
                    sources, original_answer, modified_by_user, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        a.id,
                        a.question_id,
                        a.answer_text,
                        a.confidence_score,
                        a.status.value,
                        json.dumps([s.model_dump() for s in a.sources]),
                        a.original_answer,
                        1 if a.modified_by_user else 0,
                        a.created_at.isoformat(),
                        a.updated_at.isoformat(),
                    )
                    for a in answers
                ],
            )
            await db.commit()
        return answers

    @staticmethod
    async def get_by_id(answer_id: str) -> Optional[Answer]:
        """Get an answer by ID."""
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM answers WHERE id = ?", (answer_id,)
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            return AnswerRepository._row_to_answer(row)

    @staticmethod
    async def get_by_question(question_id: str) -> Optional[Answer]:
        """Get answer for a question."""
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM answers WHERE question_id = ?", (question_id,)
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            return AnswerRepository._row_to_answer(row)

    @staticmethod
    async def get_by_session(session_id: str) -> list[Answer]:
        """Get all answers for a session."""
        async with get_db() as db:
            cursor = await db.execute(
                """
                SELECT a.* FROM answers a
                JOIN questions q ON a.question_id = q.id
                WHERE q.session_id = ?
                ORDER BY q.row_number
                """,
                (session_id,),
            )
            rows = await cursor.fetchall()
            return [AnswerRepository._row_to_answer(row) for row in rows]

    @staticmethod
    async def update(answer_id: str, **kwargs) -> Optional[Answer]:
        """Update an answer."""
        if not kwargs:
            return await AnswerRepository.get_by_id(answer_id)

        kwargs["updated_at"] = datetime.utcnow().isoformat()

        # Handle status enum
        if "status" in kwargs and isinstance(kwargs["status"], AnswerStatus):
            kwargs["status"] = kwargs["status"].value

        # Handle sources
        if "sources" in kwargs and isinstance(kwargs["sources"], list):
            kwargs["sources"] = json.dumps(
                [s.model_dump() if hasattr(s, "model_dump") else s for s in kwargs["sources"]]
            )

        # Handle modified_by_user
        if "modified_by_user" in kwargs:
            kwargs["modified_by_user"] = 1 if kwargs["modified_by_user"] else 0

        set_clause = ", ".join(f"{key} = ?" for key in kwargs.keys())
        values = list(kwargs.values()) + [answer_id]

        async with get_db() as db:
            await db.execute(
                f"UPDATE answers SET {set_clause} WHERE id = ?",
                tuple(values),
            )
            await db.commit()
        return await AnswerRepository.get_by_id(answer_id)

    @staticmethod
    async def count_by_session(session_id: str) -> int:
        """Count answers for a session."""
        async with get_db() as db:
            cursor = await db.execute(
                """
                SELECT COUNT(*) FROM answers a
                JOIN questions q ON a.question_id = q.id
                WHERE q.session_id = ?
                """,
                (session_id,),
            )
            row = await cursor.fetchone()
            return row[0] if row else 0

    @staticmethod
    async def count_approved_by_session(session_id: str) -> int:
        """Count approved answers for a session."""
        async with get_db() as db:
            cursor = await db.execute(
                """
                SELECT COUNT(*) FROM answers a
                JOIN questions q ON a.question_id = q.id
                WHERE q.session_id = ? AND (a.status = 'approved' OR a.status = 'modified')
                """,
                (session_id,),
            )
            row = await cursor.fetchone()
            return row[0] if row else 0

    @staticmethod
    def _row_to_answer(row) -> Answer:
        """Convert a database row to Answer model."""
        sources = []
        if row["sources"]:
            sources_data = json.loads(row["sources"])
            sources = [AnswerSource(**s) for s in sources_data]
        return Answer(
            id=row["id"],
            question_id=row["question_id"],
            answer_text=row["answer_text"],
            confidence_score=row["confidence_score"],
            status=AnswerStatus(row["status"]),
            sources=sources,
            original_answer=row["original_answer"],
            modified_by_user=bool(row["modified_by_user"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
