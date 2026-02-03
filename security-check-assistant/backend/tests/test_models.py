"""Tests for data models."""
import pytest
from datetime import datetime

from app.models.session import Session, SessionStatus
from app.models.question import Question, QuestionType
from app.models.answer import Answer, AnswerStatus, AnswerSource
from app.models.document import Document, DocumentStatus
from app.models.knowledge import Knowledge


class TestSessionModel:
    """Tests for Session model."""

    def test_session_creation(self):
        """Test creating a session with defaults."""
        session = Session(filename="test.xlsx")
        assert session.filename == "test.xlsx"
        assert session.status == SessionStatus.UPLOADED
        assert session.confidence_threshold == 0.70
        assert session.id is not None

    def test_session_with_all_fields(self):
        """Test creating a session with all fields."""
        session = Session(
            filename="test.xlsx",
            vendor_name="Test Corp",
            status=SessionStatus.DETECTED,
            confidence_threshold=0.85,
            question_column="A",
            answer_column="B",
            remarks_column="C",
            header_row=3,
        )
        assert session.vendor_name == "Test Corp"
        assert session.status == SessionStatus.DETECTED
        assert session.question_column == "A"
        assert session.header_row == 3


class TestQuestionModel:
    """Tests for Question model."""

    def test_question_creation(self):
        """Test creating a question."""
        question = Question(
            session_id="session-1",
            row_number=5,
            question_text="パスワードポリシーは？",
            answer_column="B",
        )
        assert question.session_id == "session-1"
        assert question.row_number == 5
        assert question.question_type == QuestionType.UNKNOWN

    def test_question_with_choices(self):
        """Test creating a question with choices."""
        question = Question(
            session_id="session-1",
            row_number=10,
            question_text="対応していますか？",
            answer_column="C",
            question_type=QuestionType.YES_NO,
            choices=["はい", "いいえ"],
        )
        assert question.question_type == QuestionType.YES_NO
        assert question.choices == ["はい", "いいえ"]


class TestAnswerModel:
    """Tests for Answer model."""

    def test_answer_creation(self):
        """Test creating an answer."""
        answer = Answer(
            question_id="q-1",
            answer_text="対応しています",
            confidence_score=0.85,
        )
        assert answer.question_id == "q-1"
        assert answer.confidence_score == 0.85
        assert answer.status == AnswerStatus.PENDING
        assert answer.sources == []

    def test_answer_with_sources(self):
        """Test creating an answer with sources."""
        source = AnswerSource(
            type="pageindex",
            document_id="doc-1",
            document_name="policy.pdf",
            page_number=5,
            snippet="パスワードは8文字以上...",
        )
        answer = Answer(
            question_id="q-1",
            answer_text="8文字以上",
            confidence_score=0.9,
            sources=[source],
        )
        assert len(answer.sources) == 1
        assert answer.sources[0].document_name == "policy.pdf"


class TestDocumentModel:
    """Tests for Document model."""

    def test_document_creation(self):
        """Test creating a document."""
        doc = Document(
            filename="policy.pdf",
            file_path="/data/documents/policy.pdf",
        )
        assert doc.filename == "policy.pdf"
        assert doc.status == DocumentStatus.UPLOADING
        assert doc.pageindex_doc_id is None


class TestKnowledgeModel:
    """Tests for Knowledge model."""

    def test_knowledge_creation(self):
        """Test creating a knowledge item."""
        knowledge = Knowledge(
            question_text="パスワードの要件は？",
            answer_text="8文字以上の英数字",
            vendor_name="Test Corp",
        )
        assert knowledge.question_text == "パスワードの要件は？"
        assert knowledge.source_type == "user_approved"
