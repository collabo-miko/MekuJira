"""PageIndex API client wrapper with self-hosted support."""
import asyncio
import json
import os
import subprocess
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
    """Self-hosted PageIndex client using OpenAI API.

    This implementation uses the PageIndex library directly with OpenAI API
    instead of relying on the PageIndex cloud service.
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the client."""
        settings = get_settings()
        self.openai_api_key = openai_api_key or settings.openai_api_key
        self.model = settings.pageindex_model
        self.max_pages_per_node = settings.pageindex_max_pages_per_node
        self.max_tokens_per_node = settings.pageindex_max_tokens_per_node

        # Paths
        self.pageindex_dir = Path(__file__).parent.parent.parent.parent / "pageindex"
        self._indexed_docs: dict[str, dict] = {}  # doc_id -> {path, tree}

        # Backward compatibility: cloud API settings
        self.cloud_api_key = settings.pageindex_api_key
        self.use_cloud = settings.pageindex_use_cloud

    async def index_document(self, file_path: str) -> str:
        """Index a PDF document and generate tree structure.

        Args:
            file_path: Path to the PDF file

        Returns:
            Document ID for subsequent searches
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Generate a unique doc_id
        doc_id = f"doc_{path.stem}_{hash(file_path) % 10000}"

        # Run PageIndex tree generation
        try:
            result = await asyncio.to_thread(
                self._run_pageindex_tree_generation,
                file_path
            )

            self._indexed_docs[doc_id] = {
                "path": file_path,
                "tree": result,
            }

            return doc_id

        except Exception as e:
            # Log error but return doc_id for tracking purposes
            print(f"Warning: PageIndex tree generation failed: {e}")
            # Store with empty tree - will use fallback search
            self._indexed_docs[doc_id] = {
                "path": file_path,
                "tree": None,
            }
            return doc_id

    def _run_pageindex_tree_generation(self, pdf_path: str) -> Optional[dict]:
        """Run PageIndex script to generate tree structure.

        This method invokes the PageIndex library to create a hierarchical
        index of the PDF document.
        """
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required for self-hosted PageIndex")

        # Check if pageindex directory exists
        if not self.pageindex_dir.exists():
            raise FileNotFoundError(
                f"PageIndex directory not found at {self.pageindex_dir}. "
                "Please clone PageIndex: git clone https://github.com/VectifyAI/PageIndex.git pageindex"
            )

        # Set up environment with API key
        env = os.environ.copy()
        env["CHATGPT_API_KEY"] = self.openai_api_key

        # Run PageIndex tree generation
        try:
            result = subprocess.run(
                [
                    "python3", "run_pageindex.py",
                    "--pdf_path", pdf_path,
                    "--model", self.model,
                    "--max_pages_per_node", str(self.max_pages_per_node),
                    "--max_tokens_per_node", str(self.max_tokens_per_node),
                    "--output_format", "json",
                ],
                cwd=str(self.pageindex_dir),
                env=env,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout for large documents
            )

            if result.returncode != 0:
                raise RuntimeError(f"PageIndex failed: {result.stderr}")

            return json.loads(result.stdout)

        except subprocess.TimeoutExpired:
            raise RuntimeError("PageIndex tree generation timed out")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse PageIndex output: {e}")

    async def search(
        self,
        query: str,
        doc_ids: list[str],
        context: Optional[str] = None,
    ) -> PageIndexSearchResult:
        """Search across indexed documents for an answer.

        Uses the OpenAI API to perform inference-based retrieval
        on the pre-built document trees.

        Args:
            query: The question to answer
            doc_ids: List of document IDs to search
            context: Optional system context for the search

        Returns:
            PageIndexSearchResult with answer, sources, and confidence
        """
        if not self.openai_api_key:
            return PageIndexSearchResult(
                answer="",
                sources=[],
                confidence=0.0,
            )

        # Collect document trees for the query
        doc_trees = []
        for doc_id in doc_ids:
            if doc_id in self._indexed_docs:
                doc_info = self._indexed_docs[doc_id]
                if doc_info.get("tree"):
                    doc_trees.append({
                        "doc_id": doc_id,
                        "path": doc_info["path"],
                        "tree": doc_info["tree"],
                    })

        if not doc_trees:
            # No indexed documents available
            return PageIndexSearchResult(
                answer="",
                sources=[],
                confidence=0.0,
            )

        # Run inference-based search
        try:
            result = await asyncio.to_thread(
                self._run_pageindex_search,
                query,
                doc_trees,
                context,
            )
            return result
        except Exception as e:
            print(f"Warning: PageIndex search failed: {e}")
            return PageIndexSearchResult(
                answer="",
                sources=[],
                confidence=0.0,
            )

    def _run_pageindex_search(
        self,
        query: str,
        doc_trees: list[dict],
        context: Optional[str] = None,
    ) -> PageIndexSearchResult:
        """Run PageIndex search using the document trees.

        This performs tree traversal and LLM-based retrieval.
        """
        if not self.pageindex_dir.exists():
            raise FileNotFoundError(f"PageIndex directory not found at {self.pageindex_dir}")

        env = os.environ.copy()
        env["CHATGPT_API_KEY"] = self.openai_api_key

        # Prepare search input
        search_input = {
            "query": query,
            "context": context or "セキュリティチェックシートの質問に対する回答を探してください。",
            "documents": doc_trees,
        }

        # Write input to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(search_input, f, ensure_ascii=False)
            input_path = f.name

        try:
            result = subprocess.run(
                [
                    "python3", "run_search.py",
                    "--input", input_path,
                    "--model", self.model,
                ],
                cwd=str(self.pageindex_dir),
                env=env,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout for search
            )

            if result.returncode != 0:
                raise RuntimeError(f"PageIndex search failed: {result.stderr}")

            output = json.loads(result.stdout)

            return PageIndexSearchResult(
                answer=output.get("answer", ""),
                sources=output.get("sources", []),
                confidence=output.get("confidence", 0.0),
            )

        except subprocess.TimeoutExpired:
            raise RuntimeError("PageIndex search timed out")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse PageIndex search output: {e}")
        finally:
            # Clean up temp file
            Path(input_path).unlink(missing_ok=True)

    async def get_document_status(self, doc_id: str) -> dict:
        """Get the indexing status of a document.

        Args:
            doc_id: Document ID to check

        Returns:
            Status dictionary with doc_id, status, and page_count
        """
        if doc_id in self._indexed_docs:
            doc_info = self._indexed_docs[doc_id]
            has_tree = doc_info.get("tree") is not None

            return {
                "doc_id": doc_id,
                "status": "indexed" if has_tree else "pending",
                "page_count": len(doc_info.get("tree", {}).get("pages", [])) if has_tree else 0,
            }

        return {
            "doc_id": doc_id,
            "status": "not_found",
            "page_count": 0,
        }

    def get_cached_doc_id(self, file_path: str) -> Optional[str]:
        """Get cached doc_id for a file path.

        Args:
            file_path: File path to look up

        Returns:
            Document ID if found, None otherwise
        """
        for doc_id, doc_info in self._indexed_docs.items():
            if doc_info.get("path") == file_path:
                return doc_id
        return None


# Singleton instance
_client: Optional[PageIndexClient] = None


def get_pageindex_client() -> PageIndexClient:
    """Get or create the PageIndex client instance."""
    global _client
    if _client is None:
        _client = PageIndexClient()
    return _client
