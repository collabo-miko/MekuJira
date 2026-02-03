"""File handling utilities."""
from pathlib import Path


def sanitize_filename(filename: str) -> str:
    """Return a safe filename without path components.

    Raises:
        ValueError: if the filename is empty or invalid.
    """
    safe_name = Path(filename).name
    if not safe_name or safe_name in {".", ".."}:
        raise ValueError("Invalid filename.")
    return safe_name
