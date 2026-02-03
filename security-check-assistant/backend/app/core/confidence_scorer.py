"""Confidence score calculator for answers."""
from dataclasses import dataclass
from typing import Optional
from enum import Enum

from app.models.answer import AnswerSource
from app.models.knowledge import KnowledgeSearchResult


class ConfidenceLevel(str, Enum):
    """Confidence level thresholds."""

    STRICT = "strict"  # 0.95
    MODERATE = "moderate"  # 0.85
    STANDARD = "standard"  # 0.70


@dataclass
class ScoringFactors:
    """Factors that contribute to the confidence score."""

    exact_match_past: bool = False  # +0.3
    pageindex_has_sources: bool = False  # +0.2
    multiple_sources_agree: bool = False  # +0.2
    question_clarity: float = 0.1  # 0.1 - 0.3


class ConfidenceScorer:
    """Calculator for answer confidence scores."""

    # Base weights for different factors
    WEIGHT_EXACT_MATCH = 0.35
    WEIGHT_PAGEINDEX_SOURCES = 0.25
    WEIGHT_MULTIPLE_SOURCES = 0.20
    WEIGHT_QUESTION_CLARITY = 0.20

    # Threshold values
    THRESHOLDS = {
        ConfidenceLevel.STRICT: 0.95,
        ConfidenceLevel.MODERATE: 0.85,
        ConfidenceLevel.STANDARD: 0.70,
    }

    def calculate(
        self,
        pageindex_answer: Optional[str],
        pageindex_sources: list[dict],
        knowledge_results: list[KnowledgeSearchResult],
        question_text: str,
    ) -> tuple[float, list[AnswerSource]]:
        """Calculate confidence score and determine best sources.

        Returns:
            Tuple of (confidence_score, sources)
        """
        score = 0.0
        sources: list[AnswerSource] = []

        # Factor 1: Check for exact match in past answers
        best_knowledge_match = None
        best_knowledge_score = 0.0
        for kr in knowledge_results:
            if kr.similarity_score > best_knowledge_score:
                best_knowledge_score = kr.similarity_score
                best_knowledge_match = kr

        if best_knowledge_score >= 0.9:
            # Near-exact match found
            score += self.WEIGHT_EXACT_MATCH
            if best_knowledge_match:
                sources.append(
                    AnswerSource(
                        type="knowledge",
                        knowledge_id=best_knowledge_match.knowledge.id,
                        snippet=best_knowledge_match.knowledge.answer_text[:200],
                    )
                )
        elif best_knowledge_score >= 0.7:
            # Good match
            score += self.WEIGHT_EXACT_MATCH * 0.6
            if best_knowledge_match:
                sources.append(
                    AnswerSource(
                        type="knowledge",
                        knowledge_id=best_knowledge_match.knowledge.id,
                        snippet=best_knowledge_match.knowledge.answer_text[:200],
                    )
                )
        elif best_knowledge_score >= 0.5:
            # Partial match
            score += self.WEIGHT_EXACT_MATCH * 0.3

        # Factor 2: PageIndex sources
        if pageindex_answer and pageindex_sources:
            score += self.WEIGHT_PAGEINDEX_SOURCES
            for ps in pageindex_sources[:3]:  # Limit to top 3 sources
                sources.append(
                    AnswerSource(
                        type="pageindex",
                        document_id=ps.get("doc_id"),
                        document_name=ps.get("filename"),
                        page_number=ps.get("page"),
                        snippet=ps.get("snippet", "")[:200],
                    )
                )
        elif pageindex_answer:
            # Has answer but no sources
            score += self.WEIGHT_PAGEINDEX_SOURCES * 0.3

        # Factor 3: Multiple sources agree
        if len(sources) >= 2:
            score += self.WEIGHT_MULTIPLE_SOURCES
        elif len(sources) == 1:
            score += self.WEIGHT_MULTIPLE_SOURCES * 0.5

        # Factor 4: Question clarity (based on length and structure)
        clarity_score = self._assess_question_clarity(question_text)
        score += self.WEIGHT_QUESTION_CLARITY * clarity_score

        # Ensure score is within bounds
        return min(max(score, 0.0), 1.0), sources

    def _assess_question_clarity(self, question_text: str) -> float:
        """Assess the clarity of a question."""
        score = 0.5  # Base score

        # Longer questions are usually clearer
        word_count = len(question_text.split())
        if word_count >= 10:
            score += 0.2
        elif word_count >= 5:
            score += 0.1

        # Questions with specific terms are clearer
        specific_terms = [
            "パスワード", "暗号化", "認証", "アクセス制御",
            "ログ", "バックアップ", "脆弱性", "セキュリティ",
        ]
        if any(term in question_text for term in specific_terms):
            score += 0.2

        # Questions ending with ? are properly formed
        if question_text.strip().endswith("?") or question_text.strip().endswith("か"):
            score += 0.1

        return min(score, 1.0)

    def get_threshold(self, level: ConfidenceLevel) -> float:
        """Get the threshold value for a confidence level."""
        return self.THRESHOLDS.get(level, 0.70)

    def get_level_from_score(self, score: float) -> str:
        """Determine the confidence level based on score."""
        if score >= self.THRESHOLDS[ConfidenceLevel.STRICT]:
            return "high"
        elif score >= self.THRESHOLDS[ConfidenceLevel.STANDARD]:
            return "medium"
        else:
            return "low"

    def meets_threshold(self, score: float, level: ConfidenceLevel) -> bool:
        """Check if a score meets the specified threshold level."""
        return score >= self.get_threshold(level)
