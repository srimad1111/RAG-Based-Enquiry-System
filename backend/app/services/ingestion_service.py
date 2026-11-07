import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from app.core.config import get_settings
from app.core.logging import logger
from app.database.connection import get_sqlite_path
from app.models.schemas import (
    ChunkDetail,
    ChunkMetadata,
    DocumentRecord,
    DocumentUploadResponse,
    IngestionStatsResponse,
)
from app.services.chunking_service import chunking_service
from app.services.parser_service import parser_service
from app.utils.helpers import ensure_directory_exists

settings = get_settings()


class IngestionService:
    """
    Orchestrates the entire document ingestion workflow:
    validation -> deduplication -> parsing -> chunking -> SQLite storage -> JSON export.
    """

    def __init__(self):
        from app.database.connection import init_database
        init_database()
        self.db_path = get_sqlite_path()
        self.uploads_dir = settings.uploads_path
        self.processed_dir = settings.processed_path
        ensure_directory_exists(self.uploads_dir)
        ensure_directory_exists(self.processed_dir)

    @staticmethod
    def compute_sha256(file_bytes: bytes) -> str:
        """Compute SHA-256 hexadecimal hash for duplicate detection."""
        return hashlib.sha256(file_bytes).hexdigest()

    def find_duplicate(
        self,
        file_hash: str,
        document_name: str,
        product_name: str,
        product_version: str
    ) -> Optional[DocumentRecord]:
        """Check if an identical file hash or exact (product, version, name) exists."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # Check by hash OR by exact product + version + filename
            cursor.execute("""
                SELECT * FROM documents
                WHERE file_hash = ?
                   OR (product_name = ? AND product_version = ? AND document_name = ?)
                LIMIT 1
            """, (file_hash, product_name, product_version, document_name))
            row = cursor.fetchone()
            if row:
                return self._row_to_doc_record(row)
        return None

    def ingest_file(
        self,
        file_bytes: bytes,
        filename: str,
        product_name: str,
        product_version: str,
        category: str = "General",
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        replace_existing: bool = False
    ) -> DocumentUploadResponse:
        """
        Ingest a file from bytes (from HTTP upload or file read).
        Validates product version, handles deduplication, parses content,
        generates structured chunks, and persists records in SQLite.
        """
        # Validate version
        clean_version = product_version.strip()
        if clean_version not in settings.SUPPORTED_PRODUCT_VERSIONS:
            raise ValueError(
                f"Unsupported product version '{clean_version}'. "
                f"Must be one of: {settings.SUPPORTED_PRODUCT_VERSIONS}"
            )

        # Check extension
        ext = Path(filename).suffix.lower()
        if ext not in settings.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file format '{ext}'. Supported: {settings.SUPPORTED_EXTENSIONS}"
            )

        file_hash = self.compute_sha256(file_bytes)
        file_size = len(file_bytes)
        upload_time_iso = datetime.now(timezone.utc).isoformat()

        # Check for duplicates
        existing_doc = self.find_duplicate(file_hash, filename, product_name, clean_version)
        replaced = False

        if existing_doc:
            if not replace_existing:
                return DocumentUploadResponse(
                    success=False,
                    message=(
                        f"Duplicate document detected! '{filename}' already exists for {product_name} {clean_version} "
                        f"(Document ID: {existing_doc.id}). Set replace_existing=True to overwrite."
                    ),
                    document=existing_doc,
                    chunks_created=existing_doc.chunk_count,
                    duplicate_detected=True,
                    replaced_previous=False
                )
            else:
                logger.info(f"Replacing existing document {existing_doc.id} ('{filename}')")
                self.delete_document(existing_doc.id)
                replaced = True

        # Generate unique document ID
        doc_id = f"doc_{uuid.uuid4().hex[:12]}"

        # Save binary to storage/uploads/<version>/<doc_id>_<filename>
        target_version_dir = self.uploads_dir / clean_version
        ensure_directory_exists(target_version_dir)
        saved_file_path = target_version_dir / f"{doc_id}_{filename}"
        saved_file_path.write_bytes(file_bytes)

        # Parse document into structural content blocks
        try:
            blocks = parser_service.parse_document(saved_file_path)
            doc_type = ext.lstrip(".").lower()
            if doc_type in ("markdown",):
                doc_type = "md"

            # Generate chunks
            chunks = chunking_service.split_blocks(
                blocks=blocks,
                document_id=doc_id,
                document_name=filename,
                product_name=product_name,
                product_version=clean_version,
                category=category,
                document_type=doc_type,
                upload_timestamp=upload_time_iso,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )

            # Persist in SQLite
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                cursor = conn.cursor()

                # Insert document record
                cursor.execute("""
                    INSERT INTO documents (
                        id, document_name, file_path, file_hash, file_size,
                        product_name, product_version, category, document_type,
                        chunk_count, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    doc_id, filename, str(saved_file_path), file_hash, file_size,
                    product_name, clean_version, category, doc_type,
                    len(chunks), "completed", upload_time_iso, upload_time_iso
                ))

                # Insert chunks
                chunk_rows = [
                    (
                        c.id, c.document_id, c.chunk_index, c.text_content,
                        c.char_count, c.section_title, c.page_number,
                        c.metadata.model_dump_json(), upload_time_iso
                    )
                    for c in chunks
                ]
                cursor.executemany("""
                    INSERT INTO document_chunks (
                        id, document_id, chunk_index, text_content, char_count,
                        section_title, page_number, metadata_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, chunk_rows)

                conn.commit()

            # Export processed JSON for debugging and fast inspection
            processed_json_path = self.processed_dir / f"{doc_id}.json"
            processed_data = {
                "document_id": doc_id,
                "document_name": filename,
                "product_name": product_name,
                "product_version": clean_version,
                "category": category,
                "document_type": doc_type,
                "chunk_count": len(chunks),
                "chunks": [c.model_dump() for c in chunks]
            }
            processed_json_path.write_text(json.dumps(processed_data, indent=2), encoding="utf-8")

            doc_record = self.get_document(doc_id)
            return DocumentUploadResponse(
                success=True,
                message=f"Successfully ingested '{filename}' into {len(chunks)} structured chunks.",
                document=doc_record,
                chunks_created=len(chunks),
                duplicate_detected=False,
                replaced_previous=replaced
            )

        except Exception as e:
            logger.error(f"Failed to ingest document '{filename}': {e}", exc_info=True)
            # Remove uploaded file if ingestion failed
            if saved_file_path.exists():
                saved_file_path.unlink(missing_ok=True)
            raise

    def get_document(self, document_id: str) -> Optional[DocumentRecord]:
        """Retrieve single document record by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documents WHERE id = ?", (document_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_doc_record(row)
        return None

    def list_documents(
        self,
        product_version: Optional[str] = None,
        category: Optional[str] = None,
        document_type: Optional[str] = None
    ) -> List[DocumentRecord]:
        """List documents with optional filtering."""
        query = "SELECT * FROM documents WHERE 1=1"
        params: List[Any] = []

        if product_version:
            query += " AND product_version = ?"
            params.append(product_version)
        if category:
            query += " AND category = ?"
            params.append(category)
        if document_type:
            query += " AND document_type = ?"
            params.append(document_type.lower().lstrip("."))

        query += " ORDER BY created_at DESC"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_doc_record(r) for r in rows]

    def get_document_chunks(self, document_id: str) -> List[ChunkDetail]:
        """Retrieve all chunks for a document ordered by index."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM document_chunks
                WHERE document_id = ?
                ORDER BY chunk_index ASC
            """, (document_id,))
            rows = cursor.fetchall()

            chunks: List[ChunkDetail] = []
            for r in rows:
                meta_dict = json.loads(r["metadata_json"])
                chunks.append(ChunkDetail(
                    id=r["id"],
                    document_id=r["document_id"],
                    chunk_index=r["chunk_index"],
                    text_content=r["text_content"],
                    char_count=r["char_count"],
                    section_title=r["section_title"],
                    page_number=r["page_number"],
                    metadata=ChunkMetadata(**meta_dict)
                ))
            return chunks

    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document record, its chunks, the physical upload file,
        and processed JSON artifact.
        """
        doc = self.get_document(document_id)
        if not doc:
            return False

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
            conn.commit()

        # Delete physical file from uploads
        file_path = Path(doc.file_path)
        if file_path.exists():
            file_path.unlink(missing_ok=True)

        # Delete processed JSON artifact
        json_path = self.processed_dir / f"{document_id}.json"
        if json_path.exists():
            json_path.unlink(missing_ok=True)

        logger.info(f"Deleted document {document_id} ('{doc.document_name}') and associated chunks.")
        return True

    def get_stats(self) -> IngestionStatsResponse:
        """Calculate aggregate counts across versions, types, and categories."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Total docs & chunks
            cursor.execute("SELECT COUNT(*), COALESCE(SUM(chunk_count), 0) FROM documents")
            total_docs, total_chunks = cursor.fetchone()

            # By version
            by_version: Dict[str, Dict[str, int]] = {}
            for ver in settings.SUPPORTED_PRODUCT_VERSIONS:
                cursor.execute("""
                    SELECT COUNT(*), COALESCE(SUM(chunk_count), 0)
                    FROM documents WHERE product_version = ?
                """, (ver,))
                docs_cnt, chunks_cnt = cursor.fetchone()
                by_version[ver] = {"documents": docs_cnt, "chunks": chunks_cnt}

            # By type
            by_type: Dict[str, int] = {}
            cursor.execute("SELECT document_type, COUNT(*) FROM documents GROUP BY document_type")
            for t_name, t_cnt in cursor.fetchall():
                by_type[t_name] = t_cnt

            # By category
            by_category: Dict[str, int] = {}
            cursor.execute("SELECT category, COUNT(*) FROM documents GROUP BY category")
            for c_name, c_cnt in cursor.fetchall():
                by_category[c_name] = c_cnt

            return IngestionStatsResponse(
                total_documents=total_docs,
                total_chunks=total_chunks,
                by_version=by_version,
                by_type=by_type,
                by_category=by_category
            )

    @staticmethod
    def _row_to_doc_record(row: sqlite3.Row) -> DocumentRecord:
        return DocumentRecord(
            id=row["id"],
            document_name=row["document_name"],
            file_path=row["file_path"],
            file_size=row["file_size"],
            file_hash=row["file_hash"],
            product_name=row["product_name"],
            product_version=row["product_version"],
            category=row["category"],
            document_type=row["document_type"],
            chunk_count=row["chunk_count"],
            status=row["status"],
            error_message=row["error_message"] if "error_message" in row.keys() else None,
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"])
        )


ingestion_service = IngestionService()
