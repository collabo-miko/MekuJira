"""Repository for Question operations."""
import json
from datetime import datetime
from typing import Optional
from app.db.database import get_db
from app.models.question import Question, QuestionType


class QuestionRepository:
    """Repository for Question CRUD operations."""

    @staticmethod
    async def create(question: Question) -> Question:
        """Create a new question."""
        async with get_db() as db:
            await db.execute(
                """
                INSERT INTO questions (
                    id, session_id, row_number, question_text, remarks,
                    answer_column, question_type, choices, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    question.id,
                    question.session_id,
                    question.row_number,
                    question.question_text,
                    question.remarks,
                    question.answer_column,
                    question.question_type.value,
                    json.dumps(question.choices) if question.choices else None,
                    question.created_at.isoformat(),
                ),
            )
            await db.commit()
        return question

    @staticmethod
    async def create_many(questions: list[Question]) -> list[Question]:
        """Create multiple questions."""
        async with get_db() as db:
            await db.executemany(
                """
                INSERT INTO questions (
                    id, session_id, row_number, question_text, remarks,
                    answer_column, question_type, choices, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        q.id,
                        q.session_id,
                        q.row_number,
                        q.question_text,
                        q.remarks,
                        q.answer_column,
                        q.question_type.value,
                        json.dumps(q.choices) if q.choices else None,
                        q.created_at.isoformat(),
                    )
                    for q in questions
                ],
            )
            await db.commit()
        return questions

    @staticmethod
    async def get_by_id(question_id: str) -> Optional[Question]:
        """Get a question by ID."""
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM questions WHERE id = ?", (question_id,)
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            return QuestionRepository._row_to_question(row)

    @staticmethod
    async def get_by_session(session_id: str) -> list[Question]:
        """Get all questions for a session."""
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM questions WHERE session_id = ? ORDER BY row_number",
                (session_id,),
            )
            rows = await cursor.fetchall()
            return [QuestionRepository._row_to_question(row) for row in rows]

    @staticmethod
    async def count_by_session(session_id: str) -> int:
        """Count questions for a session."""
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM questions WHERE session_id = ?",
                (session_id,),
            )
            row = await cursor.fetchone()
            return row[0] if row else 0

    @staticmethod
    async def delete_by_session(session_id: str) -> int:
        """Delete all questions for a session."""
        async with get_db() as db:
            cursor = await db.execute(
                "DELETE FROM questions WHERE session_id = ?", (session_id,)
            )
            await db.commit()
            return cursor.rowcount

    @staticmethod
    def _row_to_question(row) -> Question:
        """Convert a database row to Question model."""
        choices = None
        if row["choices"]:
            choices = json.loads(row["choices"])
        return Question(
            id=row["id"],
            session_id=row["session_id"],
            row_number=row["row_number"],
            question_text=row["question_text"],
            remarks=row["remarks"],
            answer_column=row["answer_column"],
            question_type=QuestionType(row["question_type"]),
            choices=choices,
            created_at=datetime.fromisoformat(row["created_at"]),
        )
