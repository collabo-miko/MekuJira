"""PageIndex API client wrapper."""
import asyncio
import httpx
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from app.config import get_settings


@dataclass
class PageIndexSearchResult:
    """Result from PageIndex search."""

    answer: str
    sources: list[dict]
    confidence: float


class PageIndexClient:
    """Wrapper for PageIndex API.

    Note: This is a mock implementation as the actual PageIndex SDK
    may not be available. Replace with actual SDK when available.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the client."""
        self.api_key = api_key or get_settings().pageindex_api_key
        self._doc_cache: dict[str, str] = {}  # filename -> doc_id
        self._base_url = "https://api.pageindex.io/v1"

    async def index_document(self, file_path: str) -> str:
        """Index a document and return the doc_id.

        In the actual implementation, this would:
        1. Upload the file to PageIndex
        2. Wait for indexing to complete
        3. Return the doc_id
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # For now, return a mock doc_id based on filename
        # In production, this would call the actual PageIndex API
        doc_id = f"doc_{path.stem}_{hash(file_path) % 10000}"
        self._doc_cache[file_path] = doc_id

        # Simulate API call
        if self.api_key:
            try:
                async with httpx.AsyncClient() as client:
                    # This is a placeholder for the actual API call
                    # response = await client.post(
                    #     f"{self._base_url}/documents",
                    #     headers={"Authorization": f"Bearer {self.api_key}"},
                    #     files={"file": open(file_path, "rb")}
                    # )
                    pass
            except Exception:
                # Fall back to mock
                pass

        return doc_id

    async def search(
        self,
        query: str,
        doc_ids: list[str],
        context: Optional[str] = None,
    ) -> PageIndexSearchResult:
        """Search across documents for an answer to the query.

        In the actual implementation, this would call PageIndex chat API.
        """
        # Build the prompt for search
        system_prompt = context or "セキュリティチェックシートの質問に対する回答を探してください。"

        # For now, return a mock response
        # In production, this would call the actual PageIndex API
        if self.api_key and doc_ids:
            try:
                async with httpx.AsyncClient() as client:
                    # This is a placeholder for the actual API call
                    # response = await client.post(
                    #     f"{self._base_url}/chat/completions",
                    #     headers={"Authorization": f"Bearer {self.api_key}"},
                    #     json={
                    #         "messages": [
                    #             {"role": "system", "content": system_prompt},
                    #             {"role": "user", "content": query}
                    #         ],
                    #         "doc_id": doc_ids
                    #     }
                    # )
                    pass
            except Exception:
                pass

        # Return mock result for testing
        return PageIndexSearchResult(
            answer="",  # Empty answer indicates no match found
            sources=[],
            confidence=0.0,
        )

    async def get_document_status(self, doc_id: str) -> dict:
        """Get the indexing status of a document."""
        # In production, this would call the actual PageIndex API
        return {
            "doc_id": doc_id,
            "status": "indexed",
            "page_count": 0,
        }

    def get_cached_doc_id(self, file_path: str) -> Optional[str]:
        """Get cached doc_id for a file path."""
        return self._doc_cache.get(file_path)


# Singleton instance
_client: Optional[PageIndexClient] = None


def get_pageindex_client() -> PageIndexClient:
    """Get or create the PageIndex client instance."""
    global _client
    if _client is None:
        _client = PageIndexClient()
    return _client
