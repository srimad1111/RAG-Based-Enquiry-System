import sqlite3
from pathlib import Path
from typing import Optional
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


def get_sqlite_path() -> Path:
    """Ensure the database directory exists and return database path."""
    db_path = settings.sqlite_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def init_database() -> None:
    """Initialize SQLite database schema and tables if they don't exist."""
    db_path = get_sqlite_path()
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            # Table for recording system initialization and metadata
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Table for future enquiry logging (Phase 2 & Phase 3)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS enquiry_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_query TEXT NOT NULL,
                    product_version TEXT NOT NULL,
                    response_text TEXT,
                    sources TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Seed initialization record if not exists
            cursor.execute("""
                INSERT OR IGNORE INTO system_metadata (key, value)
                VALUES ('initialized_phase', 'Phase 1: Project Setup & Foundation')
            """)
            conn.commit()
            logger.info(f"SQLite database initialized at: {db_path}")
    except Exception as e:
        logger.error(f"Failed to initialize SQLite database: {e}", exc_info=True)
        raise


def check_db_health() -> bool:
    """Verify SQLite database connectivity and readability."""
    db_path = get_sqlite_path()
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            return cursor.fetchone() == (1,)
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

