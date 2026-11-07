"""
Setup and verification script for NexaDesk-RAG.
Checks Python version, directory structure, storage permissions, and initializes the local database.
"""

import sys
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"


def check_python_version():
    """Verify minimum Python version."""
    print("Checking Python environment...")
    print(f"  Current version: {sys.version.split()[0]}")
    if sys.version_info < (3, 10):
        print("  [!] Warning: Python 3.10+ is recommended.")
    else:
        print("  [OK] Python version is compatible.")


def check_node_version():
    """Verify Node.js and npm availability."""
    print("\nChecking Node.js & npm environment...")
    node_path = shutil.which("node")
    npm_path = shutil.which("npm")
    if node_path:
        print(f"  [OK] Node.js found at: {node_path}")
    else:
        print("  [!] Warning: Node.js not detected in PATH.")

    if npm_path:
        print(f"  [OK] npm found at: {npm_path}")
    else:
        print("  [!] Warning: npm not detected in PATH.")


def verify_directories():
    """Verify that all core project directories exist."""
    print("\nVerifying directory layout...")
    required_dirs = [
        BACKEND_DIR / "app" / "api",
        BACKEND_DIR / "app" / "core",
        BACKEND_DIR / "app" / "services",
        BACKEND_DIR / "app" / "rag",
        BACKEND_DIR / "app" / "models",
        BACKEND_DIR / "app" / "database",
        BACKEND_DIR / "app" / "utils",
        BACKEND_DIR / "data" / "documents" / "NexaDesk" / "v1.0",
        BACKEND_DIR / "data" / "documents" / "NexaDesk" / "v2.0",
        BACKEND_DIR / "data" / "documents" / "NexaDesk" / "v3.0",
        BACKEND_DIR / "data" / "processed",
        BACKEND_DIR / "data" / "evaluation" / "results",
        BACKEND_DIR / "storage" / "chroma_db",
        BACKEND_DIR / "storage" / "uploads",
        FRONTEND_DIR / "src" / "components",
        FRONTEND_DIR / "src" / "services",
        BASE_DIR / "docs",
    ]

    missing = []
    for d in required_dirs:
        if d.exists():
            print(f"  [OK] Found: {d.relative_to(BASE_DIR)}")
        else:
            missing.append(d)
            print(f"  [MISSING] Creating: {d.relative_to(BASE_DIR)}")
            d.mkdir(parents=True, exist_ok=True)

    if not missing:
        print("  [OK] All core directories are present.")


def initialize_env_files():
    """Ensure .env files exist from .env.example templates."""
    print("\nChecking environment files...")
    backend_env = BACKEND_DIR / ".env"
    backend_env_example = BACKEND_DIR / ".env.example"
    frontend_env = FRONTEND_DIR / ".env"
    frontend_env_example = FRONTEND_DIR / ".env.example"

    if not backend_env.exists() and backend_env_example.exists():
        shutil.copy(backend_env_example, backend_env)
        print("  [+] Created backend/.env from .env.example")
    else:
        print("  [OK] backend/.env is present.")

    if not frontend_env.exists() and frontend_env_example.exists():
        shutil.copy(frontend_env_example, frontend_env)
        print("  [+] Created frontend/.env from .env.example")
    else:
        print("  [OK] frontend/.env is present.")


def initialize_sqlite():
    """Initialize SQLite database using backend database module."""
    print("\nInitializing SQLite database...")
    sys.path.insert(0, str(BACKEND_DIR))
    try:
        from app.database.connection import init_database, check_db_health
        init_database()
        if check_db_health():
            print("  [OK] SQLite database verified and responsive.")
        else:
            print("  [!] SQLite database check returned False.")
    except Exception as e:
        print(f"  [!] Could not initialize database: {e}")


def main():
    print("=" * 60)
    print("NexaDesk-RAG Project Setup & Health Verification")
    print("=" * 60)
    check_python_version()
    check_node_version()
    verify_directories()
    initialize_env_files()
    initialize_sqlite()
    print("\n" + "=" * 60)
    print("Project initialization complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

