"""Answer generation engine."""
import asyncio
from typing import Optional
from datetime import datetime

from app.core.pageindex_client import PageIndexClient, get_pageindex_client
from app.core.confidence_scorer import ConfidenceScorer, ConfidenceLevel
from app.db.repositories.knowledge_repository import KnowledgeRepository
from app.db.repositories.document_repository import DocumentRepository
from app.models.question import Question
from app.models.answer import Answer, AnswerStatus, AnswerSource
from app.models.knowledge import KnowledgeSearchResult


class AnswerEngine:
    """Engine for generating answers to security check questions."""

    def __init__(
        self,
        pageindex_client: Optional[PageIndexClient] = None,
        confidence_threshold: float = 0.70,
    ):
        """Initialize the answer engine."""
        self.pageindex = pageindex_client or get_pageindex_client()
        self.scorer = ConfidenceScorer()
        self.threshold = confidence_threshold

    async def generate_answer(
        self,
        question: Question,
        doc_ids: Optional[list[str]] = None,
    ) -> Answer:
        """Generate an answer for a single question.

        Args:
            question: The question to answer
            doc_ids: Optional list of PageIndex document IDs to search

        Returns:
            Generated Answer object
        """
        # Run searches in parallel
        tasks = []

        # Search PageIndex if we have documents
        pageindex_task = None
        if doc_ids:
            context = f"""
            あなたはセキュリティチェックシートの質問に回答するアシスタントです。
            質問に対して、参照ドキュメントから適切な回答を見つけてください。
            回答は簡潔かつ正確に記述してください。
            """
            pageindex_task = asyncio.create_task(
                self.pageindex.search(
                    query=question.question_text,
                    doc_ids=doc_ids,
                    context=context,
                )
            )
            tasks.append(pageindex_task)

        # Search knowledge base
        knowledge_task = asyncio.create_task(
            KnowledgeRepository.search(question.question_text, limit=5)
        )
        tasks.append(knowledge_task)

        # Wait for all searches
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process PageIndex results
        pageindex_answer = ""
        pageindex_sources: list[dict] = []
        if pageindex_task:
            pi_result = results[0] if not isinstance(results[0], Exception) else None
            if pi_result:
                pageindex_answer = pi_result.answer
                pageindex_sources = pi_result.sources

        # Process knowledge results
        knowledge_results: list[KnowledgeSearchResult] = []
        kb_result = results[-1] if not isinstance(results[-1], Exception) else []
        if isinstance(kb_result, list):
            knowledge_results = kb_result

        # Calculate confidence and determine sources
        confidence_score, sources = self.scorer.calculate(
            pageindex_answer=pageindex_answer,
            pageindex_sources=pageindex_sources,
            knowledge_results=knowledge_results,
            question_text=question.question_text,
        )

        # Determine the best answer text
        answer_text = self._select_best_answer(
            pageindex_answer=pageindex_answer,
            knowledge_results=knowledge_results,
            confidence_score=confidence_score,
        )

        # Determine status based on confidence
        status = AnswerStatus.PENDING
        if not answer_text:
            status = AnswerStatus.PENDING
            answer_text = ""  # No answer generated

        return Answer(
            question_id=question.id,
            answer_text=answer_text,
            confidence_score=confidence_score,
            status=status,
            sources=sources,
        )

    async def generate_batch(
        self,
        questions: list[Question],
        doc_ids: Optional[list[str]] = None,
    ) -> list[Answer]:
        """Generate answers for multiple questions.

        Args:
            questions: List of questions to answer
            doc_ids: Optional list of PageIndex document IDs

        Returns:
            List of generated Answer objects
        """
        # Get document IDs if not provided
        if doc_ids is None:
            indexed_docs = await DocumentRepository.get_indexed()
            doc_ids = [
                d.pageindex_doc_id
                for d in indexed_docs
                if d.pageindex_doc_id
            ]

        # Generate answers concurrently with some rate limiting
        batch_size = 5  # Process 5 questions at a time
        answers = []

        for i in range(0, len(questions), batch_size):
            batch = questions[i : i + batch_size]
            batch_tasks = [
                self.generate_answer(q, doc_ids)
                for q in batch
            ]
            batch_answers = await asyncio.gather(*batch_tasks, return_exceptions=True)

            for j, result in enumerate(batch_answers):
                if isinstance(result, Exception):
                    # Create a failed answer for this question
                    answers.append(
                        Answer(
                            question_id=batch[j].id,
                            answer_text="",
                            confidence_score=0.0,
                            status=AnswerStatus.PENDING,
                            sources=[],
                        )
                    )
                else:
                    answers.append(result)

        return answers

    def _select_best_answer(
        self,
        pageindex_answer: str,
        knowledge_results: list[KnowledgeSearchResult],
        confidence_score: float,
    ) -> str:
        """Select the best answer from available sources."""
        # If we have a high-confidence knowledge match, prefer it
        for kr in knowledge_results:
            if kr.similarity_score >= 0.85:
                return kr.knowledge.answer_text

        # If PageIndex returned an answer, use it
        if pageindex_answer:
            return pageindex_answer

        # Use the best knowledge match if available
        if knowledge_results:
            best = max(knowledge_results, key=lambda x: x.similarity_score)
            if best.similarity_score >= 0.5:
                return best.knowledge.answer_text

        # No good answer found
        return ""

    async def regenerate_answer(
        self,
        question: Question,
        doc_ids: Optional[list[str]] = None,
    ) -> Answer:
        """Regenerate an answer for a question.

        This is the same as generate_answer but explicitly named for clarity.
        """
        return await self.generate_answer(question, doc_ids)
