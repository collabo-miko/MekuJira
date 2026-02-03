"""Database connection and initialization."""
import aiosqlite
from pathlib import Path
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from app.config import get_settings


DATABASE_PATH = Path("./data/knowledge.db")

# SQL for creating tables
CREATE_TABLES_SQL = """
-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    vendor_name TEXT,
    status TEXT NOT NULL DEFAULT 'uploaded',
    error_message TEXT,
    total_questions INTEGER DEFAULT 0,
    answered_questions INTEGER DEFAULT 0,
    confidence_threshold REAL DEFAULT 0.70,
    question_column TEXT,
    answer_column TEXT,
    remarks_column TEXT,
    header_row INTEGER,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Questions table
CREATE TABLE IF NOT EXISTS questions (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    row_number INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    remarks TEXT,
    answer_column TEXT NOT NULL,
    question_type TEXT DEFAULT 'unknown',
    choices TEXT,  -- JSON array
    created_at TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- Answers table
CREATE TABLE IF NOT EXISTS answers (
    id TEXT PRIMARY KEY,
    question_id TEXT NOT NULL UNIQUE,
    answer_text TEXT NOT NULL,
    confidence_score REAL NOT NULL,
    status TEXT DEFAULT 'pending',
    sources TEXT,  -- JSON array
    original_answer TEXT,
    modified_by_user INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- Knowledge base table
CREATE TABLE IF NOT EXISTS knowledge (
    id TEXT PRIMARY KEY,
    question_text TEXT NOT NULL,
    answer_text TEXT NOT NULL,
    vendor_name TEXT,
    source_type TEXT DEFAULT 'user_approved',
    session_id TEXT,
    created_at TEXT NOT NULL
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    pageindex_doc_id TEXT,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    page_count INTEGER,
    status TEXT DEFAULT 'uploading',
    error_message TEXT,
    indexed_at TEXT,
    created_at TEXT NOT NULL
);

-- Indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_questions_session_id ON questions(session_id);
CREATE INDEX IF NOT EXISTS idx_answers_question_id ON answers(question_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_question_text ON knowledge(question_text);
"""


async def init_database() -> None:
    """Initialize the database with required tables."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.executescript(CREATE_TABLES_SQL)
        await db.commit()


@asynccontextmanager
async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Get database connection context manager."""
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()


class Database:
    """Database wrapper for dependency injection."""

    def __init__(self):
        self._connection: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        """Connect to the database."""
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._connection = await aiosqlite.connect(DATABASE_PATH)
        self._connection.row_factory = aiosqlite.Row

    async def disconnect(self) -> None:
        """Disconnect from the database."""
        if self._connection:
            await self._connection.close()
            self._connection = None

    @property
    def connection(self) -> aiosqlite.Connection:
        """Get the current connection."""
        if not self._connection:
            raise RuntimeError("Database not connected")
        return self._connection

    async def execute(self, sql: str, params: tuple = ()) -> aiosqlite.Cursor:
        """Execute a SQL query."""
        return await self.connection.execute(sql, params)

    async def executemany(self, sql: str, params_list: list[tuple]) -> aiosqlite.Cursor:
        """Execute a SQL query with multiple parameter sets."""
        return await self.connection.executemany(sql, params_list)

    async def fetchone(self, sql: str, params: tuple = ()) -> aiosqlite.Row | None:
        """Fetch a single row."""
        cursor = await self.connection.execute(sql, params)
        return await cursor.fetchone()

    async def fetchall(self, sql: str, params: tuple = ()) -> list[aiosqlite.Row]:
        """Fetch all rows."""
        cursor = await self.connection.execute(sql, params)
        return await cursor.fetchall()

    async def commit(self) -> None:
        """Commit the current transaction."""
        await self.connection.commit()


# Global database instance
_db: Database | None = None


async def get_database() -> Database:
    """Get or create the database instance."""
    global _db
    if _db is None:
        _db = Database()
        await _db.connect()
        # Initialize tables
        async with get_db() as conn:
            await conn.executescript(CREATE_TABLES_SQL)
            await conn.commit()
    return _db
