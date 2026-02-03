"""Format detector for Excel sheets using LLM analysis."""
import json
import re
from typing import Optional
import httpx

from app.core.excel_parser import SheetFormat
from app.config import get_settings


class FormatDetector:
    """Detects the format of security check sheets using heuristics and LLM."""

    # Common column header patterns
    QUESTION_PATTERNS = [
        r"質問", r"設問", r"確認事項", r"チェック項目", r"項目",
        r"question", r"item", r"check",
    ]
    ANSWER_PATTERNS = [
        r"回答", r"対応状況", r"実施状況", r"answer", r"response", r"status",
    ]
    REMARKS_PATTERNS = [
        r"備考", r"補足", r"コメント", r"説明", r"remarks", r"comment", r"notes",
    ]

    async def detect(
        self,
        sample_data: list[list[str]],
        sheet_name: str = "Sheet1",
    ) -> SheetFormat:
        """Detect the format of a sheet from sample data.

        First tries heuristic detection, falls back to LLM if confidence is low.
        """
        # Try heuristic detection first
        heuristic_result = self._detect_heuristic(sample_data, sheet_name)

        if heuristic_result.confidence >= 0.7:
            return heuristic_result

        # If confidence is low, try LLM detection
        # For now, just return the heuristic result
        # In production, this would call an LLM API
        return heuristic_result

    def _detect_heuristic(
        self,
        sample_data: list[list[str]],
        sheet_name: str,
    ) -> SheetFormat:
        """Detect format using heuristic pattern matching."""
        if not sample_data:
            return self._default_format(sheet_name)

        # Find header row (row with most pattern matches)
        best_header_row = 0
        best_score = 0
        header_info = None

        for row_idx, row in enumerate(sample_data[:10]):  # Check first 10 rows
            score, info = self._score_header_row(row)
            if score > best_score:
                best_score = score
                best_header_row = row_idx
                header_info = info

        if header_info is None or best_score == 0:
            return self._default_format(sheet_name)

        confidence = min(best_score / 3.0, 1.0)  # Normalize to max 1.0

        return SheetFormat(
            sheet_name=sheet_name,
            question_column=header_info.get("question", "A"),
            answer_column=header_info.get("answer", "B"),
            remarks_column=header_info.get("remarks"),
            header_row=best_header_row + 1,  # 1-based
            data_start_row=best_header_row + 2,  # 1-based, after header
            confidence=confidence,
        )

    def _score_header_row(self, row: list[str]) -> tuple[int, Optional[dict]]:
        """Score a row based on pattern matches and return column mapping."""
        score = 0
        info = {}

        for col_idx, cell in enumerate(row):
            if not cell:
                continue

            cell_lower = cell.lower()
            col_letter = self._index_to_column(col_idx)

            # Check for question column
            for pattern in self.QUESTION_PATTERNS:
                if re.search(pattern, cell_lower, re.IGNORECASE):
                    if "question" not in info:
                        info["question"] = col_letter
                        score += 1
                    break

            # Check for answer column
            for pattern in self.ANSWER_PATTERNS:
                if re.search(pattern, cell_lower, re.IGNORECASE):
                    if "answer" not in info:
                        info["answer"] = col_letter
                        score += 1
                    break

            # Check for remarks column
            for pattern in self.REMARKS_PATTERNS:
                if re.search(pattern, cell_lower, re.IGNORECASE):
                    if "remarks" not in info:
                        info["remarks"] = col_letter
                        score += 1
                    break

        return score, info if info else None

    def _index_to_column(self, index: int) -> str:
        """Convert 0-based index to column letter."""
        result = ""
        while index >= 0:
            result = chr(ord("A") + index % 26) + result
            index = index // 26 - 1
        return result

    def _default_format(self, sheet_name: str) -> SheetFormat:
        """Return a default format when detection fails."""
        return SheetFormat(
            sheet_name=sheet_name,
            question_column="A",
            answer_column="B",
            remarks_column="C",
            header_row=1,
            data_start_row=2,
            confidence=0.3,
        )

    async def detect_with_llm(
        self,
        sample_data: list[list[str]],
        sheet_name: str,
    ) -> SheetFormat:
        """Detect format using LLM (placeholder for future implementation)."""
        # This would call an LLM API with the sample data
        # For now, fall back to heuristic
        return self._detect_heuristic(sample_data, sheet_name)
