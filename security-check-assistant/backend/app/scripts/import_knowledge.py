#!/usr/bin/env python
"""
CSVファイルからナレッジベースにデータをインポートするスクリプト。

使用方法:
    python -m app.scripts.import_knowledge <csv_file_path>

CSVフォーマット:
    - question_text: 質問文（必須）
    - answer_text: 回答文（必須）
    - vendor_name: ベンダー名（オプション）
    - source_document: 参照元（オプション）
    - created_at: 作成日時（オプション、YYYY-MM-DD形式）

例:
    python -m app.scripts.import_knowledge data/imports/knowledge.csv
"""

import asyncio
import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import aiosqlite


# Database settings (relative to backend directory)
DATABASE_PATH = Path("./data/knowledge.db")

# Required columns
REQUIRED_COLUMNS = {"question_text", "answer_text"}

# Optional columns with default values
OPTIONAL_COLUMNS = {
    "vendor_name": None,
    "source_document": None,
    "created_at": None,
}


def generate_id() -> str:
    """Generate a unique ID."""
    import uuid
    return str(uuid.uuid4())


def parse_date(date_str: Optional[str]) -> datetime:
    """Parse date string or return current datetime."""
    if not date_str:
        return datetime.utcnow()

    # Try different date formats
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    # If all formats fail, return current datetime
    print(f"  Warning: Could not parse date '{date_str}', using current time")
    return datetime.utcnow()


def validate_csv(csv_path: Path) -> tuple[bool, list[str]]:
    """Validate CSV file structure."""
    errors = []

    if not csv_path.exists():
        errors.append(f"File not found: {csv_path}")
        return False, errors

    try:
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            # Check headers
            if reader.fieldnames is None:
                errors.append("CSV file is empty or has no headers")
                return False, errors

            headers = set(reader.fieldnames)
            missing = REQUIRED_COLUMNS - headers

            if missing:
                errors.append(f"Missing required columns: {', '.join(missing)}")
                return False, errors

            # Check for at least one data row
            first_row = next(reader, None)
            if first_row is None:
                errors.append("CSV file has no data rows")
                return False, errors

    except UnicodeDecodeError:
        errors.append("CSV file encoding error. Please save as UTF-8")
        return False, errors
    except Exception as e:
        errors.append(f"Error reading CSV: {e}")
        return False, errors

    return True, []


async def ensure_database_exists() -> None:
    """Ensure database and tables exist."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS knowledge (
        id TEXT PRIMARY KEY,
        question_text TEXT NOT NULL,
        answer_text TEXT NOT NULL,
        vendor_name TEXT,
        source_type TEXT DEFAULT 'imported',
        session_id TEXT,
        created_at TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_knowledge_question_text ON knowledge(question_text);
    """

    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.executescript(create_table_sql)
        await db.commit()


async def import_csv(csv_path: Path, dry_run: bool = False) -> tuple[int, int, list[str]]:
    """
    Import CSV data into knowledge base.

    Returns:
        tuple: (imported_count, skipped_count, errors)
    """
    await ensure_database_exists()

    imported = 0
    skipped = 0
    errors = []

    async with aiosqlite.connect(DATABASE_PATH) as db:
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            batch = []
            row_num = 1  # Start from 1 (header is row 0)

            for row in reader:
                row_num += 1

                # Get required fields
                question_text = row.get("question_text", "").strip()
                answer_text = row.get("answer_text", "").strip()

                # Validate required fields
                if not question_text:
                    errors.append(f"Row {row_num}: Empty question_text")
                    skipped += 1
                    continue

                if not answer_text:
                    errors.append(f"Row {row_num}: Empty answer_text")
                    skipped += 1
                    continue

                # Get optional fields
                vendor_name = row.get("vendor_name", "").strip() or None
                created_at = parse_date(row.get("created_at", "").strip())

                # Add to batch
                batch.append((
                    generate_id(),
                    question_text,
                    answer_text,
                    vendor_name,
                    "imported",  # source_type
                    None,  # session_id
                    created_at.isoformat(),
                ))
                imported += 1

                # Insert in batches of 100
                if len(batch) >= 100:
                    if not dry_run:
                        await db.executemany(
                            """
                            INSERT INTO knowledge (
                                id, question_text, answer_text, vendor_name,
                                source_type, session_id, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                            batch,
                        )
                        await db.commit()
                    batch = []

            # Insert remaining items
            if batch and not dry_run:
                await db.executemany(
                    """
                    INSERT INTO knowledge (
                        id, question_text, answer_text, vendor_name,
                        source_type, session_id, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    batch,
                )
                await db.commit()

    return imported, skipped, errors


async def get_knowledge_count() -> int:
    """Get total count of knowledge items."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM knowledge")
        row = await cursor.fetchone()
        return row[0] if row else 0


def print_usage():
    """Print usage information."""
    print(__doc__)
    print("Options:")
    print("  --dry-run    Validate CSV without importing")
    print("  --help       Show this help message")


async def main():
    """Main entry point."""
    args = sys.argv[1:]

    # Parse arguments
    if not args or "--help" in args:
        print_usage()
        sys.exit(0)

    dry_run = "--dry-run" in args
    csv_files = [arg for arg in args if not arg.startswith("--")]

    if not csv_files:
        print("Error: No CSV file specified")
        print_usage()
        sys.exit(1)

    csv_path = Path(csv_files[0])

    print(f"{'[DRY RUN] ' if dry_run else ''}Importing from: {csv_path}")
    print("-" * 50)

    # Validate CSV
    print("Validating CSV structure...")
    valid, errors = validate_csv(csv_path)

    if not valid:
        print("Validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("Validation passed")

    # Get current count
    if DATABASE_PATH.exists():
        before_count = await get_knowledge_count()
        print(f"Current knowledge items: {before_count}")
    else:
        before_count = 0
        print("Database will be created")

    # Import
    print(f"\n{'Validating' if dry_run else 'Importing'} data...")
    imported, skipped, import_errors = await import_csv(csv_path, dry_run=dry_run)

    # Print results
    print("-" * 50)
    print(f"{'Would import' if dry_run else 'Imported'}: {imported} items")
    print(f"Skipped: {skipped} items")

    if import_errors:
        print(f"\nWarnings/Errors ({len(import_errors)}):")
        for error in import_errors[:10]:  # Show first 10
            print(f"  - {error}")
        if len(import_errors) > 10:
            print(f"  ... and {len(import_errors) - 10} more")

    if not dry_run and DATABASE_PATH.exists():
        after_count = await get_knowledge_count()
        print(f"\nTotal knowledge items: {after_count}")

    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
