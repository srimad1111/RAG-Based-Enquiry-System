import os
from pathlib import Path
from typing import Dict, List
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


def ensure_directory_exists(directory_path: Path) -> Path:
    """Ensure that a directory exists, creating it if necessary."""
    try:
        directory_path.mkdir(parents=True, exist_ok=True)
        return directory_path
    except Exception as e:
        logger.error(f"Error ensuring directory {directory_path}: {e}")
        raise


def verify_storage_directories() -> Dict[str, bool]:
    """
    Verify and initialize all critical storage directories required
    for ChromaDB, uploads, processed files, and document versions.
    """
    dirs_to_check = {
        "chroma_db": settings.chroma_path,
        "uploads": settings.uploads_path,
        "documents": settings.documents_path,
        "sqlite_dir": settings.sqlite_path.parent,
    }

    results: Dict[str, bool] = {}
    for name, path in dirs_to_check.items():
        try:
            ensure_directory_exists(path)
            # Check write permission
            test_file = path / ".write_test"
            test_file.touch(exist_ok=True)
            test_file.unlink(missing_ok=True)
            results[name] = True
        except Exception as e:
            logger.warning(f"Storage directory verification warning for {name} ({path}): {e}")
            results[name] = False

    return results


def is_valid_version(version: str, supported_versions: List[str]) -> bool:
    """Check if the requested product version is valid and supported."""
    return version.strip().lower() in [v.lower() for v in supported_versions]

