"""Repository for Document operations."""
from datetime import datetime
from typing import Optional
from app.db.database import get_db
from app.models.document import Document, DocumentStatus


class DocumentRepository:
    """Repository for Document CRUD operations."""

    @staticmethod
    async def create(document: Document) -> Document:
        """Create a new document."""
        async with get_db() as db:
            await db.execute(
                """
                INSERT INTO documents (
                    id, pageindex_doc_id, filename, file_path, page_count,
                    status, error_message, indexed_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document.id,
                    document.pageindex_doc_id,
                    document.filename,
                    document.file_path,
                    document.page_count,
                    document.status.value,
                    document.error_message,
                    document.indexed_at.isoformat() if document.indexed_at else None,
                    document.created_at.isoformat(),
                ),
            )
            await db.commit()
        return document

    @staticmethod
    async def get_by_id(document_id: str) -> Optional[Document]:
        """Get a document by ID."""
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM documents WHERE id = ?", (document_id,)
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            return DocumentRepository._row_to_document(row)

    @staticmethod
    async def get_all(status: Optional[DocumentStatus] = None) -> list[Document]:
        """Get all documents, optionally filtered by status."""
        async with get_db() as db:
            if status:
                cursor = await db.execute(
                    "SELECT * FROM documents WHERE status = ? ORDER BY created_at DESC",
                    (status.value,),
                )
            else:
                cursor = await db.execute(
                    "SELECT * FROM documents ORDER BY created_at DESC"
                )
            rows = await cursor.fetchall()
            return [DocumentRepository._row_to_document(row) for row in rows]

    @staticmethod
    async def get_indexed() -> list[Document]:
        """Get all indexed documents."""
        return await DocumentRepository.get_all(status=DocumentStatus.INDEXED)

    @staticmethod
    async def update(document_id: str, **kwargs) -> Optional[Document]:
        """Update a document."""
        if not kwargs:
            return await DocumentRepository.get_by_id(document_id)

        # Handle status enum
        if "status" in kwargs and isinstance(kwargs["status"], DocumentStatus):
            kwargs["status"] = kwargs["status"].value

        # Handle indexed_at datetime
        if "indexed_at" in kwargs and isinstance(kwargs["indexed_at"], datetime):
            kwargs["indexed_at"] = kwargs["indexed_at"].isoformat()

        set_clause = ", ".join(f"{key} = ?" for key in kwargs.keys())
        values = list(kwargs.values()) + [document_id]

        async with get_db() as db:
            await db.execute(
                f"UPDATE documents SET {set_clause} WHERE id = ?",
                tuple(values),
            )
            await db.commit()
        return await DocumentRepository.get_by_id(document_id)

    @staticmethod
    async def delete(document_id: str) -> bool:
        """Delete a document."""
        async with get_db() as db:
            cursor = await db.execute(
                "DELETE FROM documents WHERE id = ?", (document_id,)
            )
            await db.commit()
            return cursor.rowcount > 0

    @staticmethod
    def _row_to_document(row) -> Document:
        """Convert a database row to Document model."""
        indexed_at = None
        if row["indexed_at"]:
            indexed_at = datetime.fromisoformat(row["indexed_at"])
        return Document(
            id=row["id"],
            pageindex_doc_id=row["pageindex_doc_id"],
            filename=row["filename"],
            file_path=row["file_path"],
            page_count=row["page_count"],
            status=DocumentStatus(row["status"]),
            error_message=row["error_message"],
            indexed_at=indexed_at,
            created_at=datetime.fromisoformat(row["created_at"]),
        )
