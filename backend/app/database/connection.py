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
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()

            # 1. System metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 2. Enquiry logs table (For Phase 3 RAG logging)
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

            # 3. Documents table (Phase 2 Ingestion)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    document_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    product_version TEXT NOT NULL,
                    category TEXT NOT NULL,
                    document_type TEXT NOT NULL,
                    chunk_count INTEGER DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'completed',
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 4. Document chunks table (Phase 2 Ingestion & Chunk Storage)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    text_content TEXT NOT NULL,
                    char_count INTEGER NOT NULL,
                    section_title TEXT,
                    page_number INTEGER DEFAULT 1,
                    metadata_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
                )
            """)

            # 5. Conversation messages table (Phase 5 Multi-turn conversation history)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    product_version TEXT NOT NULL,
                    rewritten_query TEXT,
                    citations_json TEXT,
                    abstained INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create performance indices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_docs_version ON documents (product_version)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_docs_hash ON documents (file_hash)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_docs_name_ver ON documents (product_name, product_version, document_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON document_chunks (document_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conv_msg_id ON conversation_messages (conversation_id)")

            # Seed initialization record
            cursor.execute("""
                INSERT OR REPLACE INTO system_metadata (key, value)
                VALUES ('phase_status', 'Phase 2: Document Ingestion and Processing Active')
            """)
            conn.commit()
            logger.info(f"SQLite database initialized with document tables at: {db_path}")
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
