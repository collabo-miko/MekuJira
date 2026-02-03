"""Test configuration and fixtures."""
import os
import pytest
import tempfile
from pathlib import Path


@pytest.fixture(scope="session")
def test_data_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir) / "data"
        data_dir.mkdir(parents=True)
        (data_dir / "documents").mkdir()
        (data_dir / "uploads").mkdir()
        yield data_dir


@pytest.fixture(autouse=True)
def setup_test_env(test_data_dir):
    """Setup test environment variables."""
    os.environ["DATA_DIR"] = str(test_data_dir)
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{test_data_dir}/test.db"
