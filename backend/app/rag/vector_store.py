from pathlib import Path
from typing import Dict, Any
from app.core.config import get_settings
from app.core.logging import logger
from app.utils.helpers import ensure_directory_exists

settings = get_settings()


class ChromaStorageManager:
    """
    Manages local ChromaDB storage directory and configuration.
    Ensures persistent local storage paths are ready for future ChromaDB indexing in Phase 2.
    """

    def __init__(self, persist_directory: Path = None):
        self.persist_directory = persist_directory or settings.chroma_path
        ensure_directory_exists(self.persist_directory)

    def check_status(self) -> Dict[str, Any]:
        """Check the status of persistent vector storage directory."""
        exists = self.persist_directory.exists()
        is_dir = self.persist_directory.is_dir()
        can_write = False

        if exists and is_dir:
            test_file = self.persist_directory / ".health_test"
            try:
                test_file.touch(exist_ok=True)
                test_file.unlink(missing_ok=True)
                can_write = True
            except Exception as e:
                logger.error(f"Cannot write to ChromaDB persist directory: {e}")
                can_write = False

        return {
            "status": "ready" if (exists and can_write) else "error",
            "persist_directory": str(self.persist_directory),
            "directory_exists": exists,
            "writable": can_write,
            "note": "Ready for Phase 2 document indexing & vector collections."
        }


chroma_storage_manager = ChromaStorageManager()

