#!/bin/bash
#
# Security Check Assistant - Backup Script
#
# Usage:
#   ./scripts/backup.sh
#
# Environment variables:
#   BACKUP_DIR - Backup destination (default: ./data/backups)
#   DATA_DIR - Data directory (default: ./data)
#   RETENTION_DAYS - Days to keep backups (default: 30)
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

BACKUP_DIR="${BACKUP_DIR:-$PROJECT_DIR/data/backups}"
DATA_DIR="${DATA_DIR:-$PROJECT_DIR/data}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "====================================="
echo "Security Check Assistant - Backup"
echo "====================================="
echo "Timestamp: $TIMESTAMP"
echo "Backup directory: $BACKUP_DIR"
echo "Data directory: $DATA_DIR"
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup SQLite database
if [ -f "$DATA_DIR/knowledge.db" ]; then
    echo "Backing up database..."
    cp "$DATA_DIR/knowledge.db" "$BACKUP_DIR/knowledge_$TIMESTAMP.db"
    echo "  Created: knowledge_$TIMESTAMP.db"
else
    echo "Warning: Database file not found at $DATA_DIR/knowledge.db"
fi

# Backup documents directory
if [ -d "$DATA_DIR/documents" ] && [ "$(ls -A "$DATA_DIR/documents" 2>/dev/null)" ]; then
    echo "Backing up documents..."
    tar -czf "$BACKUP_DIR/documents_$TIMESTAMP.tar.gz" -C "$DATA_DIR" documents/
    echo "  Created: documents_$TIMESTAMP.tar.gz"
else
    echo "Skipping documents backup (directory empty or not found)"
fi

# Remove old backups
echo ""
echo "Cleaning up old backups (older than $RETENTION_DAYS days)..."
DELETED_COUNT=$(find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete -print 2>/dev/null | wc -l)
echo "  Deleted: $DELETED_COUNT files"

# Show backup summary
echo ""
echo "====================================="
echo "Backup Summary"
echo "====================================="
echo "Location: $BACKUP_DIR"
echo "Files:"
ls -lh "$BACKUP_DIR"/*.db "$BACKUP_DIR"/*.tar.gz 2>/dev/null | tail -5 || echo "  (no backup files)"
echo ""
echo "Total backup size:"
du -sh "$BACKUP_DIR" 2>/dev/null || echo "  (could not calculate)"
echo ""
echo "Backup completed: $(date)"
