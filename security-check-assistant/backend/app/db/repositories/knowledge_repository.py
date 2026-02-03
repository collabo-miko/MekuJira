"""Repository for Knowledge operations."""
from datetime import datetime
from typing import Optional
from app.db.database import get_db
from app.models.knowledge import Knowledge, KnowledgeSearchResult, KnowledgeResponse


class KnowledgeRepository:
    """Repository for Knowledge CRUD operations."""

    @staticmethod
    async def create(knowledge: Knowledge) -> Knowledge:
        """Create a new knowledge item."""
        async with get_db() as db:
            await db.execute(
                """
                INSERT INTO knowledge (
                    id, question_text, answer_text, vendor_name,
                    source_type, session_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    knowledge.id,
                    knowledge.question_text,
                    knowledge.answer_text,
                    knowledge.vendor_name,
                    knowledge.source_type,
                    knowledge.session_id,
                    knowledge.created_at.isoformat(),
                ),
            )
            await db.commit()
        return knowledge

    @staticmethod
    async def create_many(items: list[Knowledge]) -> list[Knowledge]:
        """Create multiple knowledge items."""
        async with get_db() as db:
            await db.executemany(
                """
                INSERT INTO knowledge (
                    id, question_text, answer_text, vendor_name,
                    source_type, session_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        k.id,
                        k.question_text,
                        k.answer_text,
                        k.vendor_name,
                        k.source_type,
                        k.session_id,
                        k.created_at.isoformat(),
                    )
                    for k in items
                ],
            )
            await db.commit()
        return items

    @staticmethod
    async def get_by_id(knowledge_id: str) -> Optional[Knowledge]:
        """Get a knowledge item by ID."""
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM knowledge WHERE id = ?", (knowledge_id,)
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            return KnowledgeRepository._row_to_knowledge(row)

    @staticmethod
    async def get_all(limit: int = 100, offset: int = 0) -> list[Knowledge]:
        """Get all knowledge items with pagination."""
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM knowledge ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            )
            rows = await cursor.fetchall()
            return [KnowledgeRepository._row_to_knowledge(row) for row in rows]

    @staticmethod
    async def search(query: str, limit: int = 10) -> list[KnowledgeSearchResult]:
        """Search knowledge base by question text.

        Note: This is a simple LIKE-based search. For production,
        consider using a proper similarity search or vector DB.
        """
        async with get_db() as db:
            # Simple keyword-based search
            search_term = f"%{query}%"
            cursor = await db.execute(
                """
                SELECT * FROM knowledge
                WHERE question_text LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (search_term, limit),
            )
            rows = await cursor.fetchall()

            results = []
            for row in rows:
                knowledge = KnowledgeRepository._row_to_knowledge(row)
                # Calculate simple similarity score based on keyword match
                score = KnowledgeRepository._calculate_similarity(query, knowledge.question_text)
                results.append(
                    KnowledgeSearchResult(
                        knowledge=KnowledgeResponse(
                            id=knowledge.id,
                            question_text=knowledge.question_text,
                            answer_text=knowledge.answer_text,
                            vendor_name=knowledge.vendor_name,
                            source_type=knowledge.source_type,
                            session_id=knowledge.session_id,
                            created_at=knowledge.created_at,
                        ),
                        similarity_score=score,
                    )
                )

            # Sort by similarity score
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            return results

    @staticmethod
    async def count() -> int:
        """Count total knowledge items."""
        async with get_db() as db:
            cursor = await db.execute("SELECT COUNT(*) FROM knowledge")
            row = await cursor.fetchone()
            return row[0] if row else 0

    @staticmethod
    def _calculate_similarity(query: str, text: str) -> float:
        """Calculate simple word overlap similarity."""
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())

        if not query_words or not text_words:
            return 0.0

        intersection = query_words.intersection(text_words)
        union = query_words.union(text_words)

        # Jaccard similarity
        return len(intersection) / len(union) if union else 0.0

    @staticmethod
    def _row_to_knowledge(row) -> Knowledge:
        """Convert a database row to Knowledge model."""
        return Knowledge(
            id=row["id"],
            question_text=row["question_text"],
            answer_text=row["answer_text"],
            vendor_name=row["vendor_name"],
            source_type=row["source_type"],
            session_id=row["session_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
