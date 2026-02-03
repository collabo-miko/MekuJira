"""Tests for core business logic."""
import pytest

from app.core.format_detector import FormatDetector
from app.core.confidence_scorer import ConfidenceScorer, ConfidenceLevel
from app.models.knowledge import KnowledgeSearchResult, KnowledgeResponse
from datetime import datetime


class TestFormatDetector:
    """Tests for FormatDetector."""

    @pytest.fixture
    def detector(self):
        return FormatDetector()

    @pytest.mark.asyncio
    async def test_detect_with_clear_headers(self, detector):
        """Test detection with clear header row."""
        sample_data = [
            ["No.", "質問", "回答", "備考"],
            ["1", "パスワードポリシーは？", "", "必須"],
            ["2", "暗号化していますか？", "", ""],
        ]
        result = await detector.detect(sample_data, "Sheet1")
        assert result.question_column == "B"
        assert result.answer_column == "C"
        assert result.remarks_column == "D"
        assert result.header_row == 1

    @pytest.mark.asyncio
    async def test_detect_with_english_headers(self, detector):
        """Test detection with English headers."""
        sample_data = [
            ["ID", "Question", "Answer", "Notes"],
            ["1", "What is your password policy?", "", ""],
        ]
        result = await detector.detect(sample_data, "Sheet1")
        assert result.question_column == "B"
        assert result.answer_column == "C"

    @pytest.mark.asyncio
    async def test_detect_empty_data(self, detector):
        """Test detection with empty data."""
        result = await detector.detect([], "Sheet1")
        # Should return default format
        assert result.question_column == "A"
        assert result.answer_column == "B"
        assert result.confidence < 0.5


class TestConfidenceScorer:
    """Tests for ConfidenceScorer."""

    @pytest.fixture
    def scorer(self):
        return ConfidenceScorer()

    def test_calculate_high_confidence(self, scorer):
        """Test calculation with high confidence sources."""
        knowledge_results = [
            KnowledgeSearchResult(
                knowledge=KnowledgeResponse(
                    id="k-1",
                    question_text="パスワードポリシーは？",
                    answer_text="8文字以上",
                    vendor_name=None,
                    source_type="user_approved",
                    session_id=None,
                    created_at=datetime.utcnow(),
                ),
                similarity_score=0.95,
            )
        ]
        score, sources = scorer.calculate(
            pageindex_answer="8文字以上の英数字",
            pageindex_sources=[{"doc_id": "d-1", "page": 5}],
            knowledge_results=knowledge_results,
            question_text="パスワードの要件は何ですか？",
        )
        assert score >= 0.7
        assert len(sources) >= 1

    def test_calculate_low_confidence(self, scorer):
        """Test calculation with no good sources."""
        score, sources = scorer.calculate(
            pageindex_answer="",
            pageindex_sources=[],
            knowledge_results=[],
            question_text="不明な質問",
        )
        assert score < 0.5

    def test_threshold_levels(self, scorer):
        """Test threshold level retrieval."""
        assert scorer.get_threshold(ConfidenceLevel.STRICT) == 0.95
        assert scorer.get_threshold(ConfidenceLevel.MODERATE) == 0.85
        assert scorer.get_threshold(ConfidenceLevel.STANDARD) == 0.70

    def test_get_level_from_score(self, scorer):
        """Test getting level from score."""
        assert scorer.get_level_from_score(0.96) == "high"
        assert scorer.get_level_from_score(0.80) == "medium"
        assert scorer.get_level_from_score(0.50) == "low"
